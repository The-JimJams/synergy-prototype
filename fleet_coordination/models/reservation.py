"""
Reservation — a temporary claim over a shared resource.

DESIGN NOTES:
- `end_time` is when the robot EXPECTS to finish using the resource.
- `expires_at` is the HARD DEADLINE after which the reservation is
  invalid regardless of whether the robot released it. This protects
  against robots that crash or lose communication while holding a
  reservation — without expiry, a ghost reservation would permanently
  block the resource.
- `claim_id` is a UUID string for unique identification. Two robots
  may request the same resource — each request gets a different claim_id.
- `priority` is stored so the ReservationManager can compare competing
  claims without needing to call PriorityEngine again.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


def _new_claim_id() -> str:
    """Generate a unique claim ID."""
    return str(uuid.uuid4())


@dataclass
class Reservation:
    """A temporary claim over a shared resource (e.g., intersection I1)."""

    resource_id: str  # e.g., "I1", "DOCK_3"
    robot_id: str
    start_time: float  # Unix epoch — when the robot starts using it
    end_time: float  # Unix epoch — when the robot expects to leave
    priority: float  # priority score at time of reservation
    claim_id: str = field(default_factory=_new_claim_id)
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0  # Hard expiry — MUST be set

    def is_expired(self, now: float | None = None) -> bool:
        """Check if this reservation has passed its hard expiry.

        An expired reservation MUST be treated as released, even if
        the robot never explicitly released it.
        """
        if now is None:
            now = time.time()
        return now > self.expires_at

    def is_active(self, now: float | None = None) -> bool:
        """Check if this reservation is currently in its active window.

        Active means: not expired AND current time is within [start_time, end_time].
        """
        if now is None:
            now = time.time()
        return (
            not self.is_expired(now)
            and self.start_time <= now <= self.end_time
        )

    def overlaps_temporally(self, other: Reservation) -> bool:
        """Check if two reservations have overlapping time windows.

        Two intervals [a_start, a_end] and [b_start, b_end] overlap
        if and only if: a_start < b_end AND b_start < a_end
        """
        return self.start_time < other.end_time and other.start_time < self.end_time

    def __repr__(self) -> str:
        return (
            f"Reservation(resource={self.resource_id!r}, robot={self.robot_id!r}, "
            f"priority={self.priority:.2f}, expired={self.is_expired()})"
        )
