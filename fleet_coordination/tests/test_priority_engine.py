"""
Unit tests for PriorityEngine — Deterministic Conflict Arbitration.
===================================================================

Tests verify:
- Individual factor dominance (task priority, deadline urgency, waiting time, battery urgency)
- Multi-factor composite weighted scoring
- Deterministic floating-point epsilon tie-breaking
- Robust missing-data handling and boundary clamping
- WorldModel immutability
- Decentralized agreement across independent WorldModel instances
- Symmetric conflict report orientation invariance
"""

import pytest

from fleet_coordination.algorithm.priority_engine import PriorityEngine
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    PriorityWeights,
)
from fleet_coordination.models.conflict import ConflictReport, ConflictSeverity
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task
from fleet_coordination.tests.conftest import FIXED_TIME


@pytest.fixture
def engine() -> PriorityEngine:
    """Standard PriorityEngine instance."""
    return PriorityEngine()


@pytest.fixture
def wm() -> WorldModel:
    """WorldModel instance for local robot 'amr_01'."""
    return WorldModel(robot_id="amr_01")


def create_standard_conflict(
    robot_a: str = "amr_01",
    robot_b: str = "amr_02",
    resource: str = "I1",
) -> ConflictReport:
    """Helper to create a basic ConflictReport."""
    return ConflictReport(
        robot_a_id=robot_a,
        robot_b_id=robot_b,
        resource_id=resource,
        overlap_start=FIXED_TIME + 5.0,
        overlap_end=FIXED_TIME + 15.0,
        severity=ConflictSeverity.HIGH,
        detected_at=FIXED_TIME,
    )


# ===========================================================================
# Group 1: Factor Dominance
# ===========================================================================

class TestPriorityEngineFactorDominance:
    """Tests isolating individual factors when other factors are equal."""

    def test_higher_task_priority_wins(self, engine: PriorityEngine, wm: WorldModel):
        """Robot A with higher task priority (9 vs 2) wins, all else equal."""
        # Tasks
        wm.add_task(Task(task_id="task_high", priority=9))
        wm.add_task(Task(task_id="task_low", priority=2))

        # Intents
        wm.set_own_intent(
            RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id="task_high", target_resource_id="I1")
        )
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, task_id="task_low", target_resource_id="I1")
        )

        # States (equal battery)
        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        conflict = create_standard_conflict("amr_01", "amr_02")
        decision = engine.resolve(conflict, wm, now=FIXED_TIME)

        assert decision.winner_id == "amr_01"
        assert decision.loser_id == "amr_02"
        assert decision.score_a > decision.score_b
        assert decision.tie_broken_by_id is False

    def test_higher_deadline_urgency_wins(self, engine: PriorityEngine, wm: WorldModel):
        """Robot A with tight deadline wins over Robot B with no deadline (same task priority)."""
        # Task A: tight deadline (2s away) -> urgency = 1/2 = 0.5
        wm.add_task(Task(task_id="task_urgent", priority=5, deadline=FIXED_TIME + 2.0))
        # Task B: no deadline -> urgency = 0.0
        wm.add_task(Task(task_id="task_relaxed", priority=5, deadline=None))

        wm.set_own_intent(
            RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id="task_urgent", target_resource_id="I1")
        )
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, task_id="task_relaxed", target_resource_id="I1")
        )

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        conflict = create_standard_conflict("amr_01", "amr_02")
        decision = engine.resolve(conflict, wm, now=FIXED_TIME)

        assert decision.winner_id == "amr_01"
        assert decision.factors_a["deadline_urgency"] > decision.factors_b["deadline_urgency"]

    def test_longer_waiting_time_wins(self, engine: PriorityEngine, wm: WorldModel):
        """Robot A committed earlier (older intent timestamp) wins over freshly created intent."""
        # Own intent committed 60s ago
        wm.set_own_intent(
            RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 60.0, target_resource_id="I1")
        )
        # Peer intent committed 5s ago
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME - 5.0, target_resource_id="I1")
        )

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        conflict = create_standard_conflict("amr_01", "amr_02")
        decision = engine.resolve(conflict, wm, now=FIXED_TIME)

        assert decision.winner_id == "amr_01"
        assert decision.factors_a["waiting_time"] > decision.factors_b["waiting_time"]

    def test_greater_battery_urgency_wins(self, engine: PriorityEngine, wm: WorldModel):
        """Robot A with low battery (20%) wins over Robot B with full battery (100%)."""
        wm.set_own_intent(
            RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1")
        )
        wm.update_peer_intent(
            RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1")
        )

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=20.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        conflict = create_standard_conflict("amr_01", "amr_02")
        decision = engine.resolve(conflict, wm, now=FIXED_TIME)

        assert decision.winner_id == "amr_01"
        assert decision.factors_a["battery_urgency"] == 0.8  # (100 - 20) / 100
        assert decision.factors_b["battery_urgency"] == 0.0


# ===========================================================================
# Group 2: Combined Multi-Factor Scenarios
# ===========================================================================

class TestPriorityEngineCompositeScoring:
    """Tests for multi-factor weighted scoring and factor breakdown."""

    def test_combined_weighted_score_wins(self, engine: PriorityEngine, wm: WorldModel):
        """Moderate priority + tight deadline beats high priority + far deadline."""
        # A: Priority 5, tight deadline 2s -> task=(4/9)=0.444, deadline=0.5 -> score = 1.0*0.444 + 0.8*0.5 = 0.844
        wm.add_task(Task(task_id="t_a", priority=5, deadline=FIXED_TIME + 2.0))
        # B: Priority 8, distant deadline 100s -> task=(7/9)=0.777, deadline=0.01 -> score = 1.0*0.777 + 0.8*0.01 = 0.785
        wm.add_task(Task(task_id="t_b", priority=8, deadline=FIXED_TIME + 100.0))

        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id="t_a", target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, task_id="t_b", target_resource_id="I1"))

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.winner_id == "amr_01"
        assert decision.score_a > decision.score_b

    def test_factor_breakdown_dictionary_matches_formula(self, engine: PriorityEngine, wm: WorldModel):
        """PriorityDecision contains exact normalized factor dictionaries."""
        wm.add_task(Task(task_id="t1", priority=10, deadline=FIXED_TIME + 10.0))
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 30.0, task_id="t1", target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=40.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=90.0))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)

        # A factors:
        # task_prio: (10-1)/9 = 1.0
        # deadline: 1/10 = 0.1
        # wait: 30 / 120 = 0.25
        # battery: (100-40)/100 = 0.6
        fa = decision.factors_a
        assert fa["task_priority"] == pytest.approx(1.0)
        assert fa["deadline_urgency"] == pytest.approx(0.1)
        assert fa["waiting_time"] == pytest.approx(0.25)
        assert fa["battery_urgency"] == pytest.approx(0.6)


# ===========================================================================
# Group 3: Tie-Breaking & Epsilon
# ===========================================================================

class TestPriorityEngineTieBreaking:
    """Tests for floating-point near-equality tolerance and deterministic tie-breaking."""

    def test_exact_equal_scores_uses_robot_id_tie_break(self, engine: PriorityEngine, wm: WorldModel):
        """Identical state on both robots triggers tie-break: lower ID ('amr_01' < 'amr_02') wins."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.score_a == pytest.approx(decision.score_b)
        assert decision.tie_broken_by_id is True
        assert decision.winner_id == "amr_01"
        assert decision.loser_id == "amr_02"

    def test_near_equal_scores_within_epsilon_triggers_tie_break(self, engine: PriorityEngine):
        """Scores differing by 1e-11 (< score_epsilon=1e-9) trigger robot ID tie-break."""
        wm_02 = WorldModel(robot_id="amr_02")
        # Create extremely tiny timestamp difference: 1e-10 seconds
        wm_02.set_own_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm_02.update_peer_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 1e-10, target_resource_id="I1"))

        wm_02.set_own_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))
        wm_02.update_peer_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))

        decision = engine.resolve(create_standard_conflict("amr_02", "amr_01"), wm_02, now=FIXED_TIME)
        assert decision.tie_broken_by_id is True
        # Lower robot ID ('amr_01') wins despite amr_02 being robot_a
        assert decision.winner_id == "amr_01"

    def test_scores_differing_by_more_than_epsilon_uses_score(self, engine: PriorityEngine, wm: WorldModel):
        """Scores differing by 1e-5 (> score_epsilon=1e-9) win by score, not tie-breaker."""
        # amr_02 has slightly higher waiting time (1e-3 seconds difference -> delta score ~ 4e-6 > 1e-9)
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME - 0.001, target_resource_id="I1"))

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=100.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=100.0))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.tie_broken_by_id is False
        assert decision.winner_id == "amr_02"

    def test_configurable_tie_breaker_direction(self, wm: WorldModel):
        """When lower_id_wins_ties=False, higher robot ID ('amr_02') wins ties."""
        config = CoordinationConfig(lower_id_wins_ties=False)
        custom_engine = PriorityEngine(config=config)

        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        decision = custom_engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.tie_broken_by_id is True
        assert decision.winner_id == "amr_02"


# ===========================================================================
# Group 4: Missing Data & Clamping
# ===========================================================================

class TestPriorityEngineMissingDataAndClamping:
    """Tests for graceful fallback when optional telemetry or tasks are missing."""

    def test_missing_task_id_uses_zero_task_factors(self, engine: PriorityEngine, wm: WorldModel):
        """Intent with task_id=None (non-task navigation) has task_priority=0 and deadline_urgency=0."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id=None, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, task_id=None, target_resource_id="I1"))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["task_priority"] == 0.0
        assert decision.factors_a["deadline_urgency"] == 0.0

    def test_missing_task_in_world_model_falls_back_safely(self, engine: PriorityEngine, wm: WorldModel):
        """Task ID specified in intent but absent from WorldModel falls back safely to 0.0."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id="unregistered_task", target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["task_priority"] == 0.0
        assert decision.factors_a["deadline_urgency"] == 0.0

    def test_missing_robot_state_uses_safe_battery_default(self, engine: PriorityEngine, wm: WorldModel):
        """Robot with no RobotState in WorldModel receives nominal battery (urgency=0.0)."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))
        # No states added

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["battery_urgency"] == 0.0
        assert decision.factors_b["battery_urgency"] == 0.0

    def test_battery_clamped_to_valid_range(self, engine: PriorityEngine, wm: WorldModel):
        """Battery telemetry < 0% or > 100% is clamped to [0.0, 100.0]."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        wm.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=-25.0))
        wm.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=150.0))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["battery_urgency"] == 1.0  # Clamped to 0% -> urgency = (100-0)/100 = 1.0
        assert decision.factors_b["battery_urgency"] == 0.0  # Clamped to 100% -> urgency = (100-100)/100 = 0.0

    def test_past_deadline_gives_max_urgency(self, engine: PriorityEngine, wm: WorldModel):
        """Task with deadline in the past receives maximum deadline urgency (1.0)."""
        wm.add_task(Task(task_id="overdue", priority=5, deadline=FIXED_TIME - 10.0))
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, task_id="overdue", target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["deadline_urgency"] == 1.0

    def test_very_old_intent_waiting_clamped_to_one(self, engine: PriorityEngine, wm: WorldModel):
        """Intent age exceeding max_wait_seconds (120s) is clamped to 1.0."""
        # Age = 300s > 120s
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 300.0, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        decision = engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)
        assert decision.factors_a["waiting_time"] == 1.0


# ===========================================================================
# Group 5: Validation Errors & Immutability
# ===========================================================================

class TestPriorityEngineValidationAndImmutability:
    """Tests for input validation and state safety."""

    def test_missing_intent_raises_value_error(self, engine: PriorityEngine, wm: WorldModel):
        """Contender with no intent in WorldModel raises ValueError."""
        # Only own intent set; peer intent missing
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        conflict = create_standard_conflict("amr_01", "amr_02")

        with pytest.raises(ValueError, match="no intent in WorldModel"):
            engine.resolve(conflict, wm, now=FIXED_TIME)

    def test_negative_now_raises_value_error(self, engine: PriorityEngine, wm: WorldModel):
        """Negative reference timestamp raises ValueError."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))
        conflict = create_standard_conflict("amr_01", "amr_02")

        with pytest.raises(ValueError, match="cannot be negative"):
            engine.resolve(conflict, wm, now=-1.0)

    def test_world_model_immutability(self, engine: PriorityEngine, wm: WorldModel):
        """PriorityEngine.resolve() performs zero mutations on WorldModel."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        pre_state = wm.get_all_peer_states()
        pre_intents = wm.get_active_peer_intents(now=FIXED_TIME)
        pre_reservations = wm.get_all_reservations()
        pre_tasks = wm.get_all_tasks()

        engine.resolve(create_standard_conflict("amr_01", "amr_02"), wm, now=FIXED_TIME)

        assert wm.get_all_peer_states() == pre_state
        assert wm.get_active_peer_intents(now=FIXED_TIME) == pre_intents
        assert wm.get_all_reservations() == pre_reservations
        assert wm.get_all_tasks() == pre_tasks


# ===========================================================================
# Group 6: Decentralized Agreement & Symmetry (Critical Tests)
# ===========================================================================

class TestPriorityEngineDecentralizedAgreement:
    """Critical tests verifying that independent robots reach identical decisions."""

    def test_decentralized_agreement_two_world_models(self, engine: PriorityEngine):
        """Two separate robots (Robot A and Robot B) with identical telemetry reach exact same winner."""
        # Setup WorldModel A (Robot A's local store)
        wm_a = WorldModel(robot_id="amr_01")
        wm_a.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 20.0, task_id="task_1", target_resource_id="I1"))
        wm_a.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME - 10.0, task_id="task_2", target_resource_id="I1"))
        wm_a.set_own_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=60.0))
        wm_a.update_peer_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=80.0))
        wm_a.add_task(Task(task_id="task_1", priority=6))
        wm_a.add_task(Task(task_id="task_2", priority=8))

        # Setup WorldModel B (Robot B's local store) with the exact same data from its perspective
        wm_b = WorldModel(robot_id="amr_02")
        wm_b.set_own_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME - 10.0, task_id="task_2", target_resource_id="I1"))
        wm_b.update_peer_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 20.0, task_id="task_1", target_resource_id="I1"))
        wm_b.set_own_state(RobotState(robot_id="amr_02", timestamp=FIXED_TIME, battery_percent=80.0))
        wm_b.update_peer_state(RobotState(robot_id="amr_01", timestamp=FIXED_TIME, battery_percent=60.0))
        wm_b.add_task(Task(task_id="task_1", priority=6))
        wm_b.add_task(Task(task_id="task_2", priority=8))

        # Robot A resolves (amr_01 vs amr_02)
        conflict_a = create_standard_conflict("amr_01", "amr_02")
        decision_a = engine.resolve(conflict_a, wm_a, now=FIXED_TIME)

        # Robot B resolves (amr_02 vs amr_01)
        conflict_b = create_standard_conflict("amr_02", "amr_01")
        decision_b = engine.resolve(conflict_b, wm_b, now=FIXED_TIME)

        # Both MUST select the exact same winner and loser!
        assert decision_a.winner_id == decision_b.winner_id
        assert decision_a.loser_id == decision_b.loser_id

    def test_symmetric_conflict_report_orientation(self, engine: PriorityEngine, wm: WorldModel):
        """Evaluating ConflictReport(A, B) vs ConflictReport(B, A) in same WorldModel yields same winner."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME, target_resource_id="I1"))

        c_ab = create_standard_conflict("amr_01", "amr_02")
        c_ba = create_standard_conflict("amr_02", "amr_01")

        dec_ab = engine.resolve(c_ab, wm, now=FIXED_TIME)
        dec_ba = engine.resolve(c_ba, wm, now=FIXED_TIME)

        assert dec_ab.winner_id == dec_ba.winner_id
        assert dec_ab.loser_id == dec_ba.loser_id

    def test_repeatability_same_input_same_output(self, engine: PriorityEngine, wm: WorldModel):
        """Calling resolve() 100 times on identical state yields bit-for-bit identical PriorityDecision."""
        wm.set_own_intent(RobotIntent(robot_id="amr_01", timestamp=FIXED_TIME - 10.0, target_resource_id="I1"))
        wm.update_peer_intent(RobotIntent(robot_id="amr_02", timestamp=FIXED_TIME - 5.0, target_resource_id="I1"))

        conflict = create_standard_conflict("amr_01", "amr_02")
        first_decision = engine.resolve(conflict, wm, now=FIXED_TIME)

        for _ in range(100):
            d = engine.resolve(conflict, wm, now=FIXED_TIME)
            assert d.winner_id == first_decision.winner_id
            assert d.score_a == first_decision.score_a
            assert d.score_b == first_decision.score_b
            assert d.tie_broken_by_id == first_decision.tie_broken_by_id
