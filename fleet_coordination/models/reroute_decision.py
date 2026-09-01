"""
RerouteDecision Data Model
==========================

Represents the deterministic recommendation produced by RerouteEvaluator.

Zero ROS imports — pure dataclass.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from fleet_coordination.models.pose import Pose2D


@dataclass
class RerouteDecision:
    """Deterministic output of the RerouteEvaluator."""

    robot_id: str
    blocked_resource_id: str
    reroute_required: bool
    alternative_resource_id: str | None = None
    suggested_waypoints: list[Pose2D] = field(default_factory=list)
    reason: str = ""
    decided_at: float = field(default_factory=time.time)

    def is_reroute_available(self) -> bool:
        """Whether a valid alternative route was found and recommended."""
        return self.reroute_required and self.alternative_resource_id is not None

    def __repr__(self) -> str:
        return (
            f"RerouteDecision(robot={self.robot_id!r}, blocked={self.blocked_resource_id!r}, "
            f"required={self.reroute_required}, alternative={self.alternative_resource_id!r}, "
            f"reason={self.reason!r})"
        )
