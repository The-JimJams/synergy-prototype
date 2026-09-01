"""
P5 Task Model
=============

Represents a single warehouse transport task within the P5 subsystem.

These are INTERNAL P5 fields.  A future adapter will translate external
task announcements (e.g. ROS 2 TaskAnnouncement messages) into this model.

Phase 1: Data foundation + explicit state enumeration.
Phase 6: State machine enforcement (allowed transitions).
"""

from __future__ import annotations

import enum
import dataclasses
from typing import Optional, Tuple, FrozenSet

# ---------------------------------------------------------------------------
# Task status enumeration
# ---------------------------------------------------------------------------

class TaskStatus(enum.Enum):
    """Lifecycle states of a task as seen by P5.

    State machine (to be enforced in Phase 6):

        AVAILABLE
            |
            v  (announce)
        ANNOUNCED
            |
            v  (bidding opens)
        BIDDING
            |
            v  (winner selected)
        ASSIGNED
            |
            v  (robot starts moving)
        IN_PROGRESS
            |
        +---+---+
        |       |
        v       v
    COMPLETED  FAILED
                |
                v  (recovery triggered)
            RECOVERY
                |
                v  (re-announced)
            ANNOUNCED  (loop)

        CANCELLED  <- can be reached from most states
    """

    AVAILABLE = "AVAILABLE"
    ANNOUNCED = "ANNOUNCED"
    BIDDING = "BIDDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RECOVERY = "RECOVERY"
    CANCELLED = "CANCELLED"


# Explicit allowed transitions (enforced in Phase 6).
# Stored here as reference data so documentation is co-located with the model.
TASK_TRANSITIONS: dict[TaskStatus, FrozenSet[TaskStatus]] = {
    TaskStatus.AVAILABLE:    frozenset({TaskStatus.ANNOUNCED, TaskStatus.CANCELLED}),
    TaskStatus.ANNOUNCED:    frozenset({TaskStatus.BIDDING, TaskStatus.CANCELLED}),
    TaskStatus.BIDDING:      frozenset({TaskStatus.ASSIGNED, TaskStatus.AVAILABLE, TaskStatus.CANCELLED}),
    TaskStatus.ASSIGNED:     frozenset({TaskStatus.IN_PROGRESS, TaskStatus.RECOVERY, TaskStatus.CANCELLED}),
    TaskStatus.IN_PROGRESS:  frozenset({TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}),
    TaskStatus.COMPLETED:    frozenset(),   # terminal
    TaskStatus.FAILED:       frozenset({TaskStatus.RECOVERY, TaskStatus.CANCELLED}),
    TaskStatus.RECOVERY:     frozenset({TaskStatus.ANNOUNCED, TaskStatus.CANCELLED}),
    TaskStatus.CANCELLED:    frozenset(),   # terminal
}


# ---------------------------------------------------------------------------
# Task dataclass
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Task:
    """Internal P5 representation of a single warehouse transport task.

    Attributes
    ----------
    task_id : str
        Unique identifier (e.g. "T01").
    pickup_location : Tuple[float, float]
        (x, y) warehouse coordinates for item pick-up.
    dropoff_location : Tuple[float, float]
        (x, y) warehouse coordinates for item drop-off.
    priority : int
        Task urgency [1 – 10]. Higher = more urgent.
    deadline : float
        Maximum allowed completion time in seconds from task creation.
    required_payload : float
        Minimum payload capacity required (same units as Robot.payload_capacity).
    status : TaskStatus
        Current lifecycle state.
    assigned_robot : Optional[str]
        robot_id of the robot that won the bid, or None.
    required_capabilities : Tuple[str, ...]
        Capability tags that a robot must possess (Phase 3).

    Example
    -------
    >>> t = Task(
    ...     task_id="T01",
    ...     pickup_location=(10.0, 4.0),
    ...     dropoff_location=(18.0, 9.0),
    ...     priority=7,
    ...     deadline=60.0,
    ...     required_payload=100.0,
    ...     status=TaskStatus.AVAILABLE,
    ...     assigned_robot=None,
    ...     required_capabilities=("CARRY",),
    ... )
    """

    task_id: str
    pickup_location: Tuple[float, float]
    dropoff_location: Tuple[float, float]
    priority: int
    deadline: float
    required_payload: float
    status: TaskStatus
    assigned_robot: Optional[str]
    required_capabilities: Tuple[str, ...]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def transport_distance(self) -> float:
        """Euclidean distance from pickup to dropoff."""
        dx = self.pickup_location[0] - self.dropoff_location[0]
        dy = self.pickup_location[1] - self.dropoff_location[1]
        return (dx * dx + dy * dy) ** 0.5

    def is_terminal(self) -> bool:
        """Return True if the task has reached a terminal state."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.CANCELLED)

    def needs_recovery(self) -> bool:
        """Return True if this task requires failure recovery."""
        return self.status in (TaskStatus.FAILED, TaskStatus.RECOVERY)

    def allowed_transitions(self) -> FrozenSet[TaskStatus]:
        """Return the set of states this task may transition to next."""
        return TASK_TRANSITIONS.get(self.status, frozenset())

    def __str__(self) -> str:
        return (
            f"Task({self.task_id!r}, "
            f"pickup={self.pickup_location}, "
            f"dropoff={self.dropoff_location}, "
            f"priority={self.priority}, "
            f"status={self.status.value}, "
            f"robot={self.assigned_robot!r})"
        )
