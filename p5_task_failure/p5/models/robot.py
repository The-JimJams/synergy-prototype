"""
P5 Robot Model
==============

Represents a single robot's state within the P5 subsystem.

These are INTERNAL P5 fields.  They are not final ROS 2 message fields.
A future ROS 2 adapter will translate external RobotState messages into
this model without changing any P5 core logic.

Phase 1: Data foundation only.
Phase 2+: State transition logic will be added.
"""

from __future__ import annotations

import enum
import dataclasses
from typing import Optional, Tuple


class RobotStatus(enum.Enum):
    """Lifecycle status of a robot as seen by P5.

    Transitions (to be enforced in Phase 2+):
      AVAILABLE  -> BUSY      (task accepted)
      AVAILABLE  -> CHARGING  (battery low)
      BUSY       -> AVAILABLE (task completed)
      BUSY       -> FAILED    (heartbeat timeout)
      CHARGING   -> AVAILABLE (battery restored)
      FAILED     -> RECOVERED (reconnected)
      RECOVERED  -> AVAILABLE (ready again)
      any        -> OFFLINE   (graceful shutdown)
    """

    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    CHARGING = "CHARGING"
    OFFLINE = "OFFLINE"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"


@dataclasses.dataclass
class Robot:
    """Internal P5 representation of a single robot.

    Attributes
    ----------
    robot_id : str
        Unique identifier (e.g. "A", "robot_1").
    position : Tuple[float, float]
        Current (x, y) position in the warehouse coordinate frame.
    battery : float
        Battery level in percent [0.0 – 100.0].
    payload_capacity : float
        Maximum payload the robot can carry (kg or warehouse units).
    current_task : Optional[str]
        task_id of the task currently assigned, or None if idle.
    workload : int
        Number of tasks queued / in progress (0 when AVAILABLE).
    status : RobotStatus
        Current lifecycle status.
    capabilities : tuple[str, ...]
        Immutable set of capability tags (e.g. ("CARRY", "LIFT")).
        Used by the capability checker (Phase 3).

    Example
    -------
    >>> r = Robot(
    ...     robot_id="A",
    ...     position=(5.0, 3.0),
    ...     battery=85.0,
    ...     payload_capacity=500.0,
    ...     current_task=None,
    ...     workload=0,
    ...     status=RobotStatus.AVAILABLE,
    ...     capabilities=("CARRY",),
    ... )
    """

    robot_id: str
    position: Tuple[float, float]
    battery: float
    payload_capacity: float
    current_task: Optional[str]
    workload: int
    status: RobotStatus
    capabilities: Tuple[str, ...]

    # ------------------------------------------------------------------
    # Convenience helpers (pure reads — no side-effects)
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if the robot can accept a new task right now."""
        return self.status == RobotStatus.AVAILABLE and self.current_task is None

    def distance_to(self, target: Tuple[float, float]) -> float:
        """Euclidean distance from the robot's current position to *target*."""
        dx = self.position[0] - target[0]
        dy = self.position[1] - target[1]
        return (dx * dx + dy * dy) ** 0.5

    def has_capability(self, capability: str) -> bool:
        """Return True if the robot has the requested capability tag."""
        return capability in self.capabilities

    def can_carry(self, required_payload: float) -> bool:
        """Return True if the robot's payload capacity meets the requirement."""
        return self.payload_capacity >= required_payload

    def __str__(self) -> str:
        return (
            f"Robot({self.robot_id!r}, "
            f"pos={self.position}, "
            f"battery={self.battery:.0f}%, "
            f"status={self.status.value}, "
            f"task={self.current_task!r})"
        )
