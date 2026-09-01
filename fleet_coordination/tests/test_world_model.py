"""
Unit tests for WorldModel — Local Fleet State Store.
====================================================

Tests verify:
- Local state & intent storage (isolated from peer records)
- Monotonic timestamp ordering for peer updates
- Query-time filtering for freshness and expiration
- Deterministic behavior with fixed timestamps
- Garbage collection independence (INV-5)
- All 7 core architectural invariants
"""

import pytest

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    TimeoutConfig,
)
from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task, TaskStatus, TaskType
from fleet_coordination.tests.conftest import FIXED_TIME


@pytest.fixture
def wm() -> WorldModel:
    """Standard WorldModel instance for local robot 'amr_01'."""
    return WorldModel(robot_id="amr_01")


@pytest.fixture
def custom_wm() -> WorldModel:
    """WorldModel with tight 2.0s peer timeout for freshness testing."""
    config = CoordinationConfig(
        timeouts=TimeoutConfig(
            peer_state_max_age_seconds=2.0,
            peer_intent_max_age_seconds=5.0,
        )
    )
    return WorldModel(robot_id="amr_01", config=config)


# ===========================================================================
# Group 1: Own State & Own Intent
# ===========================================================================

class TestWorldModelOwnStateAndIntent:
    """Tests for local robot's own state and intent management."""

    def test_own_state_initially_none(self, wm: WorldModel):
        """Own state must be None upon initialization."""
        assert wm.get_own_state() is None

    def test_set_and_get_own_state(self, wm: WorldModel):
        """Setting valid own state stores and retrieves correctly."""
        state = RobotState(
            robot_id="amr_01",
            timestamp=FIXED_TIME,
            pose=Pose2D(1.0, 2.0, 0.0),
            status=RobotStatus.NAVIGATING,
        )
        wm.set_own_state(state)
        assert wm.get_own_state() == state

    def test_set_own_state_mismatched_id_raises_error(self, wm: WorldModel):
        """Setting own state with another robot's ID must raise ValueError."""
        state = RobotState(robot_id="amr_02", timestamp=FIXED_TIME)
        with pytest.raises(ValueError, match="mismatched ID"):
            wm.set_own_state(state)

    def test_set_own_state_empty_id_raises_error(self, wm: WorldModel):
        """Setting own state with empty ID must raise ValueError."""
        state = RobotState(robot_id="", timestamp=FIXED_TIME)
        with pytest.raises(ValueError, match="empty"):
            wm.set_own_state(state)

    def test_own_intent_initially_none(self, wm: WorldModel):
        """Own intent must be None upon initialization."""
        assert wm.get_own_intent() is None

    def test_set_and_get_own_intent(self, wm: WorldModel):
        """Setting valid own intent stores and retrieves correctly."""
        intent = RobotIntent(
            robot_id="amr_01",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 60.0,
        )
        wm.set_own_intent(intent)
        assert wm.get_own_intent() == intent

    def test_set_own_intent_mismatched_id_raises_error(self, wm: WorldModel):
        """Setting own intent with another robot's ID must raise ValueError."""
        intent = RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME)
        with pytest.raises(ValueError, match="mismatched ID"):
            wm.set_own_intent(intent)

    def test_own_intent_isolated_from_peer_intents(self, wm: WorldModel):
        """Own intent must NEVER appear in peer intent queries (INV-4)."""
        intent = RobotIntent(
            robot_id="amr_01",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 60.0,
        )
        wm.set_own_intent(intent)
        active_peers = wm.get_active_peer_intents(now=FIXED_TIME)
        assert "amr_01" not in active_peers
        assert len(active_peers) == 0
        assert len(wm.get_intents_for_resource("I1", now=FIXED_TIME)) == 0


# ===========================================================================
# Group 2: Peer State Management & Monotonicity
# ===========================================================================

class TestWorldModelPeerState:
    """Tests for tracking peer robot states and timestamp monotonicity."""

    def test_update_and_get_peer_state(self, wm: WorldModel):
        """First peer observation is accepted and retrievable."""
        peer = RobotState(robot_id="amr_02", timestamp=FIXED_TIME)
        accepted = wm.update_peer_state(peer)
        assert accepted is True
        assert wm.get_peer_state("amr_02") == peer
        assert wm.get_peer_count() == 1
        assert wm.get_known_peer_ids() == {"amr_02"}

    def test_get_all_peer_states_returns_shallow_copy(self, wm: WorldModel):
        """get_all_peer_states returns a copy that does not mutate internal storage."""
        peer = RobotState(robot_id="amr_02", timestamp=FIXED_TIME)
        wm.update_peer_state(peer)
        states = wm.get_all_peer_states()
        states["amr_fake"] = RobotState(robot_id="amr_fake", timestamp=FIXED_TIME)
        assert "amr_fake" not in wm.get_all_peer_states()

    def test_peer_state_freshness_evaluation(self, custom_wm: WorldModel):
        """Peer state within max age is recognized as fresh."""
        peer = RobotState(robot_id="amr_02", timestamp=FIXED_TIME)
        custom_wm.update_peer_state(peer)
        # Timeout is 2.0s; check at FIXED_TIME + 1.5s
        assert custom_wm.is_peer_state_fresh("amr_02", now=FIXED_TIME + 1.5) is True
        fresh = custom_wm.get_fresh_peer_states(now=FIXED_TIME + 1.5)
        assert "amr_02" in fresh

    def test_peer_state_staleness_evaluation(self, custom_wm: WorldModel):
        """Peer state older than max age is recognized as stale."""
        peer = RobotState(robot_id="amr_02", timestamp=FIXED_TIME)
        custom_wm.update_peer_state(peer)
        # Timeout is 2.0s; check at FIXED_TIME + 2.5s
        assert custom_wm.is_peer_state_fresh("amr_02", now=FIXED_TIME + 2.5) is False
        fresh = custom_wm.get_fresh_peer_states(now=FIXED_TIME + 2.5)
        assert "amr_02" not in fresh

    def test_reject_older_peer_state_update(self, wm: WorldModel):
        """INV-1: Out-of-order update with older timestamp is rejected."""
        newer = RobotState(
            robot_id="amr_02",
            timestamp=FIXED_TIME + 10.0,
            pose=Pose2D(10.0, 10.0),
        )
        older = RobotState(
            robot_id="amr_02",
            timestamp=FIXED_TIME + 5.0,
            pose=Pose2D(5.0, 5.0),
        )
        assert wm.update_peer_state(newer) is True
        assert wm.update_peer_state(older) is False
        # Stored state must remain the newer one
        stored = wm.get_peer_state("amr_02")
        assert stored is not None
        assert stored.timestamp == FIXED_TIME + 10.0
        assert stored.pose.x == 10.0

    def test_reject_equal_timestamp_peer_state_update(self, wm: WorldModel):
        """Equal timestamp update is rejected as non-newer (monotonicity)."""
        first = RobotState(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            pose=Pose2D(1.0, 1.0),
        )
        duplicate = RobotState(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            pose=Pose2D(2.0, 2.0),
        )
        assert wm.update_peer_state(first) is True
        assert wm.update_peer_state(duplicate) is False
        stored = wm.get_peer_state("amr_02")
        assert stored is not None
        assert stored.pose.x == 1.0

    def test_reject_self_robot_id_in_peer_state_update(self, wm: WorldModel):
        """INV-4: Peer update containing own robot ID is rejected."""
        self_state = RobotState(robot_id="amr_01", timestamp=FIXED_TIME)
        assert wm.update_peer_state(self_state) is False
        assert "amr_01" not in wm.get_all_peer_states()

    def test_peer_state_update_isolation(self, wm: WorldModel):
        """INV-5: Updating peer B does not modify peer A's stored state."""
        peer_a = RobotState(robot_id="amr_02", timestamp=FIXED_TIME, pose=Pose2D(2.0, 2.0))
        peer_b = RobotState(robot_id="amr_03", timestamp=FIXED_TIME, pose=Pose2D(3.0, 3.0))
        wm.update_peer_state(peer_a)
        wm.update_peer_state(peer_b)

        # Update peer B
        peer_b_new = RobotState(
            robot_id="amr_03",
            timestamp=FIXED_TIME + 5.0,
            pose=Pose2D(30.0, 30.0),
        )
        wm.update_peer_state(peer_b_new)

        stored_a = wm.get_peer_state("amr_02")
        stored_b = wm.get_peer_state("amr_03")
        assert stored_a is not None and stored_a.pose.x == 2.0
        assert stored_b is not None and stored_b.pose.x == 30.0

    def test_peer_state_sequence_monotonicity(self, wm: WorldModel):
        """Compound sequence [10, 8, 12, 12, 15] maintains strictly increasing timestamps."""
        t_seq = [10.0, 8.0, 12.0, 12.0, 15.0]
        results = [
            wm.update_peer_state(
                RobotState(robot_id="amr_02", timestamp=t, pose=Pose2D(t, t))
            )
            for t in t_seq
        ]
        assert results == [True, False, True, False, True]
        stored = wm.get_peer_state("amr_02")
        assert stored is not None
        assert stored.timestamp == 15.0
        assert stored.pose.x == 15.0


# ===========================================================================
# Group 3: Peer Intent Tracking & Resource Queries
# ===========================================================================

class TestWorldModelPeerIntent:
    """Tests for tracking peer intents, queries, and expiration filtering."""

    def test_update_and_get_peer_intent(self, wm: WorldModel):
        """First peer intent is accepted and retrievable."""
        intent = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 30.0,
        )
        assert wm.update_peer_intent(intent) is True
        assert wm.get_peer_intent("amr_02") == intent

    def test_active_peer_intent_filtering(self, wm: WorldModel):
        """INV-2: Non-expired intents are returned, expired ones are excluded."""
        active = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 20.0,
        )
        expired = RobotIntent(
            robot_id="amr_03",
            timestamp=FIXED_TIME - 30.0,
            target_resource_id="I2",
            valid_until=FIXED_TIME - 10.0,
        )
        wm.update_peer_intent(active)
        wm.update_peer_intent(expired)

        active_dict = wm.get_active_peer_intents(now=FIXED_TIME)
        assert "amr_02" in active_dict
        assert "amr_03" not in active_dict

    def test_intents_for_resource_query(self, wm: WorldModel):
        """Queries for a specific resource return matching active intents."""
        intent_i1_a = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 30.0,
        )
        intent_i1_b = RobotIntent(
            robot_id="amr_03",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 30.0,
        )
        intent_i2 = RobotIntent(
            robot_id="amr_04",
            timestamp=FIXED_TIME,
            target_resource_id="I2",
            valid_until=FIXED_TIME + 30.0,
        )
        wm.update_peer_intent(intent_i1_a)
        wm.update_peer_intent(intent_i1_b)
        wm.update_peer_intent(intent_i2)

        i1_intents = wm.get_intents_for_resource("I1", now=FIXED_TIME)
        assert len(i1_intents) == 2
        robot_ids = {i.robot_id for i in i1_intents}
        assert robot_ids == {"amr_02", "amr_03"}

    def test_intents_for_resource_excludes_expired(self, wm: WorldModel):
        """Resource query excludes expired intents targeting that resource."""
        active = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 10.0,
        )
        expired = RobotIntent(
            robot_id="amr_03",
            timestamp=FIXED_TIME - 20.0,
            target_resource_id="I1",
            valid_until=FIXED_TIME - 5.0,
        )
        wm.update_peer_intent(active)
        wm.update_peer_intent(expired)

        i1_intents = wm.get_intents_for_resource("I1", now=FIXED_TIME)
        assert len(i1_intents) == 1
        assert i1_intents[0].robot_id == "amr_02"

    def test_reject_older_peer_intent_update(self, wm: WorldModel):
        """Older peer intent update is rejected."""
        newer = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME + 10.0,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 60.0,
        )
        older = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME + 5.0,
            target_resource_id="I2",
            valid_until=FIXED_TIME + 60.0,
        )
        assert wm.update_peer_intent(newer) is True
        assert wm.update_peer_intent(older) is False
        stored = wm.get_peer_intent("amr_02")
        assert stored is not None
        assert stored.target_resource_id == "I1"

    def test_reject_equal_timestamp_peer_intent_update(self, wm: WorldModel):
        """Equal timestamp peer intent update is rejected."""
        first = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 60.0,
        )
        duplicate = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME,
            target_resource_id="I2",
            valid_until=FIXED_TIME + 60.0,
        )
        assert wm.update_peer_intent(first) is True
        assert wm.update_peer_intent(duplicate) is False
        stored = wm.get_peer_intent("amr_02")
        assert stored is not None
        assert stored.target_resource_id == "I1"

    def test_reject_self_robot_id_in_peer_intent_update(self, wm: WorldModel):
        """INV-4: Peer intent with own robot ID is rejected."""
        self_intent = RobotIntent(
            robot_id="amr_01",
            timestamp=FIXED_TIME,
            target_resource_id="I1",
            valid_until=FIXED_TIME + 60.0,
        )
        assert wm.update_peer_intent(self_intent) is False
        assert wm.get_peer_intent("amr_01") is None


# ===========================================================================
# Group 4: Reservations (Shared Resource Claims)
# ===========================================================================

class TestWorldModelReservations:
    """Tests for storing, querying, and removing reservations."""

    def test_add_and_get_reservation(self, wm: WorldModel):
        """Reservation stored by claim_id is retrievable."""
        res = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=FIXED_TIME,
            end_time=FIXED_TIME + 20.0,
            priority=5.0,
            claim_id="claim_001",
            expires_at=FIXED_TIME + 60.0,
        )
        wm.add_reservation(res)
        assert wm.get_reservation("claim_001") == res
        assert len(wm.get_all_reservations()) == 1

    def test_active_reservation_query_filtering(self, wm: WorldModel):
        """INV-3: Active queries return only in-window, non-expired reservations."""
        # Active: [now-5, now+15], expires now+30
        active = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=FIXED_TIME - 5.0,
            end_time=FIXED_TIME + 15.0,
            priority=5.0,
            claim_id="claim_active",
            expires_at=FIXED_TIME + 30.0,
        )
        # Future: [now+10, now+30], not yet active at FIXED_TIME
        future = Reservation(
            resource_id="I1",
            robot_id="amr_03",
            start_time=FIXED_TIME + 10.0,
            end_time=FIXED_TIME + 30.0,
            priority=5.0,
            claim_id="claim_future",
            expires_at=FIXED_TIME + 60.0,
        )
        # Expired: expired at now-5
        expired = Reservation(
            resource_id="I1",
            robot_id="amr_04",
            start_time=FIXED_TIME - 20.0,
            end_time=FIXED_TIME - 10.0,
            priority=5.0,
            claim_id="claim_expired",
            expires_at=FIXED_TIME - 5.0,
        )
        wm.add_reservation(active)
        wm.add_reservation(future)
        wm.add_reservation(expired)

        active_res = wm.get_active_reservations(now=FIXED_TIME)
        assert len(active_res) == 1
        assert active_res[0].claim_id == "claim_active"

    def test_reservations_for_resource_query(self, wm: WorldModel):
        """Returns non-expired reservations for a specific resource."""
        res_i1 = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=FIXED_TIME + 5.0,
            end_time=FIXED_TIME + 25.0,
            priority=5.0,
            claim_id="claim_i1",
            expires_at=FIXED_TIME + 60.0,
        )
        res_i2 = Reservation(
            resource_id="I2",
            robot_id="amr_03",
            start_time=FIXED_TIME + 5.0,
            end_time=FIXED_TIME + 25.0,
            priority=5.0,
            claim_id="claim_i2",
            expires_at=FIXED_TIME + 60.0,
        )
        wm.add_reservation(res_i1)
        wm.add_reservation(res_i2)

        i1_claims = wm.get_reservations_for_resource("I1", now=FIXED_TIME)
        assert len(i1_claims) == 1
        assert i1_claims[0].claim_id == "claim_i1"

    def test_remove_active_reservation(self, wm: WorldModel):
        """Removed reservation is deleted and disappears from queries."""
        res = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=FIXED_TIME,
            end_time=FIXED_TIME + 20.0,
            priority=5.0,
            claim_id="claim_001",
            expires_at=FIXED_TIME + 60.0,
        )
        wm.add_reservation(res)
        assert wm.remove_reservation("claim_001") is True
        assert wm.get_reservation("claim_001") is None
        assert len(wm.get_active_reservations(now=FIXED_TIME)) == 0

    def test_remove_unknown_reservation_returns_false(self, wm: WorldModel):
        """Removing non-existent claim_id returns False."""
        assert wm.remove_reservation("unknown_claim") is False

    def test_get_unknown_reservation_returns_none(self, wm: WorldModel):
        """Querying non-existent claim_id returns None."""
        assert wm.get_reservation("unknown_claim") is None

    def test_overwrite_reservation_same_claim_id(self, wm: WorldModel):
        """Duplicate claim_id overwrites stored reservation."""
        res1 = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=100.0,
            end_time=120.0,
            priority=3.0,
            claim_id="claim_001",
            expires_at=200.0,
        )
        res2 = Reservation(
            resource_id="I1",
            robot_id="amr_02",
            start_time=100.0,
            end_time=130.0,
            priority=8.0,
            claim_id="claim_001",
            expires_at=200.0,
        )
        wm.add_reservation(res1)
        wm.add_reservation(res2)
        stored = wm.get_reservation("claim_001")
        assert stored is not None
        assert stored.priority == 8.0
        assert stored.end_time == 130.0


# ===========================================================================
# Group 5: Tasks
# ===========================================================================

class TestWorldModelTasks:
    """Tests for storing and querying tasks."""

    def test_add_and_get_task(self, wm: WorldModel):
        """Task stored by task_id is retrievable."""
        task = Task(task_id="task_001", priority=7)
        wm.add_task(task)
        assert wm.get_task("task_001") == task
        assert len(wm.get_all_tasks()) == 1

    def test_get_assignable_tasks_filtering(self, wm: WorldModel):
        """Only tasks in assignable states are returned."""
        t_announced = Task(task_id="t1", status=TaskStatus.ANNOUNCED)
        t_bidding = Task(task_id="t2", status=TaskStatus.BIDDING)
        t_progress = Task(task_id="t3", status=TaskStatus.IN_PROGRESS)
        t_completed = Task(task_id="t4", status=TaskStatus.COMPLETED)
        t_failed = Task(task_id="t5", status=TaskStatus.FAILED)

        for t in [t_announced, t_bidding, t_progress, t_completed, t_failed]:
            wm.add_task(t)

        assignable = wm.get_assignable_tasks()
        assignable_ids = {t.task_id for t in assignable}
        assert assignable_ids == {"t1", "t2", "t5"}

    def test_get_unknown_task_returns_none(self, wm: WorldModel):
        """Querying unknown task returns None."""
        assert wm.get_task("nonexistent_task") is None

    def test_overwrite_task_same_task_id(self, wm: WorldModel):
        """Duplicate task_id updates task state."""
        t_initial = Task(task_id="t1", status=TaskStatus.ANNOUNCED)
        t_updated = Task(task_id="t1", status=TaskStatus.ASSIGNED, assigned_robot="amr_02")
        wm.add_task(t_initial)
        wm.add_task(t_updated)
        stored = wm.get_task("t1")
        assert stored is not None
        assert stored.status == TaskStatus.ASSIGNED
        assert stored.assigned_robot == "amr_02"


# ===========================================================================
# Group 6: Expiry Correctness vs. Garbage Collection (INV-5)
# ===========================================================================

class TestWorldModelGarbageCollection:
    """Tests verifying INV-5: correctness is independent of GC cleanup."""

    def test_expired_intent_remains_stored_until_cleanup(self, wm: WorldModel):
        """Expired intent is excluded from active query but physically present until GC."""
        expired_intent = RobotIntent(
            robot_id="amr_02",
            timestamp=FIXED_TIME - 60.0,
            target_resource_id="I1",
            valid_until=FIXED_TIME - 10.0,  # Expired at now=FIXED_TIME
        )
        wm.update_peer_intent(expired_intent)

        # 1. Correctness check: excluded from active query without cleanup
        assert len(wm.get_active_peer_intents(now=FIXED_TIME)) == 0
        assert len(wm.get_intents_for_resource("I1", now=FIXED_TIME)) == 0

        # 2. Physical storage check: still present in raw getter
        assert wm.get_peer_intent("amr_02") is not None

        # 3. Garbage collection
        counts = wm.cleanup_expired(now=FIXED_TIME)
        assert counts["intents_removed"] == 1
        assert counts["reservations_removed"] == 0

        # 4. Post-cleanup physical storage check: now completely pruned
        assert wm.get_peer_intent("amr_02") is None

    def test_cleanup_expired_purges_reservations_and_intents(self, wm: WorldModel):
        """cleanup_expired purges both expired intents and expired reservations."""
        # Expired intent
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME - 30.0,
                valid_until=FIXED_TIME - 1.0,
            )
        )
        # Active intent
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_03",
                timestamp=FIXED_TIME,
                valid_until=FIXED_TIME + 30.0,
            )
        )
        # Expired reservation
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_02",
                start_time=FIXED_TIME - 40.0,
                end_time=FIXED_TIME - 20.0,
                priority=1.0,
                claim_id="claim_old",
                expires_at=FIXED_TIME - 10.0,
            )
        )
        # Active reservation
        wm.add_reservation(
            Reservation(
                resource_id="I1",
                robot_id="amr_03",
                start_time=FIXED_TIME,
                end_time=FIXED_TIME + 20.0,
                priority=1.0,
                claim_id="claim_curr",
                expires_at=FIXED_TIME + 60.0,
            )
        )

        counts = wm.cleanup_expired(now=FIXED_TIME)
        assert counts == {"intents_removed": 1, "reservations_removed": 1}
        assert wm.get_peer_intent("amr_02") is None
        assert wm.get_peer_intent("amr_03") is not None
        assert wm.get_reservation("claim_old") is None
        assert wm.get_reservation("claim_curr") is not None

    def test_cleanup_when_nothing_expired_returns_zero_counts(self, wm: WorldModel):
        """cleanup_expired returns zero counts when all records are active."""
        wm.update_peer_intent(
            RobotIntent(
                robot_id="amr_02",
                timestamp=FIXED_TIME,
                valid_until=FIXED_TIME + 60.0,
            )
        )
        counts = wm.cleanup_expired(now=FIXED_TIME)
        assert counts == {"intents_removed": 0, "reservations_removed": 0}


# ===========================================================================
# Group 7: Validation & Edge Cases (INV-6, Boundaries)
# ===========================================================================

class TestWorldModelValidationAndEdgeCases:
    """Tests for defensive boundary validation and empty collection safety."""

    def test_empty_world_model_queries_safe(self, wm: WorldModel):
        """INV-6: All queries on empty WorldModel return safe empty results without crashing."""
        assert wm.get_own_state() is None
        assert wm.get_own_intent() is None
        assert wm.get_all_peer_states() == {}
        assert wm.get_fresh_peer_states(now=FIXED_TIME) == {}
        assert wm.get_known_peer_ids() == set()
        assert wm.get_peer_count() == 0
        assert wm.is_peer_state_fresh("amr_99", now=FIXED_TIME) is False
        assert wm.get_active_peer_intents(now=FIXED_TIME) == {}
        assert wm.get_intents_for_resource("I1", now=FIXED_TIME) == []
        assert wm.get_all_reservations() == {}
        assert wm.get_active_reservations(now=FIXED_TIME) == []
        assert wm.get_reservations_for_resource("I1", now=FIXED_TIME) == []
        assert wm.get_all_tasks() == {}
        assert wm.get_assignable_tasks() == []

    def test_init_with_empty_robot_id_raises_value_error(self):
        """Creating WorldModel with empty string robot_id raises ValueError."""
        with pytest.raises(ValueError, match="empty"):
            WorldModel(robot_id="")

    def test_validation_empty_ids_raise_value_error(self, wm: WorldModel):
        """Empty IDs in data objects passed to WorldModel raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            wm.update_peer_state(RobotState(robot_id="", timestamp=FIXED_TIME))

        with pytest.raises(ValueError, match="empty"):
            wm.update_peer_intent(RobotIntent(robot_id="", timestamp=FIXED_TIME))

        with pytest.raises(ValueError, match="empty"):
            wm.add_reservation(
                Reservation(
                    resource_id="I1",
                    robot_id="amr_02",
                    start_time=10,
                    end_time=20,
                    priority=1,
                    claim_id="",
                    expires_at=30,
                )
            )

        with pytest.raises(ValueError, match="empty"):
            wm.add_task(Task(task_id=""))

    def test_validation_inverted_reservation_interval_raises_value_error(self, wm: WorldModel):
        """Reservation with end_time < start_time raises ValueError."""
        with pytest.raises(ValueError, match="end_time"):
            wm.add_reservation(
                Reservation(
                    resource_id="I1",
                    robot_id="amr_02",
                    start_time=100.0,
                    end_time=50.0,  # Invalid interval
                    priority=1.0,
                    claim_id="claim_invalid",
                    expires_at=200.0,
                )
            )

    def test_validation_negative_timestamp_raises_value_error(self, wm: WorldModel):
        """Negative timestamps in peer updates raise ValueError."""
        with pytest.raises(ValueError, match="negative"):
            wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=-1.0))

        with pytest.raises(ValueError, match="negative"):
            wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=-5.0))
