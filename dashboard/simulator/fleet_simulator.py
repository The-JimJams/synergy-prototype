"""
SYNERGY Dashboard — Fleet Simulator
====================================

The FleetSimulator runs scenario steps in a background thread and pushes
normalized telemetry objects into the central DataStore.

Key features:
1. Thread-safe execution using a background worker thread.
2. Configurable playback speed multiplier (`speed_multiplier`).
3. Optional looping mode (`loop=True`).
4. Dispatches action dictionaries to DataStore methods cleanly.
5. Injects fresh ISO-8601 timestamps into created models.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Union, List, Dict, Any

from data_store import DataStore
from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Task,
    Event,
    NetworkStatus,
    ExperimentMetrics,
)
from simulator.scenarios import get_scenario

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FleetSimulator:
    """Replays mock telemetry scenarios into a DataStore instance."""

    def __init__(
        self,
        data_store: DataStore,
        speed_multiplier: float = 1.0,
        loop: bool = True,
    ):
        self.data_store = data_store
        self.speed_multiplier = max(0.1, speed_multiplier)
        self.loop = loop

        self._scenario_name: str = "full_demo"
        self._steps: List[Dict[str, Any]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_step_index: int = 0
        self._is_running: bool = False

        # Pre-load default scenario
        self.load_scenario(self._scenario_name)

    def load_scenario(self, scenario_input: Union[str, List[Dict[str, Any]]]) -> None:
        """Load a scenario by name or by passing a step list directly."""
        if self._is_running:
            self.stop()

        if isinstance(scenario_input, str):
            self._scenario_name = scenario_input
            self._steps = get_scenario(scenario_input)
        else:
            self._scenario_name = "custom"
            self._steps = scenario_input

        self._current_step_index = 0

    def start(self) -> None:
        """Start background simulation thread."""
        if self._is_running:
            return

        self._stop_event.clear()
        self._is_running = True
        self._thread = threading.Thread(
            target=self._run_loop, name="FleetSimulatorThread", daemon=True
        )
        self._thread.start()
        logger.info(f"FleetSimulator started scenario '{self._scenario_name}'")

    def stop(self) -> None:
        """Signal simulator thread to stop and wait for termination."""
        if not self._is_running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._is_running = False
        logger.info("FleetSimulator stopped")

    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """Return status information for telemetry inspection."""
        return {
            "running": self._is_running,
            "scenario": self._scenario_name,
            "current_step": self._current_step_index,
            "total_steps": len(self._steps),
            "speed_multiplier": self.speed_multiplier,
            "loop": self.loop,
        }

    def _run_loop(self) -> None:
        """Main loop executed in background thread."""
        try:
            while not self._stop_event.is_set():
                for idx, step in enumerate(self._steps):
                    if self._stop_event.is_set():
                        break

                    self._current_step_index = idx
                    delay = step.get("delay", 0.0)

                    if delay > 0:
                        scaled_delay = delay / self.speed_multiplier
                        # Sleep in small increments to respond quickly to stop signal
                        sleep_chunks = int(scaled_delay / 0.05) + 1
                        for _ in range(sleep_chunks):
                            if self._stop_event.is_set():
                                break
                            time.sleep(0.05)

                    if self._stop_event.is_set():
                        break

                    # Dispatch step actions
                    actions = step.get("actions", [])
                    for action in actions:
                        self._dispatch_action(action)

                if not self.loop or self._stop_event.is_set():
                    break

        except Exception as e:
            logger.exception(f"Unhandled error in FleetSimulator loop: {e}")
        finally:
            self._is_running = False

    def _dispatch_action(self, action: Dict[str, Any]) -> None:
        """Dispatch a single action to the DataStore."""
        atype = action.get("type")
        data = dict(action.get("data", {}))

        if atype == "update_robot":
            rid = data.get("robot_id")
            # If robot is actively executing an assigned task, do not overwrite with static scenario positions
            active_tasks = self.data_store.get_tasks()
            if any(t.get("assigned_robot") == rid and t.get("status") == "IN_PROGRESS" for t in active_tasks):
                return

            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_robot(RobotState.from_dict(data))

        elif atype == "update_intent":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_intent(RobotIntent.from_dict(data))

        elif atype == "clear_intent":
            rid = data.get("robot_id")
            if rid:
                self.data_store.clear_intent(rid)

        elif atype == "update_reservation":
            if "start_time" not in data and data.get("status") == "ACTIVE":
                data["start_time"] = _now_iso()
            self.data_store.update_reservation(Reservation.from_dict(data))

        elif atype == "release_reservation":
            resource_id = data.get("resource_id")
            if resource_id:
                self.data_store.release_reservation(resource_id)

        elif atype == "update_task":
            if "created_at" not in data:
                data["created_at"] = _now_iso()
            if data.get("status") == "COMPLETED" and "completed_at" not in data:
                data["completed_at"] = _now_iso()
            self.data_store.update_task(Task.from_dict(data))

        elif atype == "add_event":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.add_event(Event.from_dict(data))

        elif atype == "update_network":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_network(NetworkStatus.from_dict(data))

        elif atype == "update_metrics":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_metrics(ExperimentMetrics.from_dict(data))

        else:
            logger.warning(f"Unknown simulator action type: '{atype}'")
