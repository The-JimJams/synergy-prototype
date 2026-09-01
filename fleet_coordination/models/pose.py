"""
Pose2D — 2D position and orientation on the warehouse floor.

ASSUMPTION: Coordinates are in a consistent global reference frame.
The specific frame (e.g., ROS 'map' frame) is determined by the
ROS adapter layer at integration time. The algorithm layer treats
these as abstract (x, y, theta) values.

Unit conventions:
    x, y  — metres
    theta — radians, range [-π, π]
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose2D:
    """Immutable 2D pose (position + orientation).

    Frozen because poses represent a snapshot in time.
    A robot's pose changes, but a specific recorded pose does not.
    """

    x: float  # metres
    y: float  # metres
    theta: float = 0.0  # radians, [-π, π]

    def distance_to(self, other: Pose2D) -> float:
        """Euclidean distance between two poses (ignores orientation).

        This is used for cost estimation (e.g., how far is a robot
        from a task pickup location). It is NOT used for collision
        detection — that is Nav2's job.
        """
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __repr__(self) -> str:
        return f"Pose2D(x={self.x:.2f}, y={self.y:.2f}, θ={math.degrees(self.theta):.1f}°)"
