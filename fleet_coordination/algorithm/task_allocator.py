"""
TaskAllocator — Decentralized Task Allocation & Bidding Algorithm
==================================================================

Pure algorithmic task evaluator for decentralized multi-AMR fleets.
Operates on the local robot's WorldModel to deterministically evaluate,
bid on, and assign warehouse tasks across candidate robots without a
centralized fleet coordinator or auction server.

ARCHITECTURAL PRINCIPLES:
1. Stateless Service: TaskAllocator holds no state of its own.
   All data is read from the provided Task and WorldModel.
2. Read-Only Core: evaluate_task() is strictly read-only. It NEVER mutates
   _own_state, _peer_states, _own_intent, _peer_intents, _reservations,
   or _tasks.
3. Explicit Task Assignment: assign_task() explicitly mutates only
   task.status and task.assigned_robot in WorldModel._tasks. Robot state
   and intent are never touched.
4. Determinism (INV-2): Given identical WorldModel snapshots, task metadata,
   and reference timestamp 'now', every robot calculates the exact same
   winner.
5. Deterministic Tie-Breaking (INV-3): When top bids differ by <= score_epsilon,
   ties are broken strictly by lexicographic robot ID according to the
   configured lower_id_wins_ties policy.
6. Zero Side-Effects: Does NOT perform spatial conflict detection (Phase 3),
   priority conflict resolution (Phase 4), or reservation lifecycle
   management (Phase 5).
7. ROS-Free: Zero rclpy / ROS 2 / Gazebo / Nav2 imports.

DISTRIBUTED CONSISTENCY NOTE:
  Local WorldModels are eventually-consistent. If two robots evaluate an
  announced task under asymmetric or stale network telemetry, they may
  temporarily select different winners locally. This is an intrinsic
  distributed consistency property. The conflict is reconciled when peer
  intent/task broadcasts are received on the subsequent coordination cycle.
"""

from __future__ import annotations

import math
import time

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    TaskBidWeights,
)
from fleet_coordination.models.assignment_decision import AssignmentDecision
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task, TaskStatus
from fleet_coordination.models.task_bid import TaskBid


class TaskAllocator:
    """Pure algorithmic decentralized task allocator and bidding engine."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize TaskAllocator with coordination configuration.

        Args:
            config: Coordination configuration containing task weights and tie-break policy.
                    Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = (
            config if config is not None else CoordinationConfig()
        )

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    # =========================================================================
    # Public API — Read-Only Evaluation
    # =========================================================================

    def evaluate_task(
        self,
        task: Task,
        world_model: WorldModel,
        now: float = 0.0,
    ) -> AssignmentDecision:
        """Evaluate an announced task and deterministically determine the winner.

        This method is strictly read-only and has zero side-effects on WorldModel.

        Args:
            task:         The candidate Task to evaluate.
            world_model:  The local WorldModel to inspect for fleet state.
            now:          Current reference time (Unix epoch seconds).

        Returns:
            AssignmentDecision containing the winning robot ID, score,
            breakdown of all bids, and reason code.
        """
        # ------------------------------------------------------------------
        # Step 0 — Finite-number & validity validation
        # ------------------------------------------------------------------
        if not math.isfinite(now) or now < 0.0:
            return AssignmentDecision(
                task_id=task.task_id,
                winner_id=None,
                winner_score=0.0,
                all_bids={},
                accepted=False,
                reason="INVALID_TIMESTAMP",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Step 1 — Task Assignability Guard
        # ------------------------------------------------------------------
        if not task.is_assignable():
            reason = "ALREADY_ASSIGNED" if task.status in (TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED) else "TASK_NOT_ASSIGNABLE"
            return AssignmentDecision(
                task_id=task.task_id,
                winner_id=None,
                winner_score=0.0,
                all_bids={},
                accepted=False,
                reason=reason,
                decided_at=time.time(),
            )

        weights = self._config.task_bid_weights

        # ------------------------------------------------------------------
        # Step 2 — Gather Candidate Robot States
        # ------------------------------------------------------------------
        candidate_states: dict[str, RobotState] = {}

        # 2a. Own state (local robot)
        own_state = world_model.get_own_state()
        if own_state is not None:
            candidate_states[world_model.robot_id] = own_state

        # 2b. Peer states (include all known peers; freshness checked in eligibility)
        for peer_id, peer_state in world_model.get_all_peer_states().items():
            candidate_states[peer_id] = peer_state

        if not candidate_states:
            return AssignmentDecision(
                task_id=task.task_id,
                winner_id=None,
                winner_score=0.0,
                all_bids={},
                accepted=False,
                reason="NO_ELIGIBLE_ROBOT",
                decided_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Step 3 — Compute Bids & Check Eligibility
        # ------------------------------------------------------------------
        all_bids: dict[str, TaskBid] = {}
        eligible_bids: list[TaskBid] = []

        # Sort candidate IDs to ensure evaluation order independence
        sorted_robot_ids = sorted(candidate_states.keys())

        for robot_id in sorted_robot_ids:
            state = candidate_states[robot_id]
            is_peer = (robot_id != world_model.robot_id)

            # Check eligibility
            is_eligible, ineligibility_reason = self._check_eligibility(
                state=state,
                is_peer=is_peer,
                weights=weights,
                now=now,
            )

            # Compute normalized factors
            factors = self._compute_factors(state=state, task=task, now=now)

            # Compute composite score
            score = self._compute_composite_score(factors, weights) if is_eligible else 0.0

            bid = TaskBid(
                task_id=task.task_id,
                robot_id=robot_id,
                bid_score=score,
                eligible=is_eligible,
                factors=factors,
                ineligibility_reason=ineligibility_reason,
            )
            all_bids[robot_id] = bid

            if is_eligible:
                eligible_bids.append(bid)

        # ------------------------------------------------------------------
        # Step 4 — Winner Selection & Deterministic Tie-Breaking
        # ------------------------------------------------------------------
        if not eligible_bids:
            return AssignmentDecision(
                task_id=task.task_id,
                winner_id=None,
                winner_score=0.0,
                all_bids=all_bids,
                accepted=False,
                reason="NO_ELIGIBLE_ROBOT",
                decided_at=time.time(),
            )

        max_score = max(b.bid_score for b in eligible_bids)

        # Find all eligible candidates within epsilon tolerance
        tied_bids = [
            b for b in eligible_bids
            if abs(b.bid_score - max_score) <= weights.score_epsilon
        ]

        if len(tied_bids) == 1:
            winner = tied_bids[0]
            tie_broken_by_id = False
        else:
            # Deterministic tie-breaker by robot ID
            if self._config.lower_id_wins_ties:
                winner = min(tied_bids, key=lambda b: b.robot_id)
            else:
                winner = max(tied_bids, key=lambda b: b.robot_id)
            tie_broken_by_id = True

        return AssignmentDecision(
            task_id=task.task_id,
            winner_id=winner.robot_id,
            winner_score=winner.bid_score,
            all_bids=all_bids,
            accepted=True,
            reason="ASSIGNED",
            tie_broken_by_id=tie_broken_by_id,
            decided_at=time.time(),
        )

    # =========================================================================
    # Public API — Explicit Task Mutation
    # =========================================================================

    def assign_task(
        self,
        task_id: str,
        world_model: WorldModel,
        decision: AssignmentDecision,
    ) -> bool:
        """Explicitly apply an accepted AssignmentDecision to WorldModel tasks.

        This is the ONLY operation that mutates WorldModel, modifying strictly
        task.status and task.assigned_robot. Own/peer states, intents, and
        reservations are NEVER touched.

        Args:
            task_id:      Unique identifier of the task to assign.
            world_model:  The WorldModel containing the task.
            decision:     The AssignmentDecision granting the assignment.

        Returns:
            True if the task was found, was assignable, and was successfully
            assigned. False otherwise.
        """
        if not decision.accepted or decision.winner_id is None:
            return False

        if decision.task_id != task_id:
            return False

        task = world_model.get_task(task_id)
        if task is None:
            return False

        if not task.is_assignable():
            return False

        # Apply assignment mutation
        task.status = TaskStatus.ASSIGNED
        task.assigned_robot = decision.winner_id
        world_model.add_task(task)
        return True

    # =========================================================================
    # Internal Helpers — Eligibility & Scoring
    # =========================================================================

    def _check_eligibility(
        self,
        state: RobotState,
        is_peer: bool,
        weights: TaskBidWeights,
        now: float,
    ) -> tuple[bool, str | None]:
        """Check if a robot satisfies all eligibility constraints for bidding."""
        # 1. Peer state freshness
        if is_peer:
            max_age = self._config.timeouts.peer_state_max_age_seconds
            if state.age(now) > max_age:
                return False, "STALE_TELEMETRY"

        # 2. Operational status (must be IDLE or WAITING)
        if not state.is_available():
            return False, f"STATUS_{state.status.name}"

        # 3. Capacity (must not already have an active task)
        if state.current_task_id is not None:
            return False, "ALREADY_ASSIGNED_TASK"

        # 4. Battery threshold
        if state.battery_percent < weights.min_battery_percent:
            return False, "LOW_BATTERY"

        return True, None

    @staticmethod
    def _compute_factors(
        state: RobotState,
        task: Task,
        now: float,
    ) -> dict[str, float]:
        """Compute normalized [0.0, 1.0] factor components for a bid."""
        # Battery factor: higher battery -> higher score
        clamped_battery = max(0.0, min(state.battery_percent, 100.0))
        battery_factor = clamped_battery / 100.0

        # Task priority factor: 1..10 normalized to 0.0..1.0
        clamped_priority = max(1, min(task.priority, 10))
        priority_factor = (clamped_priority - 1) / 9.0

        # Deadline factor: higher urgency -> higher score
        deadline_factor = task.deadline_urgency(now)

        return {
            "battery_factor": battery_factor,
            "priority_factor": priority_factor,
            "deadline_factor": deadline_factor,
        }

    @staticmethod
    def _compute_composite_score(
        factors: dict[str, float],
        weights: TaskBidWeights,
    ) -> float:
        """Calculate weighted composite score normalized by total weights."""
        w_batt = weights.w_battery
        w_prio = weights.w_priority
        w_dead = weights.w_deadline
        total_w = w_batt + w_prio + w_dead

        numerator = (
            w_batt * factors.get("battery_factor", 0.0)
            + w_prio * factors.get("priority_factor", 0.0)
            + w_dead * factors.get("deadline_factor", 0.0)
        )
        if total_w <= 0.0:
            return 0.0
        return numerator / total_w
