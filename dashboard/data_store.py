"""
SYNERGY Dashboard — Central Data Store
=======================================

A single, thread-safe, in-memory store that holds **all** dashboard state.

DESIGN DECISIONS
----------------
1.  **One store, one lock.**  Every public method acquires ``self._lock``
    (a ``threading.Lock``) before touching internal collections.  This is
    sufficient for the Flask dev-server (which is threaded) and for the
    background simulator thread that pushes updates.

2.  **Bounded event history.**  ``max_events`` (default 1000) caps the
    deque so memory cannot grow indefinitely during a long demo.

3.  **Latest-wins for robot state / intent / network.**  The store keeps
    only the most recent snapshot per robot, not a time-series.  Historical
    data lives in the event log and in CSV experiment files.

4.  **No coordination logic.**  The store never decides which robot wins a
    conflict, whether a reservation should be granted, or which robot gets
    a task.  It only *records* what an adapter tells it.

5.  **Staleness detection.**  ``get_robot_state()`` and the bulk accessor
    accept a ``stale_threshold_s`` parameter.  If a robot's last update is
    older than that, the returned dict includes ``"_stale": True`` so the
    frontend can dim the card or show a warning.

PUBLIC API SUMMARY
------------------
Robots:
    update_robot(state: RobotState)
    get_robot_state(robot_id) -> dict | None
    get_all_robots() -> dict

Intents:
    update_intent(intent: RobotIntent)
    clear_intent(robot_id)
    get_intents() -> list[dict]

Reservations:
    update_reservation(reservation: Reservation)
    release_reservation(resource_id)
    get_reservations() -> list[dict]

Tasks:
    update_task(task: Task)
    get_tasks() -> list[dict]
    get_task(task_id) -> dict | None

Events:
    add_event(event: Event)
    get_events(limit, event_type, robot_id) -> list[dict]
    clear_events()

Network:
    update_network(status: NetworkStatus)
    get_network() -> dict

Metrics:
    update_metrics(metrics: ExperimentMetrics)
    get_metrics() -> dict | None
    add_experiment_run(metrics: ExperimentMetrics)
    get_experiment_runs() -> list[dict]

Housekeeping:
    reset()
    get_summary() -> dict          (health / overview)
"""

from __future__ import annotations

import threading
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Task,
    Event,
    NetworkStatus,
    ExperimentMetrics,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seconds_since(iso_timestamp: str) -> float:
    """Return elapsed seconds between *iso_timestamp* and now (UTC).

    Returns ``float('inf')`` if the timestamp cannot be parsed, so the
    caller treats it as stale rather than crashing.
    """
    try:
        then = datetime.fromisoformat(iso_timestamp)
        # Ensure timezone-aware comparison
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - then).total_seconds()
    except (ValueError, TypeError):
        return float("inf")


class DataStore:
    """Thread-safe, in-memory dashboard state container.

    Parameters
    ----------
    max_events : int
        Maximum number of events kept in the rolling history.
        Oldest events are discarded when the limit is reached.
    max_experiment_runs : int
        Maximum number of experiment result snapshots kept.
    """

    def __init__(
        self,
        max_events: int = 1000,
        max_experiment_runs: int = 200,
    ):
        self._lock = threading.Lock()
        self._max_events = max_events
        self._max_experiment_runs = max_experiment_runs

        # ── internal collections ──
        # Keyed by robot_id → RobotState
        self._robots: dict[str, RobotState] = {}
        # Keyed by robot_id → RobotIntent (latest intent per robot)
        self._intents: dict[str, RobotIntent] = {}
        # Keyed by resource_id → Reservation
        self._reservations: dict[str, Reservation] = {}
        # Keyed by task_id → Task
        self._tasks: dict[str, Task] = {}
        # Chronological, bounded
        self._events: deque[Event] = deque(maxlen=max_events)
        # Latest network snapshot
        self._network: NetworkStatus = NetworkStatus()
        # Current / live experiment metrics
        self._current_metrics: Optional[ExperimentMetrics] = None
        # Historical experiment runs
        self._experiment_runs: deque[ExperimentMetrics] = deque(
            maxlen=max_experiment_runs
        )
        # Timestamp of last store mutation (any kind)
        self._last_update: str = _now_iso()

    # ─────────────────────────────────────────────────────────────────────
    # Robots
    # ─────────────────────────────────────────────────────────────────────

    def update_robot(self, state: RobotState) -> None:
        """Insert or replace the latest state for a robot."""
        with self._lock:
            self._robots[state.robot_id] = state
            self._last_update = _now_iso()

    def get_robot_state(
        self, robot_id: str, stale_threshold_s: float = 10.0
    ) -> Optional[dict]:
        """Return a single robot's state dict, or ``None`` if unknown.

        A ``"_stale": True`` key is injected when the robot's last update
        is older than *stale_threshold_s* seconds.
        """
        with self._lock:
            rs = self._robots.get(robot_id)
            if rs is None:
                return None
            d = rs.to_dict()
            d["_stale"] = _seconds_since(rs.timestamp) > stale_threshold_s
            return d

    def get_all_robots(self, stale_threshold_s: float = 10.0) -> dict:
        """Return ``{robot_id: state_dict, ...}`` for every known robot."""
        with self._lock:
            result = {}
            for rid, rs in self._robots.items():
                d = rs.to_dict()
                d["_stale"] = _seconds_since(rs.timestamp) > stale_threshold_s
                result[rid] = d
            return result

    # ─────────────────────────────────────────────────────────────────────
    # Intents
    # ─────────────────────────────────────────────────────────────────────

    def update_intent(self, intent: RobotIntent) -> None:
        """Record the latest intent for a robot."""
        with self._lock:
            self._intents[intent.robot_id] = intent
            self._last_update = _now_iso()

    def clear_intent(self, robot_id: str) -> None:
        """Remove a robot's intent (e.g. after it has entered the resource)."""
        with self._lock:
            self._intents.pop(robot_id, None)
            self._last_update = _now_iso()

    def get_intents(self) -> list[dict]:
        """Return all current intents as a list of dicts."""
        with self._lock:
            return [intent.to_dict() for intent in self._intents.values()]

    # ─────────────────────────────────────────────────────────────────────
    # Reservations
    # ─────────────────────────────────────────────────────────────────────

    def update_reservation(self, reservation: Reservation) -> None:
        """Insert or update a reservation for a resource."""
        with self._lock:
            self._reservations[reservation.resource_id] = reservation
            self._last_update = _now_iso()

    def release_reservation(self, resource_id: str) -> None:
        """Mark a resource as FREE (keeps the entry so the UI can show it)."""
        with self._lock:
            if resource_id in self._reservations:
                old = self._reservations[resource_id]
                self._reservations[resource_id] = Reservation(
                    resource_id=resource_id,
                    robot_id=None,
                    status="FREE",
                    start_time=old.start_time,
                    end_time=_now_iso(),
                )
            else:
                # Resource was never tracked — create a FREE entry
                self._reservations[resource_id] = Reservation(
                    resource_id=resource_id, status="FREE"
                )
            self._last_update = _now_iso()

    def get_reservations(self) -> list[dict]:
        """Return all tracked reservations as a list of dicts."""
        with self._lock:
            return [r.to_dict() for r in self._reservations.values()]

    # ─────────────────────────────────────────────────────────────────────
    # Tasks
    # ─────────────────────────────────────────────────────────────────────

    def update_task(self, task: Task) -> None:
        """Insert or update a task."""
        with self._lock:
            self._tasks[task.task_id] = task
            self._last_update = _now_iso()

    def get_tasks(self) -> list[dict]:
        """Return all tasks as a list of dicts."""
        with self._lock:
            return [t.to_dict() for t in self._tasks.values()]

    def get_task(self, task_id: str) -> Optional[dict]:
        """Return a single task dict, or ``None``."""
        with self._lock:
            t = self._tasks.get(task_id)
            return t.to_dict() if t else None

    # ─────────────────────────────────────────────────────────────────────
    # Events
    # ─────────────────────────────────────────────────────────────────────

    def add_event(self, event: Event) -> None:
        """Append an event to the bounded history."""
        with self._lock:
            self._events.append(event)
            self._last_update = _now_iso()

    def get_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        robot_id: Optional[str] = None,
    ) -> list[dict]:
        """Return recent events, newest first, with optional filtering.

        Parameters
        ----------
        limit : int
            Maximum number of events to return.
        event_type : str or None
            If given, only events matching this type are returned.
        robot_id : str or None
            If given, only events involving this robot (primary or related)
            are returned.
        """
        with self._lock:
            result: list[dict] = []
            # Iterate newest-first (reversed deque)
            for ev in reversed(self._events):
                if event_type and ev.event_type != event_type:
                    continue
                if robot_id and ev.robot_id != robot_id and ev.related_robot_id != robot_id:
                    continue
                result.append(ev.to_dict())
                if len(result) >= limit:
                    break
            return result

    def clear_events(self) -> None:
        """Remove all events (useful between experiment runs)."""
        with self._lock:
            self._events.clear()
            self._last_update = _now_iso()

    # ─────────────────────────────────────────────────────────────────────
    # Network
    # ─────────────────────────────────────────────────────────────────────

    def update_network(self, status: NetworkStatus) -> None:
        """Replace the current network status snapshot."""
        with self._lock:
            self._network = status
            self._last_update = _now_iso()

    def get_network(self) -> dict:
        """Return the current network status dict."""
        with self._lock:
            return self._network.to_dict()

    # ─────────────────────────────────────────────────────────────────────
    # Metrics / Experiments
    # ─────────────────────────────────────────────────────────────────────

    def update_metrics(self, metrics: ExperimentMetrics) -> None:
        """Set the *live* experiment metrics snapshot (displayed in real-time)."""
        with self._lock:
            self._current_metrics = metrics
            self._last_update = _now_iso()

    def get_metrics(self) -> Optional[dict]:
        """Return current live metrics dict, or ``None``."""
        with self._lock:
            return self._current_metrics.to_dict() if self._current_metrics else None

    def add_experiment_run(self, metrics: ExperimentMetrics) -> None:
        """Archive a completed experiment run for later comparison."""
        with self._lock:
            self._experiment_runs.append(metrics)
            self._last_update = _now_iso()

    def get_experiment_runs(self) -> list[dict]:
        """Return all archived experiment runs as a list of dicts."""
        with self._lock:
            return [m.to_dict() for m in self._experiment_runs]

    # ─────────────────────────────────────────────────────────────────────
    # Housekeeping
    # ─────────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all state.  Useful between demo scenarios."""
        with self._lock:
            self._robots.clear()
            self._intents.clear()
            self._reservations.clear()
            self._tasks.clear()
            self._events.clear()
            self._network = NetworkStatus()
            self._current_metrics = None
            self._experiment_runs.clear()
            self._last_update = _now_iso()

    def get_summary(self) -> dict:
        """Return a lightweight health / overview dict for ``/api/health``."""
        with self._lock:
            return {
                "status": "ok",
                "robots_tracked": len(self._robots),
                "active_intents": len(self._intents),
                "active_reservations": sum(
                    1
                    for r in self._reservations.values()
                    if r.status == "ACTIVE"
                ),
                "total_reservations_tracked": len(self._reservations),
                "tasks_tracked": len(self._tasks),
                "events_stored": len(self._events),
                "max_events": self._max_events,
                "experiment_runs_stored": len(self._experiment_runs),
                "last_update": self._last_update,
            }
