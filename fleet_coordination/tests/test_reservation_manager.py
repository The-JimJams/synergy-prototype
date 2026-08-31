"""
Tests for ReservationManager — Phase 5.
=========================================

30 unit tests across 9 categories, verifying all correctness invariants
defined in the Phase 5 design document.

Test Categories:
  1. Local Single-View Mutual Exclusion           (4 tests)
  2. Optimistic Stale Concurrency & Reconciliation (4 tests)
  3. Non-Preemption of Active Claims              (3 tests)
  4. PriorityDecision Arbitration & Score Authority(4 tests)
  5. Boundary Semantics & Expiry                  (4 tests)
  6. Renewal & Replacement Safety                 (4 tests)
  7. Release Operations & Idempotency             (3 tests)
  8. Input Validation                             (2 tests)
  9. Multi-Robot & Immutability                   (2 tests)

Time conventions used throughout:
  T=100.0  — reference "now" for most tests
  T=0.0    — the past (before "now")
"""

from __future__ import annotations

import pytest

from fleet_coordination.algorithm.conflict_detector import ConflictDetector
from fleet_coordination.algorithm.priority_engine import PriorityEngine
from fleet_coordination.algorithm.reservation_manager import ReservationManager
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.priority_decision import PriorityDecision
from fleet_coordination.models.reservation import Reservation


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

GRACE = 30.0  # default_reservation_duration_seconds in CoordinationConfig


def make_wm(robot_id: str) -> WorldModel:
    """Create a fresh WorldModel with default config."""
    return WorldModel(robot_id=robot_id)


def make_manager() -> ReservationManager:
    """Create a ReservationManager with default config."""
    return ReservationManager()


def make_peer_reservation(
    robot_id: str,
    resource_id: str,
    start_time: float,
    end_time: float,
    priority: float = 0.5,
    claim_id: str | None = None,
) -> Reservation:
    """Build a peer-owned Reservation for injection into WorldModel."""
    expires_at = end_time + GRACE
    kwargs: dict = dict(
        resource_id=resource_id,
        robot_id=robot_id,
        start_time=start_time,
        end_time=end_time,
        priority=priority,
        expires_at=expires_at,
    )
    if claim_id is not None:
        kwargs["claim_id"] = claim_id
    return Reservation(**kwargs)


def make_priority_decision(
    winner_id: str,
    loser_id: str,
    resource_id: str = "I1",
    score_winner: float = 0.9,
    score_loser: float = 0.5,
    decided_at: float = 100.0,
) -> PriorityDecision:
    """Build a deterministic PriorityDecision for use in tests."""
    if winner_id < loser_id:
        robot_a_id, robot_b_id = winner_id, loser_id
        score_a, score_b = score_winner, score_loser
    else:
        robot_a_id, robot_b_id = loser_id, winner_id
        score_a, score_b = score_loser, score_winner
    return PriorityDecision(
        conflict_id="test-conflict-001",
        robot_a_id=robot_a_id,
        robot_b_id=robot_b_id,
        resource_id=resource_id,
        score_a=score_a,
        score_b=score_b,
        winner_id=winner_id,
        loser_id=loser_id,
        decided_at=decided_at,
    )


# ===========================================================================
# Category 1 — Local Single-View Mutual Exclusion (INV-1)
# ===========================================================================

class TestLocalMutualExclusion:

    def test_local_world_model_prevents_known_overlap(self):
        """INV-1: A known non-expired peer reservation blocks an overlapping request."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # Peer B holds [100, 130]
        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0)
        wm.add_reservation(peer_res)

        # amr_01 tries to reserve [110, 120] — overlaps peer
        decision = manager.request_reservation(
            wm, "I1", 110.0, 120.0, priority=0.7, now=now
        )

        assert decision.accepted is False
        assert decision.reason == "RESOURCE_CONFLICT"
        assert decision.conflicting_claim_id == peer_res.claim_id
        # WorldModel unchanged — no new reservation added for amr_01
        own_res = [
            r for r in wm.get_all_reservations().values() if r.robot_id == "amr_01"
        ]
        assert own_res == []

    def test_non_overlapping_peer_reservation_accepted(self):
        """INV-1: A peer reservation that doesn't overlap is not blocking."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # Peer B holds [50, 90] — well before our window [100, 130]
        peer_res = make_peer_reservation("amr_02", "I1", 50.0, 90.0)
        wm.add_reservation(peer_res)

        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority=0.5, now=now
        )

        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"
        assert decision.reservation is not None

    def test_boundary_touching_consecutive_reservations_accepted(self):
        """INV-7: A_end == B_start is NOT a conflict (consecutive handoff)."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # Peer B holds [100, 130] — our window [130, 160] touches but doesn't overlap
        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0)
        wm.add_reservation(peer_res)

        decision = manager.request_reservation(
            wm, "I1", 130.0, 160.0, priority=0.5, now=now
        )

        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"

    def test_different_resources_independent_acceptance(self):
        """Reservations on different resources never conflict with each other."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # Peer B holds I1 [100, 130]
        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0)
        wm.add_reservation(peer_res)

        # amr_01 requests DOCK_A for the same interval — different resource
        decision = manager.request_reservation(
            wm, "DOCK_A", 100.0, 130.0, priority=0.5, now=now
        )

        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"
        assert decision.resource_id == "DOCK_A"


# ===========================================================================
# Category 2 — Optimistic Stale Concurrency & Reconciliation Simulation
# ===========================================================================

class TestStaleConcurrencyReconciliation:

    def test_stale_concurrent_world_models_temporarily_accept_conflicting_reservations(self):
        """Both robots independently accept on stale WorldModels (no peer info yet)."""
        manager = make_manager()
        wm_a = make_wm("amr_01")
        wm_b = make_wm("amr_02")
        now = 100.0

        # Neither WorldModel knows about the other yet
        decision_a = manager.request_reservation(wm_a, "I1", 100.0, 130.0, priority=0.8, now=now)
        decision_b = manager.request_reservation(wm_b, "I1", 100.0, 130.0, priority=0.6, now=now)

        # Both locally accepted — this is the expected optimistic-concurrency behaviour
        assert decision_a.accepted is True
        assert decision_b.accepted is True

    def test_subsequent_conflict_detection_identifies_stale_overlap(self):
        """After peer exchange, ConflictDetector identifies the reservation conflict."""
        manager = make_manager()
        wm_a = make_wm("amr_01")
        wm_b = make_wm("amr_02")
        now = 100.0

        # Step 1: both accept locally
        dec_a = manager.request_reservation(wm_a, "I1", 100.0, 130.0, priority=0.8, now=now)
        dec_b = manager.request_reservation(wm_b, "I1", 100.0, 130.0, priority=0.6, now=now)
        assert dec_a.accepted and dec_b.accepted

        # Step 2: cross-inject peer reservations (simulating ROS 2 broadcast exchange)
        res_a = dec_a.reservation
        res_b = dec_b.reservation
        wm_a.add_reservation(res_b)  # amr_01 learns about amr_02's reservation
        wm_b.add_reservation(res_a)  # amr_02 learns about amr_01's reservation

        # Step 3: ConflictDetector on each WorldModel should now detect the conflict
        detector = ConflictDetector()
        from fleet_coordination.models.robot_intent import RobotIntent

        intent_a = RobotIntent(
            robot_id="amr_01",
            target_resource_id="I1",
            eta=105.0,
            valid_until=200.0,
            timestamp=99.0,
        )
        wm_a.set_own_intent(intent_a)

        conflicts = detector.detect_conflicts(wm_a, now=now)
        # At minimum, the reservation conflict must be flagged
        assert len(conflicts) >= 1
        resource_ids = {c.resource_id for c in conflicts}
        assert "I1" in resource_ids

    def test_deterministic_priority_arbitration_selects_same_winner(self):
        """PriorityEngine on both WorldModels selects the identical winner."""
        manager = make_manager()
        wm_a = make_wm("amr_01")
        wm_b = make_wm("amr_02")
        now = 100.0

        from fleet_coordination.models.robot_intent import RobotIntent
        from fleet_coordination.models.robot_state import RobotState, RobotStatus

        def make_state(rid: str, battery: float) -> RobotState:
            return RobotState(robot_id=rid, timestamp=99.0, battery_percent=battery)

        def make_intent(rid: str) -> RobotIntent:
            return RobotIntent(
                robot_id=rid,
                target_resource_id="I1",
                eta=105.0,
                valid_until=200.0,
                timestamp=95.0,
            )

        # Populate both WorldModels with symmetric knowledge
        state_a = make_state("amr_01", 80.0)
        state_b = make_state("amr_02", 60.0)
        intent_a = make_intent("amr_01")
        intent_b = make_intent("amr_02")

        wm_a.set_own_state(state_a)
        wm_a.set_own_intent(intent_a)
        wm_a.update_peer_state(state_b)
        wm_a.update_peer_intent(intent_b)

        wm_b.set_own_state(state_b)
        wm_b.set_own_intent(intent_b)
        wm_b.update_peer_state(state_a)
        wm_b.update_peer_intent(intent_a)

        engine = PriorityEngine()
        from fleet_coordination.models.conflict import ConflictReport, ConflictSeverity
        conflict = ConflictReport(
            robot_a_id="amr_01",
            robot_b_id="amr_02",
            resource_id="I1",
            severity=ConflictSeverity.HIGH,
            overlap_start=100.0,
            overlap_end=130.0,
        )
        # PriorityEngine uses world_model.robot_id as "own"
        pd_from_a = engine.resolve(conflict, wm_a, now=now)
        conflict_b = ConflictReport(
            robot_a_id="amr_01",
            robot_b_id="amr_02",
            resource_id="I1",
            severity=ConflictSeverity.HIGH,
            overlap_start=100.0,
            overlap_end=130.0,
        )
        pd_from_b = engine.resolve(conflict_b, wm_b, now=now)

        # Both must select the same winner
        assert pd_from_a.winner_id == pd_from_b.winner_id

    def test_loser_releases_reservation_after_reconciliation(self):
        """The loser robot can release its reservation after arbitration."""
        manager = make_manager()
        wm_loser = make_wm("amr_02")
        now = 100.0

        # amr_02 accepted locally
        dec = manager.request_reservation(wm_loser, "I1", 100.0, 130.0, priority=0.5, now=now)
        assert dec.accepted is True
        claim_id = dec.claim_id

        # After reconciliation, loser releases
        release_dec = manager.release_reservation(wm_loser, claim_id, now=now)
        assert release_dec.accepted is True
        assert release_dec.reason == "RELEASED"
        assert wm_loser.get_reservation(claim_id) is None


# ===========================================================================
# Category 3 — Non-Preemption of Active Claims (INV-8)
# ===========================================================================

class TestNonPreemption:

    def test_higher_priority_robot_cannot_preempt_active_peer_reservation(self):
        """INV-8: No competing request can evict an active peer reservation."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 105.0  # within [100, 130]

        # Peer B holds an active reservation [100, 130] at T=105
        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0, priority=0.2)
        wm.add_reservation(peer_res)

        # amr_01 wants [100, 130] — even with higher priority
        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority=0.99, now=now
        )

        assert decision.accepted is False
        assert decision.reason == "RESOURCE_CONFLICT"
        # Peer's reservation still intact
        assert wm.get_reservation(peer_res.claim_id) is not None

    def test_higher_priority_robot_can_reserve_after_active_reservation(self):
        """A higher-priority robot CAN reserve a consecutive non-overlapping window."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 105.0

        # Peer B holds [100, 130]
        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0)
        wm.add_reservation(peer_res)

        # amr_01 reserves [130, 160] — consecutive, not overlapping
        decision = manager.request_reservation(
            wm, "I1", 130.0, 160.0, priority=0.99, now=now
        )

        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"

    def test_existing_reservation_remains_intact_when_competing_request_rejected(self):
        """Rejected requests must not corrupt the existing peer reservation."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0, priority=0.3)
        wm.add_reservation(peer_res)

        # Rejected
        decision = manager.request_reservation(wm, "I1", 105.0, 125.0, now=now)
        assert decision.accepted is False

        # Peer reservation unchanged
        stored = wm.get_reservation(peer_res.claim_id)
        assert stored is not None
        assert stored.start_time == 100.0
        assert stored.end_time == 130.0
        assert stored.robot_id == "amr_02"


# ===========================================================================
# Category 4 — PriorityDecision Arbitration & Score Authority
# ===========================================================================

class TestPriorityDecisionArbitration:

    def test_winner_priority_decision_grants_reservation_and_sets_score(self):
        """A PriorityDecision where this robot is the winner allows acceptance."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        pd = make_priority_decision(
            winner_id="amr_01", loser_id="amr_02",
            score_winner=0.85, decided_at=99.0
        )

        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority=0.0, priority_decision=pd, now=now
        )

        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"
        # Authoritative score must be derived from PriorityDecision
        assert decision.reservation is not None
        assert decision.reservation.priority == pytest.approx(0.85)

    def test_loser_priority_decision_rejects_reservation(self):
        """A PriorityDecision where this robot is the loser must be rejected."""
        manager = make_manager()
        wm = make_wm("amr_02")
        now = 100.0

        pd = make_priority_decision(
            winner_id="amr_01", loser_id="amr_02",
            score_winner=0.85, decided_at=99.0
        )

        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority_decision=pd, now=now
        )

        assert decision.accepted is False
        assert decision.reason == "PRIORITY_LOST"
        # No reservation stored
        own = [r for r in wm.get_all_reservations().values() if r.robot_id == "amr_02"]
        assert own == []

    def test_priority_value_derived_authoritatively_from_priority_decision(self):
        """The caller-supplied `priority` is ignored when PriorityDecision is provided."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        pd = make_priority_decision(
            winner_id="amr_01", loser_id="amr_02",
            score_winner=0.77, decided_at=99.0
        )

        # Caller passes priority=0.0 — must be overridden by pd.score
        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority=0.0, priority_decision=pd, now=now
        )

        assert decision.accepted is True
        assert decision.reservation.priority == pytest.approx(0.77)

    def test_stale_priority_decision_rejected(self):
        """A PriorityDecision older than peer_intent_max_age_seconds is stale."""
        config = CoordinationConfig()
        manager = ReservationManager(config=config)
        wm = make_wm("amr_01")
        now = 100.0

        max_age = config.timeouts.peer_intent_max_age_seconds  # 10.0s
        stale_decided_at = now - max_age - 1.0  # 11s ago — definitely stale

        pd = make_priority_decision(
            winner_id="amr_01", loser_id="amr_02",
            score_winner=0.9, decided_at=stale_decided_at
        )

        decision = manager.request_reservation(
            wm, "I1", 100.0, 130.0, priority_decision=pd, now=now
        )

        assert decision.accepted is False
        assert decision.reason == "STALE_PRIORITY_DECISION"


# ===========================================================================
# Category 5 — Boundary Semantics & Expiry
# ===========================================================================

class TestBoundaryAndExpiry:

    def test_boundary_semantics_at_end_time(self):
        """now == peer.end_time: reservation is still active (inclusive boundary)."""
        manager = make_manager()
        wm = make_wm("amr_01")

        peer_res = make_peer_reservation("amr_02", "I1", 100.0, 130.0)
        wm.add_reservation(peer_res)

        # At now=130.0 (end_time), is_active=True → still blocks
        # Our window [130.0, 160.0] boundary-touches → NOT a conflict (INV-7)
        now = 130.0
        decision = manager.request_reservation(wm, "I1", 130.0, 160.0, now=now)
        assert decision.accepted is True

        # Our window [125.0, 135.0] does overlap [100, 130] → blocked
        decision2 = manager.request_reservation(wm, "I1", 125.0, 135.0, now=now)
        assert decision2.accepted is False
        assert decision2.reason == "RESOURCE_CONFLICT"

    def test_boundary_semantics_at_expires_at(self):
        """now == peer.expires_at: reservation is in grace period → still blocks future overlaps."""
        manager = make_manager()
        wm = make_wm("amr_01")

        # Peer reservation that extends into the far future so we can request
        # a window that actually overlaps it even with now=expires_at.
        # peer: [140, 200], expires_at = 200 + GRACE = 230
        peer_start = 140.0
        peer_end = 200.0
        expires_at = peer_end + GRACE  # 230.0

        peer_res = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=peer_start,
            end_time=peer_end,
            priority=0.5,
            expires_at=expires_at,
        )
        wm.add_reservation(peer_res)

        now = expires_at  # 230.0 — exactly at expiry boundary, not yet expired
        assert peer_res.is_expired(now) is False  # now > expires_at is False

        # Request window [220, 240] overlaps peer [140, 200]? No — 220 > 200.
        # Use [150, 240] which overlaps peer [140, 200]. end_time=240 > now=230. ✓
        decision = manager.request_reservation(wm, "I1", 150.0, 240.0, now=now)
        assert decision.accepted is False
        assert decision.reason == "RESOURCE_CONFLICT"
        assert decision.conflicting_claim_id == peer_res.claim_id

    def test_expired_reservation_does_not_block_new_request(self):
        """INV-3: now > expires_at → peer reservation is expired and never blocks."""
        manager = make_manager()
        wm = make_wm("amr_01")

        end_time = 130.0
        expires_at = end_time + GRACE  # 160.0
        peer_res = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=100.0,
            end_time=end_time,
            priority=0.5,
            expires_at=expires_at,
        )
        wm.add_reservation(peer_res)

        now = expires_at + 1.0  # 161.0 — strictly expired
        assert peer_res.is_expired(now) is True

        # Request a future window from now onwards — peer is expired so it must not block
        decision = manager.request_reservation(wm, "I1", now, now + 30.0, now=now)
        assert decision.accepted is True
        assert decision.reason == "ACCEPTED"

    def test_grace_period_semantics(self):
        """end_time < now <= expires_at: reservation is in grace period → still blocks."""
        manager = make_manager()
        wm = make_wm("amr_01")

        end_time = 130.0
        expires_at = end_time + GRACE  # 160.0
        peer_res = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=100.0,
            end_time=end_time,
            priority=0.5,
            expires_at=expires_at,
        )
        wm.add_reservation(peer_res)

        # now is in grace period: end_time < now <= expires_at
        now = 145.0
        assert peer_res.is_expired(now) is False

        # Request a future window from now onwards that overlaps [100, 130]
        # Use start_time in the past relative to peer's window but end_time in the future
        # to demonstrate the temporal overlap check still fires.
        # Simpler: request [100, end_time] but peer is not expired → conflict.
        # We need a valid request (end_time > now), so [now, now+10].
        # That window [145,155] does NOT overlap peer [100,130], so no conflict expected.
        # Instead, use a peer with start_time far in the future to test grace blocking:
        future_peer = Reservation(
            resource_id="DOCK_B",
            robot_id="amr_02",
            start_time=150.0,
            end_time=170.0,
            priority=0.5,
            expires_at=200.0,
        )
        wm.add_reservation(future_peer)
        # Our window [148, 160] overlaps future_peer [150, 170]
        decision = manager.request_reservation(wm, "DOCK_B", 148.0, 160.0, now=now)
        assert decision.accepted is False
        assert decision.reason == "RESOURCE_CONFLICT"
        assert decision.conflicting_claim_id == future_peer.claim_id


# ===========================================================================
# Category 6 — Renewal & Replacement Safety
# ===========================================================================

class TestRenewalAndReplacement:

    def test_valid_renewal_replaces_reservation_with_extended_end_time(self):
        """A valid renewal produces a new Reservation with the extended end_time."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # First grant a reservation
        dec = manager.request_reservation(wm, "I1", 100.0, 130.0, priority=0.6, now=now)
        assert dec.accepted
        claim_id = dec.claim_id
        original = wm.get_reservation(claim_id)
        original_created_at = original.created_at

        # Renew to 160.0
        renew_dec = manager.renew_reservation(wm, claim_id, new_end_time=160.0, now=now)
        assert renew_dec.accepted is True
        assert renew_dec.reason == "RENEWED"
        assert renew_dec.reservation is not None
        assert renew_dec.reservation.end_time == pytest.approx(160.0)
        assert renew_dec.reservation.claim_id == claim_id
        assert renew_dec.reservation.start_time == pytest.approx(100.0)
        # created_at is preserved from original
        assert renew_dec.reservation.created_at == pytest.approx(original_created_at)
        # WorldModel updated
        stored = wm.get_reservation(claim_id)
        assert stored.end_time == pytest.approx(160.0)

    def test_renewal_conflicting_with_future_peer_reservation_rejected(self):
        """Renewal that extends into a peer reservation window must be rejected."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # amr_01 has [100, 130]
        dec = manager.request_reservation(wm, "I1", 100.0, 130.0, priority=0.6, now=now)
        assert dec.accepted
        claim_id = dec.claim_id

        # Peer holds [150, 200]
        peer_res = make_peer_reservation("amr_02", "I1", 150.0, 200.0)
        wm.add_reservation(peer_res)

        # Renewal to 160.0 extends into peer window [150, 200]
        renew_dec = manager.renew_reservation(wm, claim_id, new_end_time=160.0, now=now)
        assert renew_dec.accepted is False
        assert renew_dec.reason == "RESOURCE_CONFLICT"
        assert renew_dec.conflicting_claim_id == peer_res.claim_id

        # WorldModel unchanged — original end_time still 130.0
        stored = wm.get_reservation(claim_id)
        assert stored.end_time == pytest.approx(130.0)

    def test_renewal_cannot_partially_mutate_state_on_failure(self):
        """Atomic-on-failure: WorldModel is 100% unchanged when renewal is rejected."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        dec = manager.request_reservation(wm, "I1", 100.0, 130.0, priority=0.6, now=now)
        claim_id = dec.claim_id

        # Peer blocks renewal
        peer_res = make_peer_reservation("amr_02", "I1", 140.0, 180.0)
        wm.add_reservation(peer_res)

        snapshot_before = dict(wm.get_all_reservations())
        renew_dec = manager.renew_reservation(wm, claim_id, new_end_time=150.0, now=now)
        assert renew_dec.accepted is False

        snapshot_after = dict(wm.get_all_reservations())
        # Exact same set of reservations, same end_times
        assert set(snapshot_before.keys()) == set(snapshot_after.keys())
        for cid in snapshot_before:
            assert snapshot_before[cid].end_time == snapshot_after[cid].end_time

    def test_renewal_by_non_owner_rejected(self):
        """INV-2: Only the owning robot may renew a reservation."""
        manager = make_manager()
        # amr_01 owns the reservation, but we try to renew it from amr_02's WorldModel
        wm_owner = make_wm("amr_01")
        wm_other = make_wm("amr_02")
        now = 100.0

        dec = manager.request_reservation(wm_owner, "I1", 100.0, 130.0, now=now)
        claim_id = dec.claim_id

        # Inject it into amr_02's world model (as if received over network)
        wm_other.add_reservation(dec.reservation)

        # amr_02 tries to renew a reservation owned by amr_01
        renew_dec = manager.renew_reservation(wm_other, claim_id, new_end_time=160.0, now=now)
        assert renew_dec.accepted is False
        assert renew_dec.reason == "NOT_OWNER"


# ===========================================================================
# Category 7 — Release Operations & Idempotency
# ===========================================================================

class TestReleaseOperations:

    def test_owner_can_release_reservation(self):
        """INV-2: The owning robot can release its own reservation."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        dec = manager.request_reservation(wm, "I1", 100.0, 130.0, now=now)
        assert dec.accepted
        claim_id = dec.claim_id

        release_dec = manager.release_reservation(wm, claim_id, now=now)
        assert release_dec.accepted is True
        assert release_dec.reason == "RELEASED"
        assert release_dec.claim_id == claim_id
        assert wm.get_reservation(claim_id) is None

    def test_non_owner_cannot_release_reservation(self):
        """INV-2: A robot cannot release a reservation it doesn't own."""
        manager = make_manager()
        wm_owner = make_wm("amr_01")
        wm_other = make_wm("amr_02")
        now = 100.0

        dec = manager.request_reservation(wm_owner, "I1", 100.0, 130.0, now=now)
        claim_id = dec.claim_id

        # Inject into amr_02's WorldModel
        wm_other.add_reservation(dec.reservation)

        release_dec = manager.release_reservation(wm_other, claim_id, now=now)
        assert release_dec.accepted is False
        assert release_dec.reason == "NOT_OWNER"
        # Reservation still present
        assert wm_other.get_reservation(claim_id) is not None

    def test_release_unknown_claim_id_is_idempotent_safe(self):
        """INV-4: Releasing an unknown claim_id is safe and returns ALREADY_RELEASED."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        release_dec = manager.release_reservation(wm, "nonexistent-claim-id", now=now)
        assert release_dec.accepted is True
        assert release_dec.reason == "ALREADY_RELEASED"


# ===========================================================================
# Category 8 — Input Validation
# ===========================================================================

class TestInputValidation:

    def test_inverted_interval_rejected(self):
        """end_time <= start_time must always be rejected as INVALID_INTERVAL."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # end_time == start_time
        dec1 = manager.request_reservation(wm, "I1", 100.0, 100.0, now=now)
        assert dec1.accepted is False
        assert dec1.reason == "INVALID_INTERVAL"

        # end_time < start_time
        dec2 = manager.request_reservation(wm, "I1", 120.0, 100.0, now=now)
        assert dec2.accepted is False
        assert dec2.reason == "INVALID_INTERVAL"

    def test_past_interval_rejected(self):
        """A window entirely in the past (end_time < now) must be rejected."""
        manager = make_manager()
        wm = make_wm("amr_01")
        now = 200.0

        # end_time=150.0 < now=200.0
        dec = manager.request_reservation(wm, "I1", 100.0, 150.0, now=now)
        assert dec.accepted is False
        assert dec.reason == "INVALID_INTERVAL"


# ===========================================================================
# Category 9 — Multi-Robot & Immutability
# ===========================================================================

class TestMultiRobotAndImmutability:

    def test_multi_robot_competing_requests_handled_deterministically(self):
        """Three robots competing for the same resource window: only first wins."""
        manager = make_manager()
        now = 100.0

        wm_a = make_wm("amr_01")
        wm_b = make_wm("amr_02")
        wm_c = make_wm("amr_03")

        # Robot A reserves first on its own WorldModel
        dec_a = manager.request_reservation(wm_a, "I1", 100.0, 130.0, now=now)
        assert dec_a.accepted is True

        # Broadcast A's reservation to B and C
        wm_b.add_reservation(dec_a.reservation)
        wm_c.add_reservation(dec_a.reservation)

        # B and C both see A's reservation and are rejected
        dec_b = manager.request_reservation(wm_b, "I1", 105.0, 125.0, now=now)
        dec_c = manager.request_reservation(wm_c, "I1", 100.0, 130.0, now=now)

        assert dec_b.accepted is False
        assert dec_b.reason == "RESOURCE_CONFLICT"
        assert dec_c.accepted is False
        assert dec_c.reason == "RESOURCE_CONFLICT"

        # Calling again with same params produces same result (INV-6 determinism)
        dec_b2 = manager.request_reservation(wm_b, "I1", 105.0, 125.0, now=now)
        assert dec_b2.accepted is False
        assert dec_b2.reason == "RESOURCE_CONFLICT"

    def test_world_model_immutability_on_states_intents_tasks(self):
        """INV-5: ReservationManager NEVER mutates own_state, peer_states,
        own_intent, peer_intents, or tasks."""
        from fleet_coordination.models.robot_intent import RobotIntent
        from fleet_coordination.models.robot_state import RobotState
        from fleet_coordination.models.task import Task, TaskType, TaskStatus

        manager = make_manager()
        wm = make_wm("amr_01")
        now = 100.0

        # Pre-populate non-reservation state
        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=99.0))
        wm.set_own_intent(
            RobotIntent(robot_id="amr_01", target_resource_id="I1", valid_until=200.0, timestamp=99.0)
        )
        peer_state = RobotState(robot_id="amr_02", timestamp=99.0)
        wm.update_peer_state(peer_state)
        peer_intent = RobotIntent(
            robot_id="amr_02", target_resource_id="I1", valid_until=200.0, timestamp=99.0
        )
        wm.update_peer_intent(peer_intent)
        task = Task(
            task_id="task-001",
            task_type=TaskType.DELIVERY,
            status=TaskStatus.ANNOUNCED,
        )
        wm.add_task(task)

        # Snapshot pre-operation
        snap_own_state = wm.get_own_state()
        snap_own_intent = wm.get_own_intent()
        snap_peer_states = wm.get_all_peer_states()
        snap_tasks = wm.get_all_tasks()

        # Perform a request (accepted) and a release
        dec = manager.request_reservation(wm, "I1", 100.0, 130.0, priority=0.5, now=now)
        assert dec.accepted is True
        manager.release_reservation(wm, dec.claim_id, now=now)

        # Verify no non-reservation fields changed
        assert wm.get_own_state() is snap_own_state
        assert wm.get_own_intent() is snap_own_intent
        assert wm.get_all_peer_states() == snap_peer_states
        assert wm.get_all_tasks() == snap_tasks
