"""
FailureDetector — Heartbeat Monitoring & Fault Recovery Algorithm.
===================================================================

Pure algorithmic heartbeat evaluator for decentralized multi-AMR fleets.
Operates on the local robot's WorldModel to deterministically evaluate
peer telemetry health and reclaim active tasks from failed robots.

ARCHITECTURAL PRINCIPLES:
1. Stateless Service: FailureDetector holds no persistent state. All telemetry
   is inspected from the provided WorldModel at explicit reference time 'now'.
2. Read-Only Core: evaluate_peer() and evaluate_fleet() are strictly read-only.
3. Explicit Task Reclaim: reclaim_failed_robot_tasks() mutates strictly
   task.status in WorldModel._tasks (setting it to TaskStatus.FAILED), enabling
   TaskAllocator to reassign the task to a healthy peer.
4. Determinism: Given identical WorldModel snapshots and timestamp 'now',
   every robot calculates identical health classifications and winner rankings.
5. ROS-Free: Zero rclpy / ROS 2 / Gazebo imports.
"""

from __future__ import annotations

import math
import time

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.health import (
    FleetHealthReport,
    PeerHealthAssessment,
    PeerHealthStatus,
)
from fleet_coordination.models.robot_state import RobotStatus
from fleet_coordination.models.task import TaskStatus


class FailureDetector:
    """Pure algorithmic heartbeat monitor and peer failure detector."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize FailureDetector with coordination configuration.

        Args:
            config: Coordination configuration containing timeout thresholds.
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
    # Public API — Read-Only Health Evaluation
    # =========================================================================

    def evaluate_peer(
        self,
        peer_id: str,
        world_model: WorldModel,
        now: float,
    ) -> PeerHealthAssessment | None:
        """Evaluate the health of a specific peer AMR at reference time 'now'.

        Health Evaluation Rules:
        - age <= heartbeat_suspect_timeout_seconds (3.0s) -> HEALTHY
        - 3.0s < age <= heartbeat_failure_timeout_seconds (10.0s) -> SUSPECTED
        - age > heartbeat_failure_timeout_seconds (10.0s) -> FAILED
        - Broadcast status FAILED or EMERGENCY_STOP -> FAILED immediately

        Args:
            peer_id: Unique string identifier of the peer robot.
            world_model: Local WorldModel containing peer states.
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            PeerHealthAssessment snapshot, or None if peer is unknown.

        Raises:
            ValueError: If now is NaN, infinite, or negative.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        state = world_model.get_peer_state(peer_id)
        if state is None:
            return None

        # Clamp age to 0.0 if future timestamp / clock skew occurs
        age = max(0.0, now - state.timestamp)

        suspect_timeout = self._config.timeouts.heartbeat_suspect_timeout_seconds
        failure_timeout = self._config.timeouts.heartbeat_failure_timeout_seconds

        # Evaluate failure conditions
        if state.status == RobotStatus.FAILED:
            status = PeerHealthStatus.FAILED
            reason = "SELF_REPORTED_FAILURE"
        elif state.status == RobotStatus.EMERGENCY_STOP:
            status = PeerHealthStatus.FAILED
            reason = "SELF_REPORTED_EMERGENCY_STOP"
        elif age > failure_timeout:
            status = PeerHealthStatus.FAILED
            reason = "HEARTBEAT_TIMEOUT_FAILED"
        elif age > suspect_timeout:
            status = PeerHealthStatus.SUSPECTED
            reason = "HEARTBEAT_TIMEOUT_SUSPECTED"
        else:
            status = PeerHealthStatus.HEALTHY
            reason = "HEARTBEAT_ACTIVE"

        return PeerHealthAssessment(
            robot_id=peer_id,
            status=status,
            last_seen_timestamp=state.timestamp,
            age_seconds=age,
            reason=reason,
            evaluated_at=now,
        )

    def evaluate_fleet(
        self,
        world_model: WorldModel,
        now: float,
    ) -> FleetHealthReport:
        """Evaluate the health of all known peer AMRs in the fleet.

        Queries world_model.get_all_peer_states() so that stale/failed peers
        remain detectable even after exceeding fresh-telemetry thresholds.

        Args:
            world_model: Local WorldModel to inspect.
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            FleetHealthReport detailing assessments, suspected IDs, and failed IDs.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        assessments: dict[str, PeerHealthAssessment] = {}
        suspected_ids: list[str] = []
        failed_ids: list[str] = []

        all_peers = world_model.get_all_peer_states()

        # Sort peer IDs for deterministic evaluation order
        for peer_id in sorted(all_peers.keys()):
            assessment = self.evaluate_peer(peer_id, world_model, now)
            if assessment is not None:
                assessments[peer_id] = assessment
                if assessment.status == PeerHealthStatus.SUSPECTED:
                    suspected_ids.append(peer_id)
                elif assessment.status == PeerHealthStatus.FAILED:
                    failed_ids.append(peer_id)

        return FleetHealthReport(
            assessments=assessments,
            suspected_robot_ids=suspected_ids,
            failed_robot_ids=failed_ids,
            evaluated_at=now,
        )

    # =========================================================================
    # Public API — Explicit Task Reclaim
    # =========================================================================

    def reclaim_failed_robot_tasks(
        self,
        failed_robot_id: str,
        world_model: WorldModel,
        now: float = 0.0,
    ) -> list[str]:
        """Identify unfinished tasks assigned to a failed robot and mark them FAILED.

        This makes the tasks assignable again (task.is_assignable() == True),
        allowing TaskAllocator to reassign them to healthy peers.

        Completed tasks and unassigned tasks are never touched.

        Args:
            failed_robot_id: Robot ID of the failed AMR.
            world_model: Local WorldModel containing tasks.
            now: Optional reference timestamp.

        Returns:
            List of reclaimed task IDs that were transitioned to TaskStatus.FAILED.
        """
        if not failed_robot_id:
            return []

        reclaimed_ids: list[str] = []
        all_tasks = world_model.get_all_tasks()

        for task_id in sorted(all_tasks.keys()):
            task = all_tasks[task_id]
            # Only reclaim tasks actively assigned to this failed robot
            if task.assigned_robot == failed_robot_id:
                if task.status in (TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS):
                    task.status = TaskStatus.FAILED
                    world_model.add_task(task)
                    reclaimed_ids.append(task_id)

        return reclaimed_ids
