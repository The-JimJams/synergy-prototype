"""
Tests for TaskAllocator — Phase 6.
===================================

Unit tests covering decentralized task allocation, bidding, eligibility,
deterministic tie-breaking, immutability, and lifecycle transitions.

Test Categories:
  1. Single Robot Bidding & Eligibility           (4 tests)
  2. Multi-Robot Bidding & Deterministic Winner   (4 tests)
  3. Task Status & Lifecycle Guards               (5 tests)
  4. Reassignment & Recovery                      (4 tests)
  5. Factor Formulations & Scoring Weights        (5 tests)
  6. State Freshness & Decentralized Agreement    (3 tests)
  7. Immutability & Numeric Validation            (6 tests)

Total: 31 tests
"""

from __future__ import annotations

import math
import pytest

from fleet_coordination.algorithm.task_allocator import TaskAllocator
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    TaskBidWeights,
)
from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task, TaskStatus, TaskType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_wm(robot_id: str, config: CoordinationConfig | None = None) -> WorldModel:
    """Create a fresh WorldModel."""
    return WorldModel(robot_id=robot_id, config=config)


def make_task(
    task_id: str = "T1",
    priority: int = 5,
    deadline: float | None = None,
    status: TaskStatus = TaskStatus.ANNOUNCED,
) -> Task:
    """Create a Task object with default values."""
    return Task(
        task_id=task_id,
        task_type=TaskType.PICKUP_AND_DELIVERY,
        priority=priority,
        deadline=deadline,
        source_location="SHELF_A1",
        target_location="PACKING_1",
        status=status,
    )


def make_state(
    robot_id: str,
    battery: float = 100.0,
    status: RobotStatus = RobotStatus.IDLE,
    current_task_id: str | None = None,
    timestamp: float = 100.0,
) -> RobotState:
    """Create a RobotState object."""
    return RobotState(
        robot_id=robot_id,
        battery_percent=battery,
        status=status,
        current_task_id=current_task_id,
        timestamp=timestamp,
        pose=Pose2D(0.0, 0.0, 0.0),
    )


# ===========================================================================
# Category 1 — Single Robot Bidding & Eligibility (4 tests)
# ===========================================================================

class TestSingleRobotBidding:

    def test_single_idle_robot_wins_announced_task(self):
        """Single idle robot with healthy battery is eligible and wins."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", battery=80.0, timestamp=now))
        task = make_task("T1", priority=5)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_01"
        assert dec.reason == "ASSIGNED"
        assert dec.winner_score > 0.0
        assert dec.is_winner("amr_01") is True
        assert dec.is_winner("amr_02") is False

    def test_single_busy_robot_rejected(self):
        """Single robot already executing a task (current_task_id is set) is ineligible."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", current_task_id="T_ACTIVE", timestamp=now))
        task = make_task("T1")

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is False
        assert dec.winner_id is None
        assert dec.reason == "NO_ELIGIBLE_ROBOT"
        assert "amr_01" in dec.all_bids
        assert dec.all_bids["amr_01"].eligible is False
        assert dec.all_bids["amr_01"].ineligibility_reason == "ALREADY_ASSIGNED_TASK"

    def test_single_low_battery_robot_rejected(self):
        """Robot with battery below min_battery_percent (default 20.0%) is ineligible."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        # Battery 15% < 20% threshold
        wm.set_own_state(make_state("amr_01", battery=15.0, timestamp=now))
        task = make_task("T1")

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is False
        assert dec.winner_id is None
        assert dec.reason == "NO_ELIGIBLE_ROBOT"
        assert dec.all_bids["amr_01"].eligible is False
        assert dec.all_bids["amr_01"].ineligibility_reason == "LOW_BATTERY"

    def test_single_waiting_robot_accepted(self):
        """Robot with status WAITING (e.g. yielding at an intersection) is eligible."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", status=RobotStatus.WAITING, timestamp=now))
        task = make_task("T1")

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_01"


# ===========================================================================
# Category 2 — Multi-Robot Bidding & Deterministic Winner (4 tests)
# ===========================================================================

class TestMultiRobotBidding:

    def test_highest_score_robot_wins(self):
        """Three eligible robots with differing battery levels: highest score wins."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", battery=60.0, timestamp=now))
        wm.update_peer_state(make_state("amr_02", battery=95.0, timestamp=now))
        wm.update_peer_state(make_state("amr_03", battery=40.0, timestamp=now))

        task = make_task("T1", priority=5)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_02"  # Highest battery -> highest score
        assert dec.winner_score == dec.all_bids["amr_02"].bid_score
        assert dec.tie_broken_by_id is False

    def test_equal_bids_broken_by_lower_robot_id(self):
        """Two robots with identical state: lower robot ID wins tie (lower_id_wins_ties=True)."""
        config = CoordinationConfig(lower_id_wins_ties=True)
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_02", config=config)
        now = 100.0

        wm.set_own_state(make_state("amr_02", battery=80.0, timestamp=now))
        wm.update_peer_state(make_state("amr_01", battery=80.0, timestamp=now))

        task = make_task("T1", priority=5)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_01"  # "amr_01" < "amr_02"
        assert dec.tie_broken_by_id is True

    def test_equal_bids_broken_by_higher_robot_id_when_configured(self):
        """When lower_id_wins_ties=False, higher robot ID wins the tie."""
        config = CoordinationConfig(lower_id_wins_ties=False)
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_01", config=config)
        now = 100.0

        wm.set_own_state(make_state("amr_01", battery=80.0, timestamp=now))
        wm.update_peer_state(make_state("amr_02", battery=80.0, timestamp=now))

        task = make_task("T1", priority=5)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_02"  # "amr_02" > "amr_01"
        assert dec.tie_broken_by_id is True

    def test_score_epsilon_triggers_tie_break(self):
        """Bids differing by less than score_epsilon (1e-9) are treated as tied."""
        config = CoordinationConfig(
            task_bid_weights=TaskBidWeights(score_epsilon=1e-5),
            lower_id_wins_ties=True,
        )
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_02", config=config)
        now = 100.0

        # Small difference in battery creating < 1e-5 delta
        wm.set_own_state(make_state("amr_02", battery=80.000001, timestamp=now))
        wm.update_peer_state(make_state("amr_01", battery=80.000000, timestamp=now))

        task = make_task("T1")

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        # Within epsilon -> tie-break by ID -> amr_01 wins
        assert dec.winner_id == "amr_01"
        assert dec.tie_broken_by_id is True


# ===========================================================================
# Category 3 — Task Status & Lifecycle Guards (5 tests)
# ===========================================================================

class TestTaskStatusGuards:

    def test_announced_task_is_assignable(self):
        """Task in ANNOUNCED status is eligible for evaluation."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.ANNOUNCED)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is True

    def test_bidding_task_is_assignable(self):
        """Task in BIDDING status is eligible for evaluation."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.BIDDING)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is True

    def test_assigned_task_rejected(self):
        """Task in ASSIGNED status returns accepted=False, ALREADY_ASSIGNED."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.ASSIGNED)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is False
        assert dec.reason == "ALREADY_ASSIGNED"

    def test_in_progress_task_rejected(self):
        """Task in IN_PROGRESS status returns accepted=False, ALREADY_ASSIGNED."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.IN_PROGRESS)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is False
        assert dec.reason == "ALREADY_ASSIGNED"

    def test_completed_task_rejected(self):
        """Task in COMPLETED status returns accepted=False, ALREADY_ASSIGNED."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.COMPLETED)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is False
        assert dec.reason == "ALREADY_ASSIGNED"


# ===========================================================================
# Category 4 — Reassignment & Recovery (4 tests)
# ===========================================================================

class TestReassignmentAndRecovery:

    def test_failed_task_reassignable(self):
        """Task with status FAILED is assignable for a new bidding round."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.FAILED)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is True
        assert dec.winner_id == "amr_01"

    def test_reassigned_status_task_accepted(self):
        """Task with status REASSIGNED is assignable."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", status=TaskStatus.REASSIGNED)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        assert dec.accepted is True
        assert dec.winner_id == "amr_01"

    def test_failed_robot_excluded_from_reassignment(self):
        """Robot with RobotStatus.FAILED is excluded; remaining healthy robot wins."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        # amr_01 failed, amr_02 is healthy
        wm.set_own_state(make_state("amr_01", status=RobotStatus.FAILED, timestamp=now))
        wm.update_peer_state(make_state("amr_02", status=RobotStatus.IDLE, timestamp=now))

        task = make_task("T1", status=TaskStatus.FAILED)
        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        assert dec.winner_id == "amr_02"
        assert dec.all_bids["amr_01"].eligible is False
        assert dec.all_bids["amr_01"].ineligibility_reason == "STATUS_FAILED"

    def test_explicit_assign_task_mutates_only_task(self):
        """assign_task explicitly updates task.status and task.assigned_robot in WorldModel."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", timestamp=now))
        task = make_task("T1")
        wm.add_task(task)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True

        # Perform explicit assignment
        success = allocator.assign_task("T1", wm, dec)
        assert success is True

        # Verify task in WorldModel was updated
        updated_task = wm.get_task("T1")
        assert updated_task is not None
        assert updated_task.status == TaskStatus.ASSIGNED
        assert updated_task.assigned_robot == "amr_01"

        # Subsequent assignment attempt on already ASSIGNED task fails
        second_dec = allocator.evaluate_task(updated_task, wm, now=now)
        assert second_dec.accepted is False


# ===========================================================================
# Category 5 — Factor Formulations & Scoring Weights (5 tests)
# ===========================================================================

class TestFactorFormulationsAndWeights:

    def test_battery_weight_influences_score(self):
        """Battery difference alters the composite score according to w_battery."""
        weights = TaskBidWeights(w_battery=1.0, w_priority=0.0, w_deadline=0.0)
        config = CoordinationConfig(task_bid_weights=weights)
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_01", config=config)
        now = 100.0

        wm.set_own_state(make_state("amr_01", battery=80.0, timestamp=now))
        task = make_task("T1")

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True
        # Factor is 80/100 = 0.8
        assert pytest.approx(dec.winner_score, 1e-6) == 0.8

    def test_task_priority_influences_score(self):
        """Priority (1..10) maps to priority_factor (0.0..1.0) and weights score."""
        weights = TaskBidWeights(w_battery=0.0, w_priority=1.0, w_deadline=0.0)
        config = CoordinationConfig(task_bid_weights=weights)
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_01", config=config)
        now = 100.0

        wm.set_own_state(make_state("amr_01", timestamp=now))

        # Priority 10 -> factor (10-1)/9 = 1.0
        task_10 = make_task("T10", priority=10)
        dec_10 = allocator.evaluate_task(task_10, wm, now=now)
        assert pytest.approx(dec_10.winner_score, 1e-6) == 1.0

        # Priority 1 -> factor (1-1)/9 = 0.0
        task_1 = make_task("T1", priority=1)
        dec_1 = allocator.evaluate_task(task_1, wm, now=now)
        assert pytest.approx(dec_1.winner_score, 1e-6) == 0.0

    def test_deadline_urgency_increases_score(self):
        """A closer deadline yields higher deadline_urgency and higher bid score."""
        weights = TaskBidWeights(w_battery=0.0, w_priority=0.0, w_deadline=1.0)
        config = CoordinationConfig(task_bid_weights=weights)
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_01", config=config)
        now = 100.0

        wm.set_own_state(make_state("amr_01", timestamp=now))

        # Urgent: 2 seconds remaining -> 1/2 = 0.5
        task_urgent = make_task("T_URGENT", deadline=102.0)
        dec_urgent = allocator.evaluate_task(task_urgent, wm, now=now)
        assert pytest.approx(dec_urgent.winner_score, 1e-6) == 0.5

        # Less urgent: 10 seconds remaining -> 1/10 = 0.1
        task_relaxed = make_task("T_RELAXED", deadline=110.0)
        dec_relaxed = allocator.evaluate_task(task_relaxed, wm, now=now)
        assert pytest.approx(dec_relaxed.winner_score, 1e-6) == 0.1

    def test_missing_deadline_defaults_to_zero_urgency(self):
        """When deadline is None, deadline_factor is 0.0."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1", deadline=None)
        dec = allocator.evaluate_task(task, wm, now=100.0)
        factors = dec.all_bids["amr_01"].factors
        assert factors["deadline_factor"] == 0.0

    def test_ineligible_robot_score_is_zero(self):
        """Ineligible robot bid score is strictly 0.0 regardless of other factors."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        # Busy robot (ineligible)
        wm.set_own_state(make_state("amr_01", battery=100.0, current_task_id="BUSY", timestamp=now))
        task = make_task("T1", priority=10)

        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.all_bids["amr_01"].bid_score == 0.0
        assert dec.all_bids["amr_01"].eligible is False


# ===========================================================================
# Category 6 — State Freshness & Decentralized Agreement (3 tests)
# ===========================================================================

class TestFreshnessAndDecentralizedAgreement:

    def test_stale_peer_state_excluded_from_bidding(self):
        """Peer robot whose state age > peer_state_max_age_seconds is marked ineligible."""
        config = CoordinationConfig()
        allocator = TaskAllocator(config=config)
        wm = make_wm("amr_01", config=config)
        now = 100.0

        max_age = config.timeouts.peer_state_max_age_seconds  # 5.0s
        stale_timestamp = now - max_age - 1.0  # 6s old -> stale

        wm.set_own_state(make_state("amr_01", battery=50.0, timestamp=now))
        # Peer has 100% battery but stale telemetry
        wm.update_peer_state(make_state("amr_02", battery=100.0, timestamp=stale_timestamp))

        task = make_task("T1")
        dec = allocator.evaluate_task(task, wm, now=now)

        assert dec.accepted is True
        assert dec.winner_id == "amr_01"  # amr_02 excluded due to stale telemetry
        assert dec.all_bids["amr_02"].eligible is False
        assert dec.all_bids["amr_02"].ineligibility_reason == "STALE_TELEMETRY"

    def test_decentralized_agreement_across_symmetric_world_models(self):
        """INV-10: When three robots have identical views, all three select the same winner."""
        allocator = TaskAllocator()
        now = 100.0

        state_1 = make_state("amr_01", battery=70.0, timestamp=now)
        state_2 = make_state("amr_02", battery=90.0, timestamp=now)
        state_3 = make_state("amr_03", battery=60.0, timestamp=now)
        task = make_task("T1", priority=8)

        # Build WM for amr_01
        wm_1 = make_wm("amr_01")
        wm_1.set_own_state(state_1)
        wm_1.update_peer_state(state_2)
        wm_1.update_peer_state(state_3)

        # Build WM for amr_02
        wm_2 = make_wm("amr_02")
        wm_2.set_own_state(state_2)
        wm_2.update_peer_state(state_1)
        wm_2.update_peer_state(state_3)

        # Build WM for amr_03
        wm_3 = make_wm("amr_03")
        wm_3.set_own_state(state_3)
        wm_3.update_peer_state(state_1)
        wm_3.update_peer_state(state_2)

        # Evaluate from all three perspectives
        dec_1 = allocator.evaluate_task(task, wm_1, now=now)
        dec_2 = allocator.evaluate_task(task, wm_2, now=now)
        dec_3 = allocator.evaluate_task(task, wm_3, now=now)

        # All three must agree on amr_02 as the winner with identical score
        assert dec_1.winner_id == "amr_02"
        assert dec_2.winner_id == "amr_02"
        assert dec_3.winner_id == "amr_02"
        assert dec_1.winner_score == dec_2.winner_score == dec_3.winner_score

    def test_different_world_model_insertion_order_produces_identical_winner(self):
        """Sorting candidate IDs guarantees winner selection is dictionary-order independent."""
        allocator = TaskAllocator()
        now = 100.0
        task = make_task("T1")

        state_a = make_state("amr_a", battery=80.0, timestamp=now)
        state_b = make_state("amr_b", battery=80.0, timestamp=now)

        # Insertion order 1: a then b
        wm_1 = make_wm("amr_00")
        wm_1.set_own_state(make_state("amr_00", battery=50.0, timestamp=now))
        wm_1.update_peer_state(state_a)
        wm_1.update_peer_state(state_b)

        # Insertion order 2: b then a
        wm_2 = make_wm("amr_00")
        wm_2.set_own_state(make_state("amr_00", battery=50.0, timestamp=now))
        wm_2.update_peer_state(state_b)
        wm_2.update_peer_state(state_a)

        dec_1 = allocator.evaluate_task(task, wm_1, now=now)
        dec_2 = allocator.evaluate_task(task, wm_2, now=now)

        assert dec_1.winner_id == dec_2.winner_id
        assert dec_1.tie_broken_by_id == dec_2.tie_broken_by_id


# ===========================================================================
# Category 7 — Immutability & Numeric Validation (6 tests)
# ===========================================================================

class TestImmutabilityAndNumericValidation:

    def test_world_model_immutability_on_states_and_intents(self):
        """INV-6 & INV-7: evaluate_task NEVER mutates own_state, peer_states,
        own_intent, peer_intents, or tasks."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        own_state = make_state("amr_01", timestamp=now)
        wm.set_own_state(own_state)
        peer_state = make_state("amr_02", timestamp=now)
        wm.update_peer_state(peer_state)

        own_intent = RobotIntent(robot_id="amr_01", valid_until=200.0, timestamp=now)
        wm.set_own_intent(own_intent)
        peer_intent = RobotIntent(robot_id="amr_02", valid_until=200.0, timestamp=now)
        wm.update_peer_intent(peer_intent)

        task = make_task("T1")
        wm.add_task(task)

        # Snapshots
        snap_own_state = wm.get_own_state()
        snap_peer_states = wm.get_all_peer_states()
        snap_own_intent = wm.get_own_intent()
        snap_peer_intents = {pid: wm.get_peer_intent(pid) for pid in wm.get_known_peer_ids()}
        snap_tasks = wm.get_all_tasks()

        # Run evaluation
        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True

        # Assert zero mutations
        assert wm.get_own_state() is snap_own_state
        assert wm.get_all_peer_states() == snap_peer_states
        assert wm.get_own_intent() is snap_own_intent
        current_peer_intents = {pid: wm.get_peer_intent(pid) for pid in wm.get_known_peer_ids()}
        assert current_peer_intents == snap_peer_intents
        assert wm.get_all_tasks() == snap_tasks

    def test_no_reservation_side_effects(self):
        """INV-9: evaluate_task NEVER mutates reservations."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        res = Reservation(
            resource_id="I1", robot_id="amr_01",
            start_time=100.0, end_time=130.0,
            priority=0.5, expires_at=160.0,
        )
        wm.add_reservation(res)
        wm.set_own_state(make_state("amr_01", timestamp=now))

        task = make_task("T1")
        dec = allocator.evaluate_task(task, wm, now=now)
        assert dec.accepted is True

        # Reservations unchanged
        assert wm.get_reservation(res.claim_id) == res

    def test_nan_now_rejected(self):
        """NaN reference time is rejected with INVALID_TIMESTAMP."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1")
        dec = allocator.evaluate_task(task, wm, now=float("nan"))
        assert dec.accepted is False
        assert dec.reason == "INVALID_TIMESTAMP"

    def test_inf_now_rejected(self):
        """Infinity reference time is rejected with INVALID_TIMESTAMP."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1")
        dec = allocator.evaluate_task(task, wm, now=float("inf"))
        assert dec.accepted is False
        assert dec.reason == "INVALID_TIMESTAMP"

    def test_negative_now_rejected(self):
        """Negative reference time is rejected with INVALID_TIMESTAMP."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        wm.set_own_state(make_state("amr_01"))

        task = make_task("T1")
        dec = allocator.evaluate_task(task, wm, now=-1.0)
        assert dec.accepted is False
        assert dec.reason == "INVALID_TIMESTAMP"

    def test_repeated_evaluation_is_idempotent(self):
        """INV-2: Repeated evaluations on identical state produce identical decisions."""
        allocator = TaskAllocator()
        wm = make_wm("amr_01")
        now = 100.0

        wm.set_own_state(make_state("amr_01", battery=80.0, timestamp=now))
        wm.update_peer_state(make_state("amr_02", battery=75.0, timestamp=now))

        task = make_task("T1", priority=5)

        dec1 = allocator.evaluate_task(task, wm, now=now)
        dec2 = allocator.evaluate_task(task, wm, now=now)

        assert dec1.accepted == dec2.accepted
        assert dec1.winner_id == dec2.winner_id
        assert dec1.winner_score == dec2.winner_score
        assert dec1.reason == dec2.reason
        assert dec1.tie_broken_by_id == dec2.tie_broken_by_id
