"""
RobotIntent — what a robot PLANS to do in the near future.

KEY PRINCIPLE: Robots must share INTENT, not only current position.

Knowing where a robot IS tells you about the past.
Knowing where a robot INTENDS TO GO tells you about the future.
Conflict detection requires future intent.

DESIGN NOTES:
- `valid_until` is MANDATORY. An intent without expiry is dangerous:
  if a robot crashes, its intent persists forever, blocking resources.
- `target_resource_id` is the primary field for ConflictDetector v1.
  It represents named shared resources (e.g., "I1", "I2", "DOCK_3").
- `planned_waypoints` is optional (default empty list). It will be used
  by trajectory-based conflict detection in a future enhancement.
- `priority` is the raw priority score computed by PriorityEngine.
  It is included in the intent so peers can independently resolve conflicts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from fleet_coordination.models.pose import Pose2D


@dataclass
class RobotIntent:
    """What a robot plans to do — broadcast to peers for conflict detection."""

    robot_id: str
    timestamp: float = field(default_factory=time.time)

    # What task this intent relates to (None if no active task)
    task_id: Optional[str] = None

    # The shared resource this robot intends to use (e.g., "I1", "DOCK_3")
    # This is the PRIMARY field for ConflictDetector v1
    target_resource_id: Optional[str] = None

    # When the robot expects to arrive at / start using the resource
    eta: Optional[float] = None  # Unix epoch seconds

    # Priority score — computed by PriorityEngine, included for peers
    priority: float = 0.0

    # Ordered trajectory waypoints (optional, for future trajectory-based detection)
    planned_waypoints: List[Pose2D] = field(default_factory=list)

    # Hard expiry — intent is INVALID after this time, no exceptions
    valid_until: float = 0.0  # Unix epoch seconds

    def is_expired(self, now: Optional[float] = None) -> bool:
        """Check if this intent has passed its hard expiry.

        An expired intent must NEVER be treated as valid.
        This protects against crashed robots whose intents
        would otherwise block resources indefinitely.

        Args:
            now: Current time. If None, uses time.time().
                 Pass explicitly in tests for determinism.
        """
        if now is None:
            now = time.time()
        return now > self.valid_until

    def age(self, now: Optional[float] = None) -> float:
        """How old is this intent (seconds since creation)."""
        if now is None:
            now = time.time()
        return now - self.timestamp

    def __repr__(self) -> str:
        return (
            f"RobotIntent(id={self.robot_id!r}, resource={self.target_resource_id!r}, "
            f"priority={self.priority:.2f}, expired={self.is_expired()})"
        )
