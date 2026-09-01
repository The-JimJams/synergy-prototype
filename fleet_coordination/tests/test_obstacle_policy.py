"""
Unit tests for Obstacle model, WorldModel obstacle storage, ObstaclePolicy, and RerouteEvaluator.
=================================================================================================

Validates spatial obstacle representation, query-time filtering, affected intent detection,
deterministic alternative route recommendation, and strict non-mutation invariants.
"""

from __future__ import annotations

import math
import pytest

from fleet_coordination.algorithm.obstacle_policy import ObstaclePolicy
from fleet_coordination.algorithm.reroute_evaluator import RerouteEvaluator
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    ObstacleConfig,
)
from fleet_coordination.models.obstacle import Obstacle
from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.reroute_decision import RerouteDecision
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState
from fleet_coordination.models.task import Task, TaskStatus


FIXED_TIME = 1000.0


@pytest.fixture
def config() -> CoordinationConfig:
    return CoordinationConfig(
        obstacle=ObstacleConfig(
            default_obstacle_duration_seconds=60.0,
            preferred_alternatives=["AISLE_WEST", "AISLE_EAST"],
        )
    )


@pytest.fixture
def world_model(config: CoordinationConfig) -> WorldModel:
    return WorldModel(robot_id="amr_a", config=config)


@pytest.fixture
def policy(config: CoordinationConfig) -> ObstaclePolicy:
    return ObstaclePolicy(config=config)


@pytest.fixture
def evaluator(config: CoordinationConfig) -> RerouteEvaluator:
    return RerouteEvaluator(config=config)


# =============================================================================
# 1. Obstacle Data Model Tests
# =============================================================================

class TestObstacleModel:
    """Tests creation, validation, and lifecycle methods of Obstacle dataclass."""

    def test_obstacle_creation_valid(self) -> None:
        obs = Obstacle(
            obstacle_id="obs_1",
            resource_id="AISLE_CENTRAL",
            detected_at=FIXED_TIME,
            valid_until=FIXED_TIME + 60.0,
            location=Pose2D(0.0, 3.3, 0.0),
            is_active=True,
            reporter_id="amr_b",
        )
        assert obs.obstacle_id == "obs_1"
        assert obs.resource_id == "AISLE_CENTRAL"
        assert obs.is_blocking(now=FIXED_TIME + 10.0) is True
        assert obs.is_expired(now=FIXED_TIME + 10.0) is False

    def test_obstacle_validation_errors(self) -> None:
        with pytest.raises(ValueError, match="obstacle_id must be a non-empty string"):
            Obstacle(obstacle_id="", resource_id="AISLE_1")

        with pytest.raises(ValueError, match="resource_id must be a non-empty string"):
            Obstacle(obstacle_id="obs_1", resource_id="")

        with pytest.raises(ValueError, match="valid_until cannot be negative"):
            Obstacle(obstacle_id="obs_1", resource_id="AISLE_1", valid_until=-5.0)

    def test_obstacle_is_blocking_lifecycle(self) -> None:
        # 1. Active and unexpired -> blocking
        obs = Obstacle(obstacle_id="obs_1", resource_id="I1", valid_until=FIXED_TIME + 30.0)
        assert obs.is_blocking(now=FIXED_TIME) is True

        # 2. Expired -> not blocking
        assert obs.is_expired(now=FIXED_TIME + 30.1) is True
        assert obs.is_blocking(now=FIXED_TIME + 30.1) is False

        # 3. Explicitly deactivated -> not blocking even if within validity window
        obs.is_active = False
        assert obs.is_blocking(now=FIXED_TIME) is False

    def test_obstacle_zero_valid_until_never_expires(self) -> None:
        obs = Obstacle(obstacle_id="obs_perm", resource_id="ZONE_A", valid_until=0.0)
        assert obs.is_expired(now=FIXED_TIME + 100000.0) is False
        assert obs.is_blocking(now=FIXED_TIME + 100000.0) is True


# =============================================================================
# 2. WorldModel Obstacle Storage & Garbage Collection Tests
# =============================================================================

class TestWorldModelObstacles:
    """Tests CRUD and query-time filtering of obstacles inside WorldModel."""

    def test_world_model_obstacle_crud(self, world_model: WorldModel) -> None:
        obs1 = Obstacle(obstacle_id="obs_1", resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0)
        obs2 = Obstacle(obstacle_id="obs_2", resource_id="I1", valid_until=FIXED_TIME + 60.0)

        world_model.add_obstacle(obs1)
        world_model.add_obstacle(obs2)

        assert world_model.get_obstacle("obs_1") == obs1
        assert world_model.get_obstacle("obs_2") == obs2
        assert len(world_model.get_all_obstacles()) == 2

        # Remove obstacle
        assert world_model.remove_obstacle("obs_1") is True
        assert world_model.get_obstacle("obs_1") is None
        assert world_model.remove_obstacle("obs_1") is False

    def test_get_active_obstacles_filters_expired(self, world_model: WorldModel) -> None:
        obs_active = Obstacle(obstacle_id="obs_act", resource_id="AISLE_1", valid_until=FIXED_TIME + 30.0)
        obs_expired = Obstacle(obstacle_id="obs_exp", resource_id="AISLE_2", valid_until=FIXED_TIME - 5.0)
        obs_inactive = Obstacle(obstacle_id="obs_inact", resource_id="AISLE_3", valid_until=FIXED_TIME + 30.0, is_active=False)

        world_model.add_obstacle(obs_active)
        world_model.add_obstacle(obs_expired)
        world_model.add_obstacle(obs_inactive)

        active = world_model.get_active_obstacles(now=FIXED_TIME)
        assert len(active) == 1
        assert active[0].obstacle_id == "obs_act"

    def test_cleanup_expired_purges_obstacles(self, world_model: WorldModel) -> None:
        obs_active = Obstacle(obstacle_id="obs_act", resource_id="AISLE_1", valid_until=FIXED_TIME + 30.0)
        obs_expired = Obstacle(obstacle_id="obs_exp", resource_id="AISLE_2", valid_until=FIXED_TIME - 5.0)

        world_model.add_obstacle(obs_active)
        world_model.add_obstacle(obs_expired)

        counts = world_model.cleanup_expired(now=FIXED_TIME)
        assert counts["obstacles_removed"] == 1
        assert world_model.get_obstacle("obs_exp") is None
        assert world_model.get_obstacle("obs_act") is not None


# =============================================================================
# 3. ObstaclePolicy Decision Tests
# =============================================================================

class TestObstaclePolicy:
    """Tests blockage evaluation and affected robot intent detection."""

    def test_is_resource_blocked(self, policy: ObstaclePolicy, world_model: WorldModel) -> None:
        world_model.add_obstacle(
            Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0)
        )

        assert policy.is_resource_blocked("AISLE_CENTRAL", world_model, now=FIXED_TIME) is True
        assert policy.is_resource_blocked("AISLE_WEST", world_model, now=FIXED_TIME) is False
        assert policy.is_resource_blocked("", world_model, now=FIXED_TIME) is False

    def test_is_resource_blocked_with_expired_obstacle(
        self, policy: ObstaclePolicy, world_model: WorldModel
    ) -> None:
        world_model.add_obstacle(
            Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME - 10.0)
        )
        assert policy.is_resource_blocked("AISLE_CENTRAL", world_model, now=FIXED_TIME) is False

    def test_get_active_blocked_resources(
        self, policy: ObstaclePolicy, world_model: WorldModel
    ) -> None:
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.add_obstacle(Obstacle("obs_2", "I1", valid_until=FIXED_TIME + 60.0))
        world_model.add_obstacle(Obstacle("obs_3", "AISLE_EAST", valid_until=FIXED_TIME - 1.0))

        blocked = policy.get_active_blocked_resources(world_model, now=FIXED_TIME)
        assert blocked == {"AISLE_CENTRAL", "I1"}

    def test_is_intent_affected(
        self, policy: ObstaclePolicy, world_model: WorldModel
    ) -> None:
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))

        intent_affected = RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL")
        intent_safe = RobotIntent("amr_a", target_resource_id="AISLE_WEST")
        intent_no_res = RobotIntent("amr_a", target_resource_id=None)

        assert policy.is_intent_affected(intent_affected, world_model, now=FIXED_TIME) is True
        assert policy.is_intent_affected(intent_safe, world_model, now=FIXED_TIME) is False
        assert policy.is_intent_affected(intent_no_res, world_model, now=FIXED_TIME) is False
        assert policy.is_intent_affected(None, world_model, now=FIXED_TIME) is False

    def test_identify_affected_robots_multi_peer(
        self, policy: ObstaclePolicy, world_model: WorldModel
    ) -> None:
        # Setup: Block AISLE_CENTRAL
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))

        # Own intent (amr_a): targets AISLE_CENTRAL -> affected
        world_model.set_own_intent(
            RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0)
        )

        # Peer intent (amr_b): targets AISLE_CENTRAL -> affected
        world_model.update_peer_intent(
            RobotIntent("amr_b", timestamp=FIXED_TIME, target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0)
        )

        # Peer intent (amr_c): targets AISLE_WEST -> not affected
        world_model.update_peer_intent(
            RobotIntent("amr_c", timestamp=FIXED_TIME, target_resource_id="AISLE_WEST", valid_until=FIXED_TIME + 30.0)
        )

        affected = policy.identify_affected_robots(world_model, now=FIXED_TIME)
        assert affected == {"amr_a": "AISLE_CENTRAL", "amr_b": "AISLE_CENTRAL"}


# =============================================================================
# 4. RerouteEvaluator Decision & Alternative Selection Tests
# =============================================================================

class TestRerouteEvaluator:
    """Tests RerouteEvaluator alternative route decisions."""

    def test_no_reroute_when_intent_unaffected(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # Obstacle is on AISLE_CENTRAL, but robot intends AISLE_WEST
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.set_own_intent(RobotIntent("amr_a", target_resource_id="AISLE_WEST", valid_until=FIXED_TIME + 30.0))

        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_WEST", "AISLE_EAST"], now=FIXED_TIME
        )
        assert decision.reroute_required is False
        assert decision.alternative_resource_id is None
        assert decision.reason == "INTENT_UNAFFECTED"

    def test_reroute_suggested_with_configured_preferred_alternative(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # Obstacle blocks AISLE_CENTRAL; alternatives: AISLE_EAST, AISLE_WEST
        # Preferred in config: ["AISLE_WEST", "AISLE_EAST"] -> AISLE_WEST should win
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.set_own_intent(RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0))

        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_EAST", "AISLE_WEST"], now=FIXED_TIME
        )
        assert decision.reroute_required is True
        assert decision.alternative_resource_id == "AISLE_WEST"
        assert decision.reason == "REROUTE_SUGGESTED"
        assert decision.is_reroute_available() is True

    def test_reroute_filters_blocked_alternatives(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # Target AISLE_CENTRAL is blocked
        # Preferred AISLE_WEST is ALSO blocked
        # Only AISLE_EAST is clear -> AISLE_EAST should be chosen
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.add_obstacle(Obstacle("obs_2", "AISLE_WEST", valid_until=FIXED_TIME + 60.0))
        world_model.set_own_intent(RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0))

        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_WEST", "AISLE_EAST"], now=FIXED_TIME
        )
        assert decision.reroute_required is True
        assert decision.alternative_resource_id == "AISLE_EAST"
        assert decision.reason == "REROUTE_SUGGESTED"

    def test_no_alternative_route_when_all_alternatives_blocked(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # AISLE_CENTRAL blocked, AISLE_WEST blocked, AISLE_EAST blocked
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.add_obstacle(Obstacle("obs_2", "AISLE_WEST", valid_until=FIXED_TIME + 60.0))
        world_model.add_obstacle(Obstacle("obs_3", "AISLE_EAST", valid_until=FIXED_TIME + 60.0))
        world_model.set_own_intent(RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0))

        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_WEST", "AISLE_EAST"], now=FIXED_TIME
        )
        assert decision.reroute_required is True
        assert decision.alternative_resource_id is None
        assert decision.reason == "NO_ALTERNATIVE_ROUTE"
        assert decision.is_reroute_available() is False

    def test_empty_alternatives_list_yields_no_alternative(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.set_own_intent(RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0))

        decision = evaluator.evaluate_reroute("amr_a", world_model, available_alternatives=[], now=FIXED_TIME)
        assert decision.reroute_required is True
        assert decision.alternative_resource_id is None
        assert decision.reason == "NO_ALTERNATIVE_ROUTE"

    def test_missing_or_empty_intent_handled_safely(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # No intent set
        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_WEST"], now=FIXED_TIME
        )
        assert decision.reroute_required is False
        assert decision.reason == "NO_ACTIVE_INTENT"

    def test_peer_robot_reroute_evaluation(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))
        world_model.update_peer_intent(
            RobotIntent("amr_b", timestamp=FIXED_TIME, target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0)
        )

        decision = evaluator.evaluate_reroute(
            "amr_b", world_model, available_alternatives=["AISLE_WEST", "AISLE_EAST"], now=FIXED_TIME
        )
        assert decision.robot_id == "amr_b"
        assert decision.reroute_required is True
        assert decision.alternative_resource_id == "AISLE_WEST"


# =============================================================================
# 5. Non-Mutation & Separation of Concerns Tests
# =============================================================================

class TestSeparationOfConcerns:
    """Verifies that ObstaclePolicy and RerouteEvaluator are strictly read-only decision services."""

    def test_evaluator_does_not_mutate_world_model(
        self, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        # Setup intent, reservation, and task
        original_intent = RobotIntent("amr_a", target_resource_id="AISLE_CENTRAL", valid_until=FIXED_TIME + 30.0)
        world_model.set_own_intent(original_intent)

        res = Reservation(
            resource_id="AISLE_CENTRAL",
            robot_id="amr_a",
            start_time=FIXED_TIME,
            end_time=FIXED_TIME + 30.0,
            priority=1.0,
            claim_id="claim_1",
            expires_at=FIXED_TIME + 60.0,
        )
        world_model.add_reservation(res)

        task = Task(task_id="task_1", assigned_robot="amr_a", status=TaskStatus.IN_PROGRESS)
        world_model.add_task(task)

        # Add blockage
        world_model.add_obstacle(Obstacle("obs_1", "AISLE_CENTRAL", valid_until=FIXED_TIME + 60.0))

        # Run reroute evaluation
        decision = evaluator.evaluate_reroute(
            "amr_a", world_model, available_alternatives=["AISLE_WEST"], now=FIXED_TIME
        )
        assert decision.reroute_required is True

        # CRITICAL INVARIANTS: State, intent, reservations, and tasks remain UNCHANGED by evaluator
        assert world_model.get_own_intent() == original_intent
        assert world_model.get_reservation("claim_1") == res
        assert world_model.get_task("task_1").status == TaskStatus.IN_PROGRESS  # type: ignore


# =============================================================================
# 6. Numeric Safety & Validation Tests
# =============================================================================

class TestNumericSafety:
    """Tests validation of invalid timestamps."""

    def test_invalid_now_raises_value_error(
        self, policy: ObstaclePolicy, evaluator: RerouteEvaluator, world_model: WorldModel
    ) -> None:
        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            policy.is_resource_blocked("AISLE_1", world_model, now=-1.0)

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            policy.get_active_blocked_resources(world_model, now=float("nan"))

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            evaluator.evaluate_reroute("amr_a", world_model, ["AISLE_WEST"], now=float("inf"))
