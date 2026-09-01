"""
SYNERGY Dashboard — Normalized Data Models
===========================================

These dataclasses define the **internal** data contract for the dashboard.
Every piece of telemetry — whether it comes from the mock simulator or from a
real ROS 2 adapter — is converted into one of these structures before it
reaches the data store, Flask API, or frontend.

KEY DESIGN DECISIONS
--------------------
1.  All fields that may be unavailable from a particular telemetry source are
    ``Optional`` with sensible defaults (``None``, ``"UNKNOWN"``, ``0``, etc.).
    This means the dashboard never crashes because a source omits a field.

2.  ``timestamp`` fields are ISO-8601 strings (``datetime.isoformat()``).
    Strings travel cleanly through JSON serialization without custom encoders.

3.  Status values (``RobotState.status``, ``Task.status``, …) are plain strings
    rather than Python ``Enum`` members.  External sources (ROS topics, mock
    scenarios) may use vocabularies we haven't seen yet, so the dashboard
    accepts any string and the frontend maps known values to colours/icons.

4.  There is **no coordination logic** here.  Models are passive containers.
    They do not decide priorities, grant reservations, or assign tasks.

5.  Every model has a ``to_dict()`` method so the Flask API can serialize it
    to JSON with a single call, and a ``from_dict()`` class-method so data
    can be reconstructed from JSON payloads or config files.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _generate_id() -> str:
    """Return a short unique ID suitable for run/event identifiers."""
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# RobotState
# ---------------------------------------------------------------------------

@dataclass
class RobotState:
    """Snapshot of a single robot's physical and logical state.

    Populated by the mock simulator or a ROS 2 adapter.  The dashboard
    uses this to draw the robot on the map, fill the status card, and
    detect staleness.

    Attributes
    ----------
    robot_id : str
        Short identifier, e.g. ``"A"``, ``"B"``, ``"C"``.
    x, y : float
        Position in the warehouse coordinate frame (metres).
    yaw : float
        Heading in radians.  0 = facing +X, π/2 = facing +Y.
    velocity : float
        Linear speed (m/s).  Negative values are unusual but allowed.
    battery : float
        Battery level as a percentage (0–100).
    status : str
        One of ``IDLE``, ``MOVING``, ``WAITING``, ``REROUTING``,
        ``FAILED``, ``CHARGING``, or any string the source provides.
    task_id : Optional[str]
        ID of the currently assigned task, or ``None`` if idle.
    timestamp : str
        ISO-8601 timestamp of when this state was produced / received.
    """

    robot_id: str
    x: float = 0.0
    y: float = 0.0
    yaw: float = 0.0
    velocity: float = 0.0
    battery: float = 100.0
    status: str = "IDLE"
    task_id: Optional[str] = None
    timestamp: str = field(default_factory=_now_iso)

    # -- Serialization helpers ------------------------------------------------

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RobotState":
        return cls(
            robot_id=data.get("robot_id", "UNKNOWN"),
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            yaw=float(data.get("yaw", 0.0)),
            velocity=float(data.get("velocity", 0.0)),
            battery=float(data.get("battery", 100.0)),
            status=data.get("status", "UNKNOWN"),
            task_id=data.get("task_id"),
            timestamp=data.get("timestamp", _now_iso()),
        )


# ---------------------------------------------------------------------------
# RobotIntent
# ---------------------------------------------------------------------------

@dataclass
class RobotIntent:
    """A robot's declared intention to use a shared resource.

    In the real SYNERGY system, intents are broadcast by Fleet Coordination
    Agents.  The dashboard merely *observes* them.

    Attributes
    ----------
    robot_id : str
        Which robot declared this intent.
    resource_id : str
        The intersection / shared resource the robot intends to enter,
        e.g. ``"I1"``.
    eta : Optional[float]
        Estimated seconds until the robot reaches the resource.
    timestamp : str
        When the intent was produced / received.
    """

    robot_id: str
    resource_id: str
    eta: Optional[float] = None
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RobotIntent":
        return cls(
            robot_id=data.get("robot_id", "UNKNOWN"),
            resource_id=data.get("resource_id", "UNKNOWN"),
            eta=data.get("eta"),
            timestamp=data.get("timestamp", _now_iso()),
        )


# ---------------------------------------------------------------------------
# Reservation
# ---------------------------------------------------------------------------

@dataclass
class Reservation:
    """An active or released reservation on a shared resource.

    The dashboard displays which intersections are currently held and by
    whom.  It does **not** grant or revoke reservations — that is the job
    of the Fleet Coordination Agents.

    Attributes
    ----------
    resource_id : str
        The intersection / resource, e.g. ``"I1"``.
    robot_id : Optional[str]
        The robot that holds the reservation, or ``None`` if the
        resource is free.
    status : str
        ``"ACTIVE"``, ``"FREE"``, ``"PENDING"``, or source vocabulary.
    start_time : Optional[str]
        ISO-8601 timestamp when the reservation began.
    end_time : Optional[str]
        ISO-8601 timestamp when the reservation ended / will end.
    """

    resource_id: str
    robot_id: Optional[str] = None
    status: str = "FREE"
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Reservation":
        return cls(
            resource_id=data.get("resource_id", "UNKNOWN"),
            robot_id=data.get("robot_id"),
            status=data.get("status", "FREE"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
        )


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A warehouse task (pick-up → drop-off) tracked by the dashboard.

    Attributes
    ----------
    task_id : str
        Unique identifier, e.g. ``"T01"``.
    pickup : str
        Named pickup location.
    dropoff : str
        Named drop-off / destination location.
    assigned_robot : Optional[str]
        Robot currently responsible, or ``None`` if unassigned.
    status : str
        ``"ANNOUNCED"``, ``"ASSIGNED"``, ``"IN_PROGRESS"``,
        ``"WAITING"``, ``"COMPLETED"``, ``"REASSIGNED"``, ``"FAILED"``.
    created_at : str
        ISO-8601 creation timestamp.
    completed_at : Optional[str]
        ISO-8601 completion timestamp, or ``None`` if still open.
    """

    task_id: str
    pickup: str = ""
    dropoff: str = ""
    assigned_robot: Optional[str] = None
    status: str = "ANNOUNCED"
    created_at: str = field(default_factory=_now_iso)
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            task_id=data.get("task_id", _generate_id()),
            pickup=data.get("pickup", ""),
            dropoff=data.get("dropoff", ""),
            assigned_robot=data.get("assigned_robot"),
            status=data.get("status", "ANNOUNCED"),
            created_at=data.get("created_at", _now_iso()),
            completed_at=data.get("completed_at"),
        )


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

@dataclass
class Event:
    """A single coordination / fleet event recorded by the dashboard.

    Events form the chronological log that is critical during live demos.

    Attributes
    ----------
    timestamp : str
        ISO-8601.
    event_type : str
        E.g. ``"CONFLICT"``, ``"WINNER"``, ``"RESERVATION"``, ``"WAIT"``,
        ``"RELEASE"``, ``"REROUTE"``, ``"OBSTACLE"``, ``"FAILURE"``,
        ``"REASSIGNMENT"``, ``"TASK_COMPLETED"``, ``"HEARTBEAT_TIMEOUT"``,
        ``"NETWORK_DEGRADED"``, ``"NETWORK_RECOVERED"``.
    robot_id : Optional[str]
        Primary robot involved.
    related_robot_id : Optional[str]
        Secondary robot (e.g. the loser in a conflict).
    resource_id : Optional[str]
        Intersection / resource, if applicable.
    task_id : Optional[str]
        Related task, if applicable.
    message : str
        Human-readable description for the event log UI.
    """

    timestamp: str = field(default_factory=_now_iso)
    event_type: str = "INFO"
    robot_id: Optional[str] = None
    related_robot_id: Optional[str] = None
    resource_id: Optional[str] = None
    task_id: Optional[str] = None
    message: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Event":
        return cls(
            timestamp=data.get("timestamp", _now_iso()),
            event_type=data.get("event_type", "INFO"),
            robot_id=data.get("robot_id"),
            related_robot_id=data.get("related_robot_id"),
            resource_id=data.get("resource_id"),
            task_id=data.get("task_id"),
            message=data.get("message", ""),
        )


# ---------------------------------------------------------------------------
# NetworkStatus
# ---------------------------------------------------------------------------

@dataclass
class NetworkStatus:
    """Snapshot of the inter-robot communication network health.

    If the real prototype does not implement network-degradation simulation,
    these values will be populated by the mock adapter and clearly labelled
    as simulated in the UI.

    Attributes
    ----------
    status : str
        ``"NORMAL"``, ``"DEGRADED"``, ``"DISCONNECTED"``.
    latency_ms : Optional[float]
        Simulated or measured round-trip latency.
    packet_loss_percent : Optional[float]
        Simulated or measured packet loss (0–100).
    active_peers : Optional[int]
        Number of robots / agents currently reachable.
    timestamp : str
        ISO-8601.
    """

    status: str = "NORMAL"
    latency_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    active_peers: Optional[int] = None
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkStatus":
        return cls(
            status=data.get("status", "NORMAL"),
            latency_ms=data.get("latency_ms"),
            packet_loss_percent=data.get("packet_loss_percent"),
            active_peers=data.get("active_peers"),
            timestamp=data.get("timestamp", _now_iso()),
        )


# ---------------------------------------------------------------------------
# ExperimentMetrics
# ---------------------------------------------------------------------------

@dataclass
class ExperimentMetrics:
    """Metrics for a single experiment run (baseline or proposed).

    These are the numbers the evaluation section of the dashboard displays.
    The dashboard **never fabricates** a positive improvement — it calculates
    it from actual measured data.

    Attributes
    ----------
    run_id : str
        Unique identifier for this run.
    mode : str
        ``"baseline"`` (stop-and-wait) or ``"proposed"`` (decentralized).
    total_task_time : float
        Wall-clock seconds for all tasks in this run.
    average_wait_time : float
        Mean waiting time across all robots in this run.
    tasks_completed : int
        Number of tasks finished.
    collision_count : int
        Number of collisions detected (should be 0 in a correct system).
    scenario : str
        Which scenario produced this run (e.g. ``"conflict"``).
    timestamp : str
        ISO-8601 when the run concluded.
    notes : str
        Free-form notes attached by the operator.
    """

    run_id: str = field(default_factory=_generate_id)
    mode: str = "proposed"
    total_task_time: float = 0.0
    average_wait_time: float = 0.0
    tasks_completed: int = 0
    collision_count: int = 0
    scenario: str = ""
    timestamp: str = field(default_factory=_now_iso)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ExperimentMetrics":
        return cls(
            run_id=data.get("run_id", _generate_id()),
            mode=data.get("mode", "proposed"),
            total_task_time=float(data.get("total_task_time", 0.0)),
            average_wait_time=float(data.get("average_wait_time", 0.0)),
            tasks_completed=int(data.get("tasks_completed", 0)),
            collision_count=int(data.get("collision_count", 0)),
            scenario=data.get("scenario", ""),
            timestamp=data.get("timestamp", _now_iso()),
            notes=data.get("notes", ""),
        )
