"""
Task — a unit of work to be assigned to a robot.

Tasks are announced to the fleet. Each robot independently evaluates
eligibility and bids. The deterministic winner rule ensures all robots
agree on who gets the task.

DESIGN NOTES:
- `priority` is an integer 1–10 (not the computed priority score).
  This is the task's intrinsic importance level.
- `status` tracks the task lifecycle from announcement through completion.
- `assigned_robot` is None until a winner is selected.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto


class TaskType(Enum):
    """Type of warehouse task."""

    PICKUP = auto()  # Pick up payload from source
    DELIVERY = auto()  # Deliver payload to target
    PICKUP_AND_DELIVERY = auto()  # Full cycle: source -> target
    CHARGING = auto()  # Go to charging station
    INSPECTION = auto()  # Patrol / inspect area


class TaskStatus(Enum):
    """Lifecycle status of a task.

    Transitions:
        ANNOUNCED -> BIDDING (bid window open)
        BIDDING -> ASSIGNED (winner selected)
        ASSIGNED -> IN_PROGRESS (winner starts execution)
        IN_PROGRESS -> COMPLETED (success)
        IN_PROGRESS -> FAILED (robot couldn't complete)
        FAILED -> REASSIGNED (new winner selected)
        ASSIGNED -> FAILED (assigned robot failed before starting)
    """

    ANNOUNCED = auto()
    BIDDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    REASSIGNED = auto()


@dataclass
class Task:
    """A unit of work to be assigned to a robot in the fleet."""

    task_id: str
    task_type: TaskType = TaskType.PICKUP_AND_DELIVERY
    priority: int = 5  # 1 (lowest) to 10 (highest)
    deadline: float | None = None  # Unix epoch seconds, or None = no deadline
    payload_kg: float = 0.0
    source_location: str = ""  # Named location, e.g., "SHELF_A3"
    target_location: str = ""  # Named location, e.g., "PACKING_1"
    assigned_robot: str | None = None
    status: TaskStatus = TaskStatus.ANNOUNCED
    announced_at: float = field(default_factory=time.time)

    def is_assignable(self) -> bool:
        """Whether this task can be assigned (or reassigned) to a robot."""
        return self.status in (
            TaskStatus.ANNOUNCED,
            TaskStatus.BIDDING,
            TaskStatus.FAILED,
            TaskStatus.REASSIGNED,
        )

    def deadline_urgency(self, now: float | None = None) -> float:
        """How urgent is this task based on deadline proximity.

        Returns a value >= 0. Higher = more urgent.
        Returns 0.0 if there is no deadline.

        The formula: max(0, 1 / max(remaining_seconds, 1))
        This gives a smooth urgency curve that increases as the
        deadline approaches, without division by zero.
        """
        if self.deadline is None:
            return 0.0
        if now is None:
            now = time.time()
        remaining = self.deadline - now
        if remaining <= 0:
            return 1.0  # Past deadline — maximum urgency
        return 1.0 / max(remaining, 1.0)

    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id!r}, type={self.task_type.name}, "
            f"priority={self.priority}, status={self.status.name}, "
            f"assigned={self.assigned_robot!r})"
        )
