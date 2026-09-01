"""
Obstacle Data Model
===================

Represents a spatial blockage on a named warehouse resource or aisle segment.

Zero ROS imports — pure dataclass.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from fleet_coordination.models.pose import Pose2D


@dataclass
class Obstacle:
    """A spatial blockage on a named warehouse resource or aisle segment."""

    obstacle_id: str
    resource_id: str
    detected_at: float = field(default_factory=time.time)
    valid_until: float = 0.0
    location: Pose2D | None = None
    is_active: bool = True
    reporter_id: str = ""

    def __post_init__(self) -> None:
        if not self.obstacle_id:
            raise ValueError("obstacle_id must be a non-empty string")
        if not self.resource_id:
            raise ValueError("resource_id must be a non-empty string")
        if self.valid_until < 0.0:
            raise ValueError("valid_until cannot be negative")

    def is_expired(self, now: float | None = None) -> bool:
        """Check if the obstacle validity window has expired.

        If valid_until is 0.0, the obstacle never automatically expires by time.
        """
        if self.valid_until <= 0.0:
            return False
        if now is None:
            now = time.time()
        return now > self.valid_until

    def is_blocking(self, now: float | None = None) -> bool:
        """Check if obstacle is currently actively blocking a resource."""
        return self.is_active and not self.is_expired(now)

    def __repr__(self) -> str:
        loc_str = f"({self.location.x:.2f}, {self.location.y:.2f})" if self.location else "None"
        return (
            f"Obstacle(id={self.obstacle_id!r}, resource={self.resource_id!r}, "
            f"active={self.is_active}, location={loc_str}, valid_until={self.valid_until:.1f})"
        )
