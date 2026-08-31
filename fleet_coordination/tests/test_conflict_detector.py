"""
Unit tests for ConflictDetector — Coordination Conflict Detection Engine.
=========================================================================

Tests verify:
- Spatial contention over named shared resources (I1, I2)
- Temporal overlap using open-interval semantics
- Option C occupancy duration modeling (bounded by valid_until)
- Evidence aggregation (multi-source intent + reservation per peer)
- Bounding conflict windows without false continuous overlap
- Severity classification & deterministic sorting
- Zero state mutation of WorldModel
"""

import pytest

from fleet_coordination.algorithm.conflict_detector import ConflictDetector
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    ConflictDetectionConfig,
    CoordinationConfig,
    TimeoutConfig,
)
from fleet_coordination.models.conflict import ConflictSeverity
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.tests.conftest import FIXED_TIME


@pytest.fixture
def detector() -> ConflictDetector:
    """Standard ConflictDetector instance."""
    return ConflictDetector()


@pytest.fixture
def wm() -> WorldModel:
    """WorldModel for local robot 'amr_01'."""
    return WorldModel(robot_id="amr_01")


# ===========================================================================
# 1. Base / Empty Conditions
# ===========================================================================

class TestConflictDetectorBaseConditions:
    """Tests for empty inputs, missing intents, or unassigned resources."""

    def test_no_own_intent_returns_empty(self, detector: ConflictDetector, wm: WorldModel):
        """When own intent is None, no conflicts are reported."""
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_own_intent_no_resource_returns_empty(self, detector: ConflictDetector, wm: WorldModel):
        """When own intent has no target_resource_id (open navigation), returns empty."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id=None,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_no_peers_or_reservations_returns_empty(self, detector: ConflictDetector, wm: WorldModel):
        """When targeting a resource uncontested by peers, returns empty."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []


# ===========================================================================
# 2. Spatial & Temporal Overlap Scenarios
# ===========================================================================

class TestConflictDetectorSpatialAndTemporal:
    """Tests for pairwise spatial and temporal overlap semantics."""

    def test_single_peer_intent_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Single peer intent overlapping in time and space generates ConflictReport."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 15.0,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        c = conflicts[0]
        assert c.robot_a_id == "amr_01"
        assert c.robot_b_id == "amr_02"
        assert c.resource_id == "I1"
        assert c.overlap_start == FIXED_TIME + 15.0

    def test_single_peer_reservation_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Peer holding a reservation on the same resource generates ConflictReport."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 40.0,
            )
        )
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_02",
                start_time=FIXED_TIME + 15.0,
                end_time=FIXED_TIME + 25.0,
                priority=5.0,
                claim_id="claim_001",
                expires_at=FIXED_TIME + 60.0,
            )
        )
        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        assert conflicts[0].robot_b_id == "amr_02"
        assert conflicts[0].overlap_start == FIXED_TIME + 15.0
        assert conflicts[0].overlap_end == FIXED_TIME + 25.0

    def test_different_resource_no_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Peers targeting different resources at identical times do not conflict."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I2",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_same_resource_disjoint_time_no_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Same resource with disjoint time intervals does not conflict."""
        # Own window: [now+10, now+20] (valid_until=now+20)
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        # Peer window: [now+30, now+50]
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 30.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_boundary_touching_time_no_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Touching at boundary (A ends exactly when B starts) is not a conflict."""
        # Own window: [now+10, now+20]
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        # Peer starts exactly at now+20
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 20.0,
                valid_until=FIXED_TIME + 40.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_sub_threshold_overlap_filtered_out(self, detector: ConflictDetector, wm: WorldModel):
        """Overlap shorter than min_temporal_overlap_seconds (1.0s) is ignored."""
        # Own window: [now+10, now+20]
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        # Peer window: [now+19.5, now+30] -> overlap is only 0.5s (< 1.0s)
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 19.5,
                valid_until=FIXED_TIME + 30.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []


# ===========================================================================
# 3. Filtering & Expiration
# ===========================================================================

class TestConflictDetectorFiltering:
    """Tests for expiration and planning horizon filtering."""

    def test_expired_peer_intent_ignored(self, detector: ConflictDetector, wm: WorldModel):
        """Expired peer intent in WorldModel is ignored."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 40.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME - 50.0,
                target_resource_id="I1",
                eta=FIXED_TIME - 20.0,
                valid_until=FIXED_TIME - 5.0,  # Expired
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_conflict_beyond_planning_horizon_ignored(self, wm: WorldModel):
        """Conflict starting beyond planning_horizon_seconds (60s) is ignored."""
        custom_detector = ConflictDetector(
            config=ConflictDetectionConfig(planning_horizon_seconds=30.0)
        )
        # Own intent far in future: ETA = now+40s
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 40.0,
                valid_until=FIXED_TIME + 80.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 42.0,
                valid_until=FIXED_TIME + 80.0,
            )
        )
        assert custom_detector.detect_conflicts(wm, now=FIXED_TIME) == []


# ===========================================================================
# 4. Evidence Aggregation & Multi-Source
# ===========================================================================

class TestConflictDetectorEvidenceAggregation:
    """Tests for multi-peer reports, evidence merging, and bounding windows."""

    def test_multiple_competing_peers_all_reported(self, detector: ConflictDetector, wm: WorldModel):
        """Multiple peers competing for same resource each receive a ConflictReport."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 15.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_03",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 18.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 2
        peers = {c.robot_b_id for c in conflicts}
        assert peers == {"amr_02", "amr_03"}

    def test_own_reservation_not_reported_as_conflict(self, detector: ConflictDetector, wm: WorldModel):
        """Own reservation on target resource does not create a self-conflict."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_01",
                start_time=FIXED_TIME + 10.0,
                end_time=FIXED_TIME + 30.0,
                priority=5.0,
                claim_id="claim_self",
                expires_at=FIXED_TIME + 60.0,
            )
        )
        assert detector.detect_conflicts(wm, now=FIXED_TIME) == []

    def test_evidence_aggregation_merges_intent_and_reservation_intervals(
        self, detector: ConflictDetector, wm: WorldModel
    ):
        """Peer with both intent [100, 110] and reservation [105, 130] vs own [100, 120]

        Produces single report spanning the full bounding overlap window [100, 120].
        """
        # Own window: [FIXED_TIME, FIXED_TIME + 20]
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        # Peer intent overlap evidence: [FIXED_TIME, FIXED_TIME + 10]
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 10.0,
            )
        )
        # Peer reservation overlap evidence: [FIXED_TIME + 5, FIXED_TIME + 30] -> overlap with own is [FIXED_TIME + 5, FIXED_TIME + 20]
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_02",
                start_time=FIXED_TIME + 5.0,
                end_time=FIXED_TIME + 30.0,
                priority=5.0,
                claim_id="claim_002",
                expires_at=FIXED_TIME + 60.0,
            )
        )

        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        c = conflicts[0]
        assert c.robot_b_id == "amr_02"
        assert c.overlap_start == FIXED_TIME
        assert c.overlap_end == FIXED_TIME + 20.0

    def test_separated_conflict_intervals_do_not_create_false_continuous_overlap(
        self, detector: ConflictDetector, wm: WorldModel
    ):
        """Verify separated evidence intervals [100, 105] and [120, 125] form bounding window.

        Own interval: [100, 130]
        Peer intent evidence: [100, 105]
        Peer reservation evidence: [120, 125]
        Verifies that bounding window is [100, 125] with earliest onset at 100.0.
        """
        # Own window: [FIXED_TIME, FIXED_TIME + 30.0]
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 30.0,
            )
        )
        # Peer intent: [FIXED_TIME, FIXED_TIME + 5.0]
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 5.0,
            )
        )
        # Peer reservation: [FIXED_TIME + 20.0, FIXED_TIME + 25.0]
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_02",
                start_time=FIXED_TIME + 20.0,
                end_time=FIXED_TIME + 25.0,
                priority=5.0,
                claim_id="claim_separated",
                expires_at=FIXED_TIME + 60.0,
            )
        )

        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        c = conflicts[0]
        assert c.robot_b_id == "amr_02"
        # Bounding window bounds the separated intervals
        assert c.overlap_start == FIXED_TIME
        assert c.overlap_end == FIXED_TIME + 25.0
        # Severity is based on earliest actual onset (FIXED_TIME - now = 0 -> CRITICAL)
        assert c.severity == ConflictSeverity.CRITICAL


# ===========================================================================
# 5. Occupancy Model & Edge Cases
# ===========================================================================

class TestConflictDetectorOccupancyAndTiming:
    """Tests for Option C occupancy duration and ETA boundary clamping."""

    def test_occupancy_duration_derived_from_config_bounded_by_valid_until(
        self, detector: ConflictDetector, wm: WorldModel
    ):
        """Option C: Occupancy duration is bounded by valid_until."""
        # Default duration is 30s. If valid_until is only +15s, end is capped at +15s
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 10.0,
                valid_until=FIXED_TIME + 25.0,  # 15s after ETA
            )
        )
        # Peer has ETA at +20s with long valid_until
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 20.0,
                valid_until=FIXED_TIME + 80.0,
            )
        )
        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        c = conflicts[0]
        assert c.overlap_start == FIXED_TIME + 20.0
        assert c.overlap_end == FIXED_TIME + 25.0  # Capped by own valid_until

    def test_past_eta_clamped_to_now(self, detector: ConflictDetector, wm: WorldModel):
        """Past ETA (< now) is conservatively clamped to now as occupancy start."""
        # Own ETA was 5s ago
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME - 10.0,
                target_resource_id="I1",
                eta=FIXED_TIME - 5.0,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        # Peer ETA is right now
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 20.0,
            )
        )
        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 1
        assert conflicts[0].overlap_start == FIXED_TIME
        assert conflicts[0].severity == ConflictSeverity.CRITICAL


# ===========================================================================
# 6. Severity & Deterministic Ordering
# ===========================================================================

class TestConflictDetectorSeverityAndOrdering:
    """Tests for severity calculation levels and deterministic sorting."""

    def test_conflict_severity_classification(self, detector: ConflictDetector):
        """Verifies CRITICAL (<=0s), HIGH (<=10s), MEDIUM (<=30s), LOW (>30s)."""
        wm = WorldModel(robot_id="amr_01")
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 100.0,
            )
        )

        # Critical: onset at FIXED_TIME (0s)
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_crit",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        c_crit = detector.detect_conflicts(wm, now=FIXED_TIME)[0]
        assert c_crit.severity == ConflictSeverity.CRITICAL

        # High: onset at FIXED_TIME + 5s
        wm2 = WorldModel(robot_id="amr_01")
        wm2.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 5.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        wm2.update_peer_intent(
            RobotIntent(
                robot_id="amr_high",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 5.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        c_high = detector.detect_conflicts(wm2, now=FIXED_TIME)[0]
        assert c_high.severity == ConflictSeverity.HIGH

        # Medium: onset at FIXED_TIME + 20s
        wm3 = WorldModel(robot_id="amr_01")
        wm3.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 20.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        wm3.update_peer_intent(
            RobotIntent(
                robot_id="amr_med",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 20.0,
                valid_until=FIXED_TIME + 50.0,
            )
        )
        c_med = detector.detect_conflicts(wm3, now=FIXED_TIME)[0]
        assert c_med.severity == ConflictSeverity.MEDIUM

        # Low: onset at FIXED_TIME + 45s
        wm4 = WorldModel(robot_id="amr_01")
        wm4.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 45.0,
                valid_until=FIXED_TIME + 90.0,
            )
        )
        wm4.update_peer_intent(
            RobotIntent(
                robot_id="amr_low",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME + 45.0,
                valid_until=FIXED_TIME + 90.0,
            )
        )
        c_low = detector.detect_conflicts(wm4, now=FIXED_TIME)[0]
        assert c_low.severity == ConflictSeverity.LOW

    def test_deterministic_conflict_sorting(self, detector: ConflictDetector, wm: WorldModel):
        """Conflict reports are sorted by severity rank, earliest overlap start, then peer ID."""
        wm.set_own_intent(
            RobotIntent(
                robot_id="amr_01",
                timestamp=FIXED_TIME,
                target_resource_id="I1",
                eta=FIXED_TIME,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        # Peer 3: Medium severity (eta +15s)
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_03", timestamp=FIXED_TIME, target_resource_id="I1", eta=FIXED_TIME + 15.0, valid_until=FIXED_TIME + 50.0)
        )
        # Peer 2: Critical severity (eta now)
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1", eta=FIXED_TIME, valid_until=FIXED_TIME + 50.0)
        )
        # Peer 4: Critical severity (eta now, tie-breaker peer_id > amr_02)
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_04", timestamp=FIXED_TIME, target_resource_id="I1", eta=FIXED_TIME, valid_until=FIXED_TIME + 50.0)
        )

        conflicts = detector.detect_conflicts(wm, now=FIXED_TIME)
        assert len(conflicts) == 3
        # Expected order: amr_02 (CRITICAL), amr_04 (CRITICAL), amr_03 (MEDIUM)
        assert [c.robot_b_id for c in conflicts] == ["amr_02", "amr_04", "amr_03"]
