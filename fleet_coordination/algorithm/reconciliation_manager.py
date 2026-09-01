"""
ReconciliationManager — Deterministic Fleet State Reconciliation Engine.
========================================================================

Pure algorithmic engine that deterministically merges divergent WorldModel
state (peer telemetry, intents, shared reservations, and tasks) following
a network partition or recovery event.

ARCHITECTURAL PRINCIPLES:
1. Pure Algorithmic Service: Operates on WorldModel snapshots at reference time 'now'.
2. Decentralized Symmetry: Given identical exchanged messages, every AMR executes
   the exact same tie-breaking logic and converges to the exact same world view.
3. Deterministic Precedence:
   - RobotState: Monotonic timestamp rule.
   - RobotIntent: Monotonic timestamp + active validity window.
   - Reservations: Priority -> Earlier Created Timestamp -> Lexicographic Robot ID.
   - Tasks: Precedence: COMPLETED > IN_PROGRESS > ASSIGNED > BIDDING > ANNOUNCED.
4. ROS-Free: Zero rclpy / ROS 2 / Gazebo imports.
"""

from __future__ import annotations

import math

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.reconciliation import ReconciliationReport
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState
from fleet_coordination.models.task import Task, TaskStatus


# Explicit lifecycle hierarchy ranking for deterministic task conflict resolution
TASK_STATUS_RANK: dict[TaskStatus, int] = {
    TaskStatus.COMPLETED: 5,
    TaskStatus.IN_PROGRESS: 4,
    TaskStatus.ASSIGNED: 3,
    TaskStatus.BIDDING: 2,
    TaskStatus.ANNOUNCED: 1,
    TaskStatus.FAILED: 0,
    TaskStatus.REASSIGNED: 0,
}


class ReconciliationManager:
    """Deterministically resolves divergent WorldModel state following network recovery."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize ReconciliationManager with coordination configuration.

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

    def reconcile_peer_states(
        self,
        incoming_states: list[RobotState],
        world_model: WorldModel,
        now: float,
    ) -> tuple[int, int]:
        """Merge incoming peer telemetry, strictly applying monotonic timestamp ordering.

        Args:
            incoming_states: List of received peer RobotState snapshots.
            world_model: Local WorldModel to update.
            now: Reference timestamp (Unix epoch seconds).

        Returns:
            Tuple of (states_updated_count, stale_rejected_count).

        Raises:
            ValueError: If now is invalid.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        updated = 0
        rejected = 0

        for state in incoming_states:
            if state.robot_id == world_model.robot_id:
                # Never overwrite own local telemetry via peer updates
                rejected += 1
                continue

            success = world_model.update_peer_state(state)
            if success:
                updated += 1
            else:
                rejected += 1

        return updated, rejected

    def reconcile_peer_intents(
        self,
        incoming_intents: list[RobotIntent],
        world_model: WorldModel,
        now: float,
    ) -> tuple[int, int]:
        """Merge incoming peer intents, rejecting expired and stale intents.

        Args:
            incoming_intents: List of received peer RobotIntent objects.
            world_model: Local WorldModel to update.
            now: Reference timestamp.

        Returns:
            Tuple of (intents_updated_count, stale_rejected_count).
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        updated = 0
        rejected = 0

        for intent in incoming_intents:
            if intent.robot_id == world_model.robot_id:
                rejected += 1
                continue

            if intent.is_expired(now):
                rejected += 1
                continue

            success = world_model.update_peer_intent(intent)
            if success:
                updated += 1
            else:
                rejected += 1

        return updated, rejected

    def reconcile_reservations(
        self,
        incoming_reservations: list[Reservation],
        world_model: WorldModel,
        now: float,
    ) -> int:
        """Detect and deterministically resolve overlapping claims on shared resources.

        Resolution Hierarchy for Overlapping Claims:
        1. Higher priority claim wins.
        2. If priority tied (within score_epsilon): earlier created_at timestamp wins.
        3. If created_at tied: lower robot_id wins (lexicographic tie-breaker).
        4. Losing claim is removed from WorldModel.

        Args:
            incoming_reservations: Received Reservation claims from reconnected peers.
            world_model: Local WorldModel to reconcile.
            now: Reference timestamp.

        Returns:
            Number of conflicting reservations resolved.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        # Ingest valid incoming reservations
        for res in incoming_reservations:
            if not res.is_expired(now):
                world_model.add_reservation(res)

        score_epsilon = self._config.priority_weights.score_epsilon
        resolved_conflicts = 0

        # Scan all non-expired reservations for resource overlaps
        all_reservations = [
            r for r in world_model.get_all_reservations().values() if not r.is_expired(now)
        ]

        # Group by resource_id
        by_resource: dict[str, list[Reservation]] = {}
        for r in all_reservations:
            by_resource.setdefault(r.resource_id, []).append(r)

        for resource_id, claims in by_resource.items():
            if len(claims) <= 1:
                continue

            # Check pairwise overlaps
            for i in range(len(claims)):
                for j in range(i + 1, len(claims)):
                    r1 = claims[i]
                    r2 = claims[j]

                    if r1.overlaps_temporally(r2):
                        # Determine winner
                        winner, loser = self._resolve_reservation_conflict(
                            r1, r2, score_epsilon
                        )
                        # Remove loser from WorldModel
                        world_model.remove_reservation(loser.claim_id)
                        resolved_conflicts += 1

        return resolved_conflicts

    def _resolve_reservation_conflict(
        self,
        r1: Reservation,
        r2: Reservation,
        score_epsilon: float,
    ) -> tuple[Reservation, Reservation]:
        """Deterministically resolve a single pairwise reservation conflict."""
        # 1. Higher priority wins
        if abs(r1.priority - r2.priority) > score_epsilon:
            if r1.priority > r2.priority:
                return r1, r2
            return r2, r1

        # 2. Earlier created_at timestamp wins
        if abs(r1.created_at - r2.created_at) > score_epsilon:
            if r1.created_at < r2.created_at:
                return r1, r2
            return r2, r1

        # 3. Lexicographic robot_id tie-breaker
        if r1.robot_id != r2.robot_id:
            if self._config.lower_id_wins_ties:
                if r1.robot_id < r2.robot_id:
                    return r1, r2
                return r2, r1

        # 4. Final claim_id tie-break
        if r1.claim_id < r2.claim_id:
            return r1, r2
        return r2, r1

    def reconcile_tasks(
        self,
        incoming_tasks: list[Task],
        world_model: WorldModel,
        now: float,
    ) -> int:
        """Reconcile task state divergence across partitioned peers.

        Lifecycle Precedence:
        COMPLETED > IN_PROGRESS > ASSIGNED > BIDDING > ANNOUNCED

        Args:
            incoming_tasks: Received Task objects from peers.
            world_model: Local WorldModel to update.
            now: Reference timestamp.

        Returns:
            Number of conflicting tasks resolved/updated.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        reconciled_tasks = 0

        for incoming in incoming_tasks:
            stored = world_model.get_task(incoming.task_id)

            if stored is None:
                world_model.add_task(incoming)
                reconciled_tasks += 1
                continue

            incoming_rank = TASK_STATUS_RANK.get(incoming.status, 0)
            stored_rank = TASK_STATUS_RANK.get(stored.status, 0)

            # Higher status rank wins
            if incoming_rank > stored_rank:
                world_model.add_task(incoming)
                reconciled_tasks += 1
            elif incoming_rank == stored_rank:
                # If equal rank (e.g. both ASSIGNED), break tie by lower assigned_robot
                if incoming.assigned_robot and stored.assigned_robot:
                    if incoming.assigned_robot != stored.assigned_robot:
                        if self._config.lower_id_wins_ties:
                            if incoming.assigned_robot < stored.assigned_robot:
                                world_model.add_task(incoming)
                                reconciled_tasks += 1

        return reconciled_tasks

    def reconcile_fleet_snapshot(
        self,
        incoming_states: list[RobotState],
        incoming_intents: list[RobotIntent],
        incoming_reservations: list[Reservation],
        incoming_tasks: list[Task],
        world_model: WorldModel,
        now: float,
    ) -> ReconciliationReport:
        """Execute full post-recovery reconciliation across all fleet domains.

        Args:
            incoming_states: Peer states.
            incoming_intents: Peer intents.
            incoming_reservations: Peer reservations.
            incoming_tasks: Known fleet tasks.
            world_model: Local WorldModel.
            now: Current reference timestamp.

        Returns:
            ReconciliationReport detailing all actions taken.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        states_upd, states_rej = self.reconcile_peer_states(
            incoming_states, world_model, now
        )
        intents_upd, intents_rej = self.reconcile_peer_intents(
            incoming_intents, world_model, now
        )
        res_resolved = self.reconcile_reservations(
            incoming_reservations, world_model, now
        )
        tasks_resolved = self.reconcile_tasks(
            incoming_tasks, world_model, now
        )

        return ReconciliationReport(
            states_updated=states_upd,
            intents_updated=intents_upd,
            conflicting_reservations_resolved=res_resolved,
            conflicting_tasks_resolved=tasks_resolved,
            stale_records_rejected=states_rej + intents_rej,
            is_clean=True,
            reconciled_at=now,
        )
