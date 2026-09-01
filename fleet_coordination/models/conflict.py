"""
ConflictReport — the output of the ConflictDetector.

When the ConflictDetector identifies that two robots have overlapping
claims on the same resource in overlapping time windows, it produces
a ConflictReport describing the conflict.

This report is consumed by:
- PriorityEngine (to determine who wins)
- ReservationManager (to grant/deny reservations)
- DecisionLogger (to explain the decision)

DESIGN NOTES:
- `severity` is based on how soon the conflict will occur. This
  helps the system prioritize which conflicts to resolve first.
- `conflict_id` is a unique identifier for deduplication — the same
  physical conflict detected on multiple ticks should not generate
  duplicate resolution actions.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from enum import Enum, auto


class ConflictSeverity(Enum):
    """How urgently a conflict needs resolution.

    Based on temporal proximity:
        LOW      — conflict is > 30s in the future
        MEDIUM   — conflict is 10–30s in the future
        HIGH     — conflict is < 10s in the future
        CRITICAL — robots are already at the same resource

    NOTE: These thresholds are experimental parameters. They
    should be tunable, not hard-coded as safety limits.
    """

    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class ConflictReport:
    """Description of a detected conflict between two robots."""

    robot_a_id: str
    robot_b_id: str
    resource_id: str
    overlap_start: float  # Unix epoch — when the overlap begins
    overlap_end: float  # Unix epoch — when the overlap ends
    severity: ConflictSeverity = ConflictSeverity.LOW
    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: float = field(default_factory=time.time)

    def overlap_duration(self) -> float:
        """Duration of the temporal overlap in seconds."""
        return max(0.0, self.overlap_end - self.overlap_start)

    def involves_robot(self, robot_id: str) -> bool:
        """Check if a specific robot is involved in this conflict."""
        return robot_id in (self.robot_a_id, self.robot_b_id)

    def __repr__(self) -> str:
        return (
            f"ConflictReport({self.robot_a_id!r} vs {self.robot_b_id!r} "
            f"at {self.resource_id!r}, severity={self.severity.name}, "
            f"overlap={self.overlap_duration():.1f}s)"
        )
