"""
ReservationManager — Resource Reservation Lifecycle Algorithm
=============================================================

Validates and manages the local robot's resource reservation claims against
the WorldModel's known reservation state.

ARCHITECTURAL PRINCIPLES:
1. Stateless Service: ReservationManager holds no state of its own.
   All state is read from and written to the provided WorldModel.
2. WorldModel Mutation Scope: ONLY `world_model._reservations` is ever
   mutated. _own_state, _own_intent, _peer_states, _peer_intents, and
   _tasks are NEVER touched.
3. Local Safety (INV-1): Within a single consistent WorldModel view,
   ReservationManager never accepts a new reservation that overlaps a
   known non-expired peer reservation on the same exclusive resource.
4. Non-Preemption (INV-8): An active, granted reservation is never
   preempted or revoked by a competing request, regardless of priority.
5. Determinism (INV-6): Identical requests against identical WorldModel
   state produce bit-for-bit identical ReservationDecision outputs.
6. Atomic-on-Failure Replacement: The renew_reservation() method
   constructs a replacement Reservation before mutating WorldModel.
   If validation fails at any step, WorldModel remains unchanged.
7. ROS-Free: Zero rclpy / ROS 2 / Gazebo / Nav2 imports.

DISTRIBUTED SAFETY NOTE:
  This manager provides *local* mutual exclusion only. Two robots on
  separate, stale WorldModel views may both accept overlapping
  reservations simultaneously. Stale concurrent decisions are reconciled
  deterministically when peer reservation information is eventually
  exchanged and processed by the ConflictDetector + PriorityEngine
  pipeline on the next coordination cycle.

EXPIRY SEMANTICS SUMMARY (matches WorldModel & ConflictDetector):
  now < start_time                  → Accepted/Pending  (blocks overlaps)
  start_time <= now <= end_time     → Active            (blocks overlaps)
  end_time < now <= expires_at      → Grace Period      (blocks overlaps)
  now > expires_at                  → Expired           (never blocks)

ALREADY_RESERVED SEMANTICS:
  If the requesting robot already holds a non-expired reservation on the
  same resource whose window overlaps the new request, the operation is
  treated as idempotent. reason='ALREADY_RESERVED', accepted=True, and
  the existing reservation's claim_id is returned. A second UUID is NOT
  created. Non-overlapping intervals on the same resource are always
  granted as independent reservations.

EXPIRED CLAIM RENEWAL:
  renew_reservation() on a claim whose is_expired(now)==True returns
  accepted=False, reason='INVALID_INTERVAL'. This reuses the existing
  invalid-interval reason code rather than introducing a new enum value.
  Callers who need to distinguish 'expired' from 'inverted interval'
  should check whether the claim exists and is_expired() before calling
  renew_reservation().

UNKNOWN CLAIM ASYMMETRY:
  release_reservation(unknown_claim_id) → accepted=True, reason='ALREADY_RELEASED'
    (idempotent: the claim is already gone)
  renew_reservation(unknown_claim_id)   → accepted=False, reason='ALREADY_RELEASED'
    (logical error: cannot extend a non-existent claim)
"""

from __future__ import annotations

import math
import time

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.priority_decision import PriorityDecision
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.reservation_decision import ReservationDecision


class ReservationManager:
    """Algorithmic manager for local resource reservation lifecycle.

    Stateless: all persistent state lives inside the WorldModel passed
    to each method call.
    """

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize the ReservationManager with configuration.

        Args:
            config: Coordination configuration. Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = config or CoordinationConfig()

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    # =========================================================================
    # Public API
    # =========================================================================

    def request_reservation(
        self,
        world_model: WorldModel,
        resource_id: str,
        start_time: float,
        end_time: float,
        priority: float = 0.0,
        priority_decision: PriorityDecision | None = None,
        now: float = 0.0,
    ) -> ReservationDecision:
        """Validate and grant/deny a resource claim for the local robot.

        Validation order:
          0. Finite-number check (now, start_time, end_time must be finite)
          1. Interval validity (end_time > start_time, end_time > now)
          2. PriorityDecision freshness and winner check (if provided)
          3. Peer reservation conflict scan (local single-view exclusion)
          3b. Own-reservation overlap check (ALREADY_RESERVED idempotency)
          4. Grant: construct and store the Reservation

        Authoritative priority score:
          - With PriorityDecision: uses the winner's score from the decision.
          - Without PriorityDecision: uses the `priority` argument directly.

        Args:
            world_model:        The local WorldModel to query and mutate.
            resource_id:        Target shared resource (e.g. 'I1', 'DOCK_A').
            start_time:         Requested occupancy start (Unix epoch seconds).
            end_time:           Requested occupancy end (Unix epoch seconds).
            priority:           Fallback priority score (uncontested requests).
            priority_decision:  Arbitration result from PriorityEngine, or None.
            now:                Current reference time (Unix epoch seconds).

        Returns:
            ReservationDecision with accepted=True on success, or
            accepted=False with a reason code on rejection.
        """
        robot_id = world_model.robot_id

        # ------------------------------------------------------------------
        # Step 0 — Finite-number validation (NaN/Infinity are never valid)
        # ------------------------------------------------------------------
        for val in (now, start_time, end_time):
            if not math.isfinite(val):
                return ReservationDecision(
                    accepted=False,
                    robot_id=robot_id,
                    resource_id=resource_id,
                    start_time=start_time,
                    end_time=end_time,
                    reason="INVALID_INTERVAL",
                    decided_at=time.time(),
                )

        # ------------------------------------------------------------------
        # Step 1 — Interval validity
        # ------------------------------------------------------------------
        if end_time <= start_time:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                reason="INVALID_INTERVAL",
                decided_at=time.time(),
            )

        if end_time <= now:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                reason="INVALID_INTERVAL",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Step 2 — PriorityDecision arbitration (if provided)
        # ------------------------------------------------------------------
        authoritative_priority = priority

        if priority_decision is not None:
            # 2a. Freshness check
            max_age = self._config.timeouts.peer_intent_max_age_seconds
            decision_age = now - priority_decision.decided_at
            if decision_age > max_age:
                return ReservationDecision(
                    accepted=False,
                    robot_id=robot_id,
                    resource_id=resource_id,
                    start_time=start_time,
                    end_time=end_time,
                    reason="STALE_PRIORITY_DECISION",
                    decided_at=time.time(),
                )

            # 2b. Winner check
            if not priority_decision.is_winner(robot_id):
                return ReservationDecision(
                    accepted=False,
                    robot_id=robot_id,
                    resource_id=resource_id,
                    start_time=start_time,
                    end_time=end_time,
                    reason="PRIORITY_LOST",
                    decided_at=time.time(),
                )

            # 2c. Derive authoritative priority score from the decision
            if priority_decision.robot_a_id == robot_id:
                authoritative_priority = priority_decision.score_a
            else:
                authoritative_priority = priority_decision.score_b

        # ------------------------------------------------------------------
        # Step 3 — Peer reservation conflict scan (INV-1: local exclusion)
        # ------------------------------------------------------------------
        candidate = Reservation(
            resource_id=resource_id,
            robot_id=robot_id,
            start_time=start_time,
            end_time=end_time,
            priority=authoritative_priority,
            expires_at=end_time + self._config.timeouts.default_reservation_duration_seconds,
        )

        conflict_claim_id = self._find_conflicting_peer_reservation(
            world_model, candidate, now
        )
        if conflict_claim_id is not None:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                reason="RESOURCE_CONFLICT",
                conflicting_claim_id=conflict_claim_id,
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Step 3b — Own-reservation overlap check (idempotency, INV-ALREADY)
        # If this robot already holds a non-expired reservation on the same
        # resource that overlaps this window, return it rather than creating
        # a second UUID reservation.
        # ------------------------------------------------------------------
        own_claim_id = self._find_own_overlapping_reservation(
            world_model, candidate, now
        )
        if own_claim_id is not None:
            existing_own = world_model.get_reservation(own_claim_id)
            return ReservationDecision(
                accepted=True,
                robot_id=robot_id,
                resource_id=resource_id,
                start_time=start_time,
                end_time=end_time,
                claim_id=own_claim_id,
                reason="ALREADY_RESERVED",
                reservation=existing_own,
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Step 4 — Grant: store the reservation
        # ------------------------------------------------------------------
        world_model.add_reservation(candidate)

        return ReservationDecision(
            accepted=True,
            robot_id=robot_id,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            claim_id=candidate.claim_id,
            reason="ACCEPTED",
            reservation=candidate,
            decided_at=time.time(),
        )

    def renew_reservation(
        self,
        world_model: WorldModel,
        claim_id: str,
        new_end_time: float,
        now: float = 0.0,
    ) -> ReservationDecision:
        """Extend an active reservation's end_time using atomic replacement.

        The replacement Reservation shares the original claim_id, robot_id,
        resource_id, start_time, priority, and created_at — only end_time
        and expires_at are updated.

        WorldModel remains completely unchanged if any validation step fails
        (atomic-on-failure guarantee).

        Args:
            world_model:   The local WorldModel to query and mutate.
            claim_id:      Unique identifier of the existing reservation.
            new_end_time:  Extended occupancy end (Unix epoch seconds).
            now:           Current reference time (Unix epoch seconds).

        Returns:
            ReservationDecision with accepted=True and reason="RENEWED" on
            success, or accepted=False with a reason code on rejection.

        NOTE on expired claims:
            If the claim exists but is_expired(now) is True, this method
            returns accepted=False with reason='INVALID_INTERVAL'. Callers
            that need to distinguish "expired" from "inverted interval"
            should call world_model.get_reservation(claim_id) and check
            is_expired(now) before calling renew_reservation().
        """
        robot_id = world_model.robot_id

        # ------------------------------------------------------------------
        # Step 0 — Finite-number validation (NaN/Infinity are never valid)
        # ------------------------------------------------------------------
        for val in (now, new_end_time):
            if not math.isfinite(val):
                return ReservationDecision(
                    accepted=False,
                    robot_id=robot_id,
                    resource_id="",
                    start_time=0.0,
                    end_time=new_end_time,
                    claim_id=claim_id,
                    reason="INVALID_INTERVAL",
                    decided_at=time.time(),
                )

        # ------------------------------------------------------------------
        # Lookup: claim must exist and not be expired
        # ------------------------------------------------------------------
        existing = world_model.get_reservation(claim_id)
        if existing is None:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id="",
                start_time=0.0,
                end_time=new_end_time,
                claim_id=claim_id,
                reason="ALREADY_RELEASED",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Ownership check (INV-2)
        # ------------------------------------------------------------------
        if existing.robot_id != robot_id:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=existing.resource_id,
                start_time=existing.start_time,
                end_time=new_end_time,
                claim_id=claim_id,
                reason="NOT_OWNER",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Expiry check — cannot renew an already-expired reservation
        # ------------------------------------------------------------------
        if existing.is_expired(now):
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=existing.resource_id,
                start_time=existing.start_time,
                end_time=new_end_time,
                claim_id=claim_id,
                reason="INVALID_INTERVAL",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Interval validity — new_end_time must be after existing start_time
        # ------------------------------------------------------------------
        if new_end_time <= existing.start_time:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=existing.resource_id,
                start_time=existing.start_time,
                end_time=new_end_time,
                claim_id=claim_id,
                reason="INVALID_INTERVAL",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Build replacement — check extension window against peer reservations
        # The extension window is [existing.end_time, new_end_time].
        # We check the full candidate window to be conservative.
        # ------------------------------------------------------------------
        grace = self._config.timeouts.default_reservation_duration_seconds
        renewed = Reservation(
            resource_id=existing.resource_id,
            robot_id=existing.robot_id,
            start_time=existing.start_time,
            end_time=new_end_time,
            priority=existing.priority,
            claim_id=existing.claim_id,
            created_at=existing.created_at,
            expires_at=new_end_time + grace,
        )

        conflict_claim_id = self._find_conflicting_peer_reservation(
            world_model, renewed, now, exclude_claim_id=claim_id
        )
        if conflict_claim_id is not None:
            # WorldModel not mutated — atomic-on-failure
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=existing.resource_id,
                start_time=existing.start_time,
                end_time=new_end_time,
                claim_id=claim_id,
                reason="RESOURCE_CONFLICT",
                conflicting_claim_id=conflict_claim_id,
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Atomic replacement — overwrite in WorldModel (dict key = claim_id)
        # ------------------------------------------------------------------
        world_model.add_reservation(renewed)

        return ReservationDecision(
            accepted=True,
            robot_id=robot_id,
            resource_id=existing.resource_id,
            start_time=existing.start_time,
            end_time=new_end_time,
            claim_id=claim_id,
            reason="RENEWED",
            reservation=renewed,
            decided_at=time.time(),
        )

    def release_reservation(
        self,
        world_model: WorldModel,
        claim_id: str,
        now: float = 0.0,
    ) -> ReservationDecision:
        """Explicitly release an active reservation held by the local robot.

        Idempotent: if the claim_id is not found, returns accepted=True with
        reason="ALREADY_RELEASED" — treating unknown claims as already gone.

        Args:
            world_model:  The local WorldModel to query and mutate.
            claim_id:     Unique identifier of the reservation to release.
            now:          Current reference time (Unix epoch seconds).

        Returns:
            ReservationDecision with accepted=True on success (RELEASED or
            ALREADY_RELEASED), or accepted=False with reason="NOT_OWNER"
            if the claim belongs to a different robot.
        """
        robot_id = world_model.robot_id

        existing = world_model.get_reservation(claim_id)

        # ------------------------------------------------------------------
        # Idempotent: unknown claim_id → treat as already released
        # ------------------------------------------------------------------
        if existing is None:
            return ReservationDecision(
                accepted=True,
                robot_id=robot_id,
                resource_id="",
                start_time=0.0,
                end_time=0.0,
                claim_id=claim_id,
                reason="ALREADY_RELEASED",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Ownership check (INV-2)
        # ------------------------------------------------------------------
        if existing.robot_id != robot_id:
            return ReservationDecision(
                accepted=False,
                robot_id=robot_id,
                resource_id=existing.resource_id,
                start_time=existing.start_time,
                end_time=existing.end_time,
                claim_id=claim_id,
                reason="NOT_OWNER",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Release
        # ------------------------------------------------------------------
        world_model.remove_reservation(claim_id)

        return ReservationDecision(
            accepted=True,
            robot_id=robot_id,
            resource_id=existing.resource_id,
            start_time=existing.start_time,
            end_time=existing.end_time,
            claim_id=claim_id,
            reason="RELEASED",
            decided_at=time.time(),
        )

    def check_availability(
        self,
        world_model: WorldModel,
        resource_id: str,
        start_time: float,
        end_time: float,
        robot_id: str,
        now: float = 0.0,
    ) -> tuple[bool, Reservation | None]:
        """Query whether a time window on a resource is free of peer reservations.

        "Free" means: no non-expired peer reservation (belonging to a robot
        other than `robot_id`) temporally overlaps [start_time, end_time).

        This is a read-only query — WorldModel is never mutated.

        Args:
            world_model:  The local WorldModel to query.
            resource_id:  Target shared resource.
            start_time:   Query window start (Unix epoch seconds).
            end_time:     Query window end (Unix epoch seconds).
            robot_id:     The requesting robot's ID (excluded from conflict check).
            now:          Current reference time.

        Returns:
            (True, None) if the window is free.
            (False, blocking_reservation) if a conflict exists.
        """
        probe = Reservation(
            resource_id=resource_id,
            robot_id=robot_id,
            start_time=start_time,
            end_time=end_time,
            priority=0.0,
            expires_at=end_time + 1.0,
        )
        conflict_id = self._find_conflicting_peer_reservation(
            world_model, probe, now
        )
        if conflict_id is None:
            return True, None
        blocking = world_model.get_reservation(conflict_id)
        return False, blocking

    # =========================================================================
    # Internal helpers
    # =========================================================================

    def _find_conflicting_peer_reservation(
        self,
        world_model: WorldModel,
        candidate: Reservation,
        now: float,
        exclude_claim_id: str | None = None,
    ) -> str | None:
        """Return the claim_id of the first non-expired PEER reservation that
        overlaps the candidate, or None if the resource window is clear.

        "Peer" means: robot_id != candidate.robot_id.
        Expired reservations (now > expires_at) are never blocking (INV-3).
        Boundary-touching intervals (A_end == B_start) are non-overlapping (INV-7).

        Args:
            world_model:       WorldModel to scan.
            candidate:         Proposed reservation to check against.
            now:               Current reference time.
            exclude_claim_id:  Skip this claim_id (used during renewal to
                               avoid self-collision with the existing record).

        Returns:
            claim_id of the first conflicting reservation, or None.
        """
        for claim_id, res in world_model.get_all_reservations().items():
            # Skip self-owned reservations
            if res.robot_id == candidate.robot_id:
                continue
            # Skip excluded claim (renewal scenario)
            if exclude_claim_id is not None and claim_id == exclude_claim_id:
                continue
            # Expired reservations never block (INV-3)
            if res.is_expired(now):
                continue
            # Resource must match
            if res.resource_id != candidate.resource_id:
                continue
            # Temporal overlap check — boundary-touching is NOT a conflict (INV-7)
            if candidate.overlaps_temporally(res):
                return claim_id
        return None

    def _find_own_overlapping_reservation(
        self,
        world_model: WorldModel,
        candidate: Reservation,
        now: float,
    ) -> str | None:
        """Return the claim_id of the first non-expired OWN reservation on the
        same resource that temporally overlaps the candidate, or None.

        Used by request_reservation() to implement ALREADY_RESERVED idempotency:
        if this robot already holds a valid overlapping claim, a second UUID is
        not created. Non-overlapping own reservations on the same resource are
        not returned — they represent independent time slots.

        Args:
            world_model:  WorldModel to scan.
            candidate:    Proposed reservation to check against.
            now:          Current reference time.

        Returns:
            claim_id of the first overlapping own reservation, or None.
        """
        for claim_id, res in world_model.get_all_reservations().items():
            # Only self-owned reservations
            if res.robot_id != candidate.robot_id:
                continue
            # Expired own reservations are not blocking
            if res.is_expired(now):
                continue
            # Resource must match
            if res.resource_id != candidate.resource_id:
                continue
            # Temporal overlap (boundary-touching is not a conflict)
            if candidate.overlaps_temporally(res):
                return claim_id
        return None
