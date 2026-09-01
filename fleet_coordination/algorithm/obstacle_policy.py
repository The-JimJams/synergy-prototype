"""
ObstaclePolicy — Spatial Blockage & Contested Intent Evaluator.
==============================================================

Pure algorithmic evaluator for spatial blockages and aisle obstructions.
Inspects the local WorldModel to identify which warehouse resources are
currently blocked and which AMRs in the fleet have intents targeting them.

ARCHITECTURAL PRINCIPLES:
1. Pure Stateless Service: Holds no mutable state. Evaluates local WorldModel
   at explicit reference time 'now'.
2. Read-Only Core: Never mutates WorldModel, RobotIntent, or Reservations.
3. Decision-Only: Identifies affected resources and AMRs without commanding motion.
4. Deterministic: Given the same WorldModel snapshot and 'now', all AMRs
   reach identical blockage determinations.
5. ROS-Free: Zero rclpy / ROS 2 / Gazebo imports.
"""

from __future__ import annotations

import math

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.robot_intent import RobotIntent


class ObstaclePolicy:
    """Evaluates obstacle validity and identifies contested/blocked fleet intents."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize ObstaclePolicy with coordination configuration.

        Args:
            config: Coordination configuration. Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = (
            config if config is not None else CoordinationConfig()
        )

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    def is_resource_blocked(
        self,
        resource_id: str | None,
        world_model: WorldModel,
        now: float,
    ) -> bool:
        """Check if a specific named resource has an active, non-expired obstacle.

        Args:
            resource_id: Named resource identifier (e.g. "AISLE_CENTRAL", "I1").
            world_model: Local WorldModel to inspect.
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            True if an active obstacle blocks the resource, False otherwise.

        Raises:
            ValueError: If now is NaN, infinite, or negative.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        if not resource_id:
            return False

        active_obstacles = world_model.get_active_obstacles(now)
        return any(obs.resource_id == resource_id for obs in active_obstacles)

    def get_active_blocked_resources(
        self,
        world_model: WorldModel,
        now: float,
    ) -> set[str]:
        """Return a set of all currently blocked resource IDs.

        Args:
            world_model: Local WorldModel to inspect.
            now: Current reference timestamp.

        Returns:
            Set of resource IDs that are currently obstructed.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        active_obstacles = world_model.get_active_obstacles(now)
        return {obs.resource_id for obs in active_obstacles}

    def is_intent_affected(
        self,
        intent: RobotIntent | None,
        world_model: WorldModel,
        now: float,
    ) -> bool:
        """Check if a robot's planned intent targets a currently blocked resource.

        Args:
            intent: RobotIntent to check (or None).
            world_model: Local WorldModel to inspect.
            now: Current reference timestamp.

        Returns:
            True if the intent's target_resource_id is blocked, False otherwise.
        """
        if intent is None or intent.target_resource_id is None:
            return False

        return self.is_resource_blocked(intent.target_resource_id, world_model, now)

    def identify_affected_robots(
        self,
        world_model: WorldModel,
        now: float,
    ) -> dict[str, str]:
        """Find all AMRs (own + peers) whose active intents target blocked resources.

        Args:
            world_model: Local WorldModel to inspect.
            now: Current reference timestamp.

        Returns:
            Dictionary mapping robot_id -> blocked_resource_id.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        affected: dict[str, str] = {}

        # 1. Check own intent
        own_intent = world_model.get_own_intent()
        if own_intent is not None and own_intent.target_resource_id is not None:
            if self.is_resource_blocked(own_intent.target_resource_id, world_model, now):
                affected[world_model.robot_id] = own_intent.target_resource_id

        # 2. Check active peer intents
        active_peer_intents = world_model.get_active_peer_intents(now)
        for peer_id in sorted(active_peer_intents.keys()):
            peer_intent = active_peer_intents[peer_id]
            if peer_intent.target_resource_id is not None:
                if self.is_resource_blocked(peer_intent.target_resource_id, world_model, now):
                    affected[peer_id] = peer_intent.target_resource_id

        return affected
