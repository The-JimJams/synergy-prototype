"""
Peer health and fleet failure detection data models.
====================================================

Represents the health evaluation state of peer AMRs in the decentralized fleet.

Zero ROS imports — pure dataclasses.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto


class PeerHealthStatus(Enum):
    """Health classification of a peer AMR based on heartbeat freshness & telemetry."""

    HEALTHY = auto()
    SUSPECTED = auto()
    FAILED = auto()


@dataclass(frozen=True)
class PeerHealthAssessment:
    """Health snapshot for a single peer robot."""

    robot_id: str
    status: PeerHealthStatus
    last_seen_timestamp: float
    age_seconds: float
    reason: str  # e.g., "HEARTBEAT_ACTIVE", "HEARTBEAT_TIMEOUT_SUSPECTED", "HEARTBEAT_TIMEOUT_FAILED", "SELF_REPORTED_FAILURE"
    evaluated_at: float = field(default_factory=time.time)

    def is_healthy(self) -> bool:
        """Whether this robot is currently healthy and active."""
        return self.status == PeerHealthStatus.HEALTHY

    def is_failed(self) -> bool:
        """Whether this robot is declared failed."""
        return self.status == PeerHealthStatus.FAILED

    def __repr__(self) -> str:
        return (
            f"PeerHealthAssessment(robot={self.robot_id!r}, status={self.status.name}, "
            f"age={self.age_seconds:.2f}s, reason={self.reason!r})"
        )


@dataclass
class FleetHealthReport:
    """Comprehensive health assessment across all known peers in the fleet."""

    assessments: dict[str, PeerHealthAssessment] = field(default_factory=dict)
    suspected_robot_ids: list[str] = field(default_factory=list)
    failed_robot_ids: list[str] = field(default_factory=list)
    evaluated_at: float = field(default_factory=time.time)

    def has_failures(self) -> bool:
        """Check if any peer robot is in FAILED status."""
        return len(self.failed_robot_ids) > 0

    def has_suspicions(self) -> bool:
        """Check if any peer robot is in SUSPECTED status."""
        return len(self.suspected_robot_ids) > 0

    def __repr__(self) -> str:
        return (
            f"FleetHealthReport(total={len(self.assessments)}, "
            f"suspected={self.suspected_robot_ids}, failed={self.failed_robot_ids})"
        )
