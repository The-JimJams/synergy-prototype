"""
RerouteEvaluator — Deterministic Alternative Route Evaluator.
============================================================

Pure algorithmic decision engine that evaluates whether an AMR's planned
trajectory or target corridor is obstructed by an active obstacle, and
deterministically selects a viable alternative route candidate.

ARCHITECTURAL PRINCIPLES:
1. Pure Stateless Service: Holds no persistent state. All evaluations are
   derived from the provided WorldModel at explicit reference time 'now'.
2. Decision-Only: Returns a RerouteDecision recommendation.
   DOES NOT mutate RobotIntent, Reservations, or Tasks.
   DOES NOT invoke ReservationManager or TaskAllocator.
   DOES NOT command robot velocities or perform path planning.
3. Determinism: Given identical WorldModel state, available alternatives,
   and reference time 'now', produces identical RerouteDecision output.
4. ROS-Free: Zero rclpy / ROS 2 / Gazebo / Nav2 imports.
"""

from __future__ import annotations

import math

from fleet_coordination.algorithm.obstacle_policy import ObstaclePolicy
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.reroute_decision import RerouteDecision


class RerouteEvaluator:
    """Evaluates alternative route candidates when an AMR's route is obstructed."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize RerouteEvaluator with coordination configuration.

        Args:
            config: Coordination configuration. Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = (
            config if config is not None else CoordinationConfig()
        )
        self._obstacle_policy: ObstaclePolicy = ObstaclePolicy(config=self._config)

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    def evaluate_reroute(
        self,
        robot_id: str,
        world_model: WorldModel,
        available_alternatives: list[str],
        now: float,
    ) -> RerouteDecision:
        """Deterministically evaluate whether an alternative route is required and available.

        Evaluation Steps:
        1. Retrieve the robot's active intent (own or peer).
        2. Check if the intent has an active target_resource_id. If none -> INTENT_UNAFFECTED.
        3. Check if target_resource_id is blocked by an active obstacle.
           - If not blocked -> reroute_required=False, reason="INTENT_UNAFFECTED".
        4. If blocked, filter available_alternatives by removing any alternative that
           is also blocked by an active obstacle.
        5. If no viable alternatives remain -> reroute_required=True, alternative=None,
           reason="NO_ALTERNATIVE_ROUTE".
        6. If viable alternatives exist, select deterministically (using preferred
           order in config if configured, else lexicographic sort) ->
           reroute_required=True, alternative=winner, reason="REROUTE_SUGGESTED".

        Args:
            robot_id: Identifier of the AMR being evaluated.
            world_model: Local WorldModel to inspect.
            available_alternatives: Candidate alternative corridor/resource IDs.
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            RerouteDecision detailing whether rerouting is required and the suggested alternative.

        Raises:
            ValueError: If now is NaN, infinite, or negative.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        if not robot_id:
            return RerouteDecision(
                robot_id="",
                blocked_resource_id="",
                reroute_required=False,
                alternative_resource_id=None,
                reason="INVALID_ROBOT_ID",
                decided_at=now,
            )

        # 1. Retrieve the target robot's active intent
        if robot_id == world_model.robot_id:
            intent = world_model.get_own_intent()
        else:
            intent = world_model.get_peer_intent(robot_id)

        if intent is None or intent.target_resource_id is None:
            return RerouteDecision(
                robot_id=robot_id,
                blocked_resource_id="",
                reroute_required=False,
                alternative_resource_id=None,
                reason="NO_ACTIVE_INTENT",
                decided_at=now,
            )

        target_resource = intent.target_resource_id

        # 2. Check if target resource is blocked
        is_blocked = self._obstacle_policy.is_resource_blocked(
            target_resource, world_model, now
        )
        if not is_blocked:
            return RerouteDecision(
                robot_id=robot_id,
                blocked_resource_id=target_resource,
                reroute_required=False,
                alternative_resource_id=None,
                reason="INTENT_UNAFFECTED",
                decided_at=now,
            )

        # 3. Filter viable alternative candidates
        viable_alternatives: list[str] = []
        for alt in available_alternatives:
            if alt and alt != target_resource:
                if not self._obstacle_policy.is_resource_blocked(alt, world_model, now):
                    viable_alternatives.append(alt)

        # 4. Handle no viable alternative
        if not viable_alternatives:
            return RerouteDecision(
                robot_id=robot_id,
                blocked_resource_id=target_resource,
                reroute_required=True,
                alternative_resource_id=None,
                reason="NO_ALTERNATIVE_ROUTE",
                decided_at=now,
            )

        # 5. Deterministic selection among viable alternatives
        winner_alternative: str | None = None

        # Check configured preference list first
        preferred = self._config.obstacle.preferred_alternatives
        for pref in preferred:
            if pref in viable_alternatives:
                winner_alternative = pref
                break

        # Fallback to lexicographic sort
        if winner_alternative is None:
            winner_alternative = sorted(viable_alternatives)[0]

        return RerouteDecision(
            robot_id=robot_id,
            blocked_resource_id=target_resource,
            reroute_required=True,
            alternative_resource_id=winner_alternative,
            reason="REROUTE_SUGGESTED",
            decided_at=now,
        )
