"""
RobotState — snapshot of a robot's current physical and operational state.

This is the data a robot broadcasts to its peers. Every field here is
something that other robots need to know to make coordination decisions.

DESIGN NOTES:
- `timestamp` is when the state was GENERATED, not when it was RECEIVED.
  The receiver calculates freshness as: now() - state.timestamp
- `status` is an enum, not a string, to prevent typos and enable
  exhaustive matching.
- Fields are intentionally minimal. Do not add fields unless another
  algorithm module needs them for a coordination decision.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from fleet_coordination.models.pose import Pose2D


class RobotStatus(Enum):
    """Operational status of a robot.

    State transitions:
        IDLE -> NAVIGATING (task assigned, moving to goal)
        NAVIGATING -> WAITING (yielding at intersection / conflict)
        NAVIGATING -> IDLE (task completed)
        NAVIGATING -> EMERGENCY_STOP (safety trigger)
        WAITING -> NAVIGATING (conflict resolved, resuming)
        * -> CHARGING (battery low)
        * -> FAILED (hardware/software fault)
        EMERGENCY_STOP -> IDLE (manual reset)
    """

    IDLE = auto()
    NAVIGATING = auto()
    WAITING = auto()
    CHARGING = auto()
    FAILED = auto()
    EMERGENCY_STOP = auto()


@dataclass
class RobotState:
    """Snapshot of a robot's current state.

    This is broadcast to peers. Every peer stores the latest received
    RobotState per robot_id, along with receive-time for freshness.
    """

    robot_id: str
    timestamp: float = field(default_factory=time.time)
    pose: Pose2D = field(default_factory=lambda: Pose2D(0.0, 0.0, 0.0))
    linear_velocity: float = 0.0  # m/s, magnitude
    angular_velocity: float = 0.0  # rad/s
    battery_percent: float = 100.0  # 0.0–100.0
    current_task_id: str | None = None
    status: RobotStatus = RobotStatus.IDLE

    def age(self, now: float | None = None) -> float:
        """How old is this state snapshot (seconds).

        Args:
            now: Current time. If None, uses time.time().
                 Pass explicitly in tests for determinism.
        """
        if now is None:
            now = time.time()
        return now - self.timestamp

    def is_available(self) -> bool:
        """Whether this robot could potentially accept a new task."""
        return self.status in (RobotStatus.IDLE, RobotStatus.WAITING)

    def __repr__(self) -> str:
        return (
            f"RobotState(id={self.robot_id!r}, status={self.status.name}, "
            f"pose={self.pose}, battery={self.battery_percent:.1f}%)"
        )
