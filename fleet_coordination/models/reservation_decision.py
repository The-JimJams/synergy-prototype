"""
ReservationDecision — the output of the ReservationManager.
============================================================

Represents the result of a reservation request, renewal, or release
operation performed by the local robot's ReservationManager.

reason codes (stored in `reason` field):
  "ACCEPTED"                — New reservation successfully granted.
  "RELEASED"                — Existing claim successfully released.
  "RENEWED"                 — Existing claim extended to a new end_time.
  "RESOURCE_CONFLICT"       — Rejected: a known, non-expired peer
                              reservation overlaps the requested window.
  "PRIORITY_LOST"           — Rejected: a valid PriorityDecision was
                              provided but this robot did not win.
  "STALE_PRIORITY_DECISION" — Rejected: the provided PriorityDecision
                              is too old to be trusted.
  "INVALID_INTERVAL"        — Rejected: end_time <= start_time, or the
                              requested window has already passed.
  "NOT_OWNER"               — Rejected: the claim_id exists but belongs
                              to a different robot (release/renew only).
  "ALREADY_RELEASED"        — Idempotent: claim_id was not found;
                              treated as already-released (safe).
  "ALREADY_RESERVED"        — Idempotent: an identical active claim by
                              this robot already covers this resource.

Consumed by:
  - Caller code (ROS 2 node, coordinator loop) to decide next action.
  - DecisionLogger (future) for audit trail storage.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from fleet_coordination.models.reservation import Reservation


@dataclass
class ReservationDecision:
    """Result of a reservation request, renewal, or release operation."""

    # Whether the operation was accepted (True) or rejected / no-op (False).
    # For RELEASED and ALREADY_RELEASED: accepted=True (idempotent success).
    accepted: bool

    # Identity of the robot that made the request.
    robot_id: str

    # The resource this decision pertains to.
    resource_id: str

    # The time window of the request or resulting reservation.
    start_time: float
    end_time: float

    # Unique identifier of the reservation.
    # Set on ACCEPTED / RENEWED. Set to the released claim_id on RELEASED.
    # None when the request was rejected before a claim was created.
    claim_id: str | None = None

    # Human-readable outcome code (see module docstring for valid values).
    reason: str = ""

    # claim_id of the conflicting peer reservation on RESOURCE_CONFLICT rejections.
    # None for all other outcomes.
    conflicting_claim_id: str | None = None

    # The resulting Reservation object on ACCEPTED / RENEWED.
    # None on rejections and on RELEASED / ALREADY_RELEASED.
    reservation: Reservation | None = None

    # Unix epoch timestamp at which this decision was produced.
    decided_at: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        claim = f", claim={self.claim_id!r}" if self.claim_id else ""
        return (
            f"ReservationDecision(accepted={self.accepted}, reason={self.reason!r}, "
            f"robot={self.robot_id!r}, resource={self.resource_id!r}{claim})"
        )
