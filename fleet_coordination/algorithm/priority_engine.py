"""
PriorityEngine — Pure Algorithmic Priority Arbitration Engine.
==============================================================

Resolves detected coordination conflicts by evaluating competing robots'
state, intent commitment, and task urgency to deterministically determine
which AMR receives priority access to a contested resource.

ARCHITECTURAL PRINCIPLES:
1. Determinism: Given identical fleet information and reference timestamp 'now',
   every robot calculating priority for a conflict produces the exact same winner.
2. Read-Only: PriorityEngine queries WorldModel state without performing mutations.
3. Zero Side-Effects: Resolves conflicts only. Does not grant/deny reservations,
   allocate tasks, or plan motion paths.
4. Epsilon Tie-Breaking: Uses configurable score_epsilon tolerance before invoking
   the deterministic lexicographic robot ID tie-breaker.
5. Intent Commitment Age Proxy: Waiting time is computed as intent commitment age
   (now - intent.timestamp), representing commitment duration rather than physical stop line wait.
"""

from __future__ import annotations

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    PriorityWeights,
)
from fleet_coordination.models.conflict import ConflictReport
from fleet_coordination.models.priority_decision import PriorityDecision
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState
from fleet_coordination.models.task import Task


class PriorityEngine:
    """Pure algorithmic priority arbitration engine for coordination conflicts."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize PriorityEngine with coordination configuration.

        Args:
            config: Coordination configuration containing priority weights and tie-break policy.
                    Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = (
            config if config is not None else CoordinationConfig()
        )

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    def resolve(
        self,
        conflict: ConflictReport,
        world_model: WorldModel,
        now: float,
    ) -> PriorityDecision:
        """Deterministically resolve a coordination conflict between two AMRs.

        Args:
            conflict: The ConflictReport identifying the competing robots and resource.
            world_model: The local robot's WorldModel (read-only).
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            A PriorityDecision with scores, factor breakdowns, winner, and loser.

        Raises:
            ValueError: If now < 0.0, or if either contender has no RobotIntent on record.
        """
        if now < 0.0:
            raise ValueError("Reference time 'now' cannot be negative")

        robot_a_id = conflict.robot_a_id
        robot_b_id = conflict.robot_b_id

        # Verify core coordination intent exists for both contenders
        intent_a = self._get_robot_intent(robot_a_id, world_model)
        intent_b = self._get_robot_intent(robot_b_id, world_model)

        if intent_a is None:
            raise ValueError(
                f"Cannot resolve conflict: contender {robot_a_id!r} has no intent in WorldModel"
            )
        if intent_b is None:
            raise ValueError(
                f"Cannot resolve conflict: contender {robot_b_id!r} has no intent in WorldModel"
            )

        weights = self._config.priority_weights

        # Compute factor scores and composite scores for both contenders
        factors_a = self._compute_factors(robot_a_id, intent_a, world_model, now, weights)
        factors_b = self._compute_factors(robot_b_id, intent_b, world_model, now, weights)

        score_a = self._calculate_composite_score(factors_a, weights)
        score_b = self._calculate_composite_score(factors_b, weights)

        # Deterministic comparison with epsilon tolerance
        delta = abs(score_a - score_b)
        if delta <= weights.score_epsilon:
            # Scores are effectively tied -> deterministic robot ID tie-breaker
            if self._config.lower_id_wins_ties:
                winner_id = min(robot_a_id, robot_b_id)
            else:
                winner_id = max(robot_a_id, robot_b_id)
            loser_id = robot_b_id if winner_id == robot_a_id else robot_a_id
            tie_broken_by_id = True
        elif score_a > score_b:
            winner_id = robot_a_id
            loser_id = robot_b_id
            tie_broken_by_id = False
        else:
            winner_id = robot_b_id
            loser_id = robot_a_id
            tie_broken_by_id = False

        return PriorityDecision(
            conflict_id=conflict.conflict_id,
            robot_a_id=robot_a_id,
            robot_b_id=robot_b_id,
            resource_id=conflict.resource_id,
            score_a=score_a,
            score_b=score_b,
            factors_a=factors_a,
            factors_b=factors_b,
            winner_id=winner_id,
            loser_id=loser_id,
            tie_broken_by_id=tie_broken_by_id,
            decided_at=now,
        )

    # =========================================================================
    # Factor Computation & Scoring
    # =========================================================================

    def _compute_factors(
        self,
        robot_id: str,
        intent: RobotIntent,
        world_model: WorldModel,
        now: float,
        weights: PriorityWeights,
    ) -> dict[str, float]:
        """Compute normalized [0.0, 1.0] factor values for one contender."""
        # 1. Waiting Time Proxy (intent commitment age)
        waiting_age = max(now - intent.timestamp, 0.0)
        max_wait = max(weights.max_wait_seconds, 1.0)
        p_wait = min(waiting_age / max_wait, 1.0)

        # 2. Task Priority & Deadline Urgency
        p_task = 0.0
        p_deadline = 0.0
        if intent.task_id:
            task = world_model.get_task(intent.task_id)
            if task is not None:
                # Intrinsic priority 1..10 normalized to 0.0..1.0
                clamped_task_prio = max(1, min(task.priority, 10))
                p_task = (clamped_task_prio - 1) / 9.0
                p_deadline = task.deadline_urgency(now)

        # 3. Battery Urgency
        p_battery = 0.0
        state = self._get_robot_state(robot_id, world_model)
        if state is not None:
            clamped_battery = max(0.0, min(state.battery_percent, 100.0))
            p_battery = (100.0 - clamped_battery) / 100.0

        return {
            "task_priority": p_task,
            "deadline_urgency": p_deadline,
            "waiting_time": p_wait,
            "battery_urgency": p_battery,
        }

    @staticmethod
    def _calculate_composite_score(
        factors: dict[str, float],
        weights: PriorityWeights,
    ) -> float:
        """Calculate weighted composite score from normalized factor values."""
        return (
            weights.w_task * factors.get("task_priority", 0.0)
            + weights.w_deadline * factors.get("deadline_urgency", 0.0)
            + weights.w_wait * factors.get("waiting_time", 0.0)
            + weights.w_battery * factors.get("battery_urgency", 0.0)
        )

    # =========================================================================
    # Helpers
    # =========================================================================

    @staticmethod
    def _get_robot_intent(robot_id: str, world_model: WorldModel) -> RobotIntent | None:
        """Fetch intent for local or peer robot from WorldModel."""
        if robot_id == world_model.robot_id:
            return world_model.get_own_intent()
        return world_model.get_peer_intent(robot_id)

    @staticmethod
    def _get_robot_state(robot_id: str, world_model: WorldModel) -> RobotState | None:
        """Fetch state for local or peer robot from WorldModel."""
        if robot_id == world_model.robot_id:
            return world_model.get_own_state()
        return world_model.get_peer_state(robot_id)
