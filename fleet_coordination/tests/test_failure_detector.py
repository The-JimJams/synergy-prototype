"""
Unit tests for FailureDetector algorithm.
==========================================

Tests peer heartbeat monitoring, health state transitions (HEALTHY -> SUSPECTED -> FAILED),
auto-recovery, task reclaim, and end-to-end integration with TaskAllocator.
"""

from __future__ import annotations

import math
import pytest

from fleet_coordination.algorithm.failure_detector import FailureDetector
from fleet_coordination.algorithm.task_allocator import TaskAllocator
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig, TimeoutConfig
from fleet_coordination.models.health import (
    FleetHealthReport,
    PeerHealthAssessment,
    PeerHealthStatus,
)
from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task, TaskStatus, TaskType


@pytest.fixture
def custom_config() -> CoordinationConfig:
    """Config with standard 3.0s suspect and 10.0s failure timeouts."""
    return CoordinationConfig(
        timeouts=TimeoutConfig(
            heartbeat_suspect_timeout_seconds=3.0,
            heartbeat_failure_timeout_seconds=10.0,
            peer_state_max_age_seconds=5.0,
        )
    )


@pytest.fixture
def detector(custom_config: CoordinationConfig) -> FailureDetector:
    return FailureDetector(config=custom_config)


@pytest.fixture
def world_model(custom_config: CoordinationConfig) -> WorldModel:
    return WorldModel(robot_id="amr_a", config=custom_config)


class TestPeerHealthEvaluation:
    """Tests evaluate_peer() health classifications and boundaries."""

    def test_healthy_peer(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # Last seen at t=100.0, now=101.5 -> age=1.5s <= 3.0s -> HEALTHY
        state = RobotState(robot_id="amr_b", timestamp=100.0, status=RobotStatus.NAVIGATING)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=101.5)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.HEALTHY
        assert assessment.reason == "HEARTBEAT_ACTIVE"
        assert assessment.age_seconds == pytest.approx(1.5)
        assert assessment.is_healthy() is True
        assert assessment.is_failed() is False

    def test_exact_3s_boundary_is_healthy(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # age == 3.0s -> HEALTHY
        state = RobotState(robot_id="amr_b", timestamp=100.0)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=103.0)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.HEALTHY
        assert assessment.reason == "HEARTBEAT_ACTIVE"

    def test_suspected_peer_just_beyond_3s(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # age == 3.001s -> SUSPECTED
        state = RobotState(robot_id="amr_b", timestamp=100.0)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=103.001)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.SUSPECTED
        assert assessment.reason == "HEARTBEAT_TIMEOUT_SUSPECTED"
        assert assessment.is_healthy() is False
        assert assessment.is_failed() is False

    def test_exact_10s_boundary_is_suspected(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # age == 10.0s -> SUSPECTED
        state = RobotState(robot_id="amr_b", timestamp=100.0)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=110.0)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.SUSPECTED
        assert assessment.reason == "HEARTBEAT_TIMEOUT_SUSPECTED"

    def test_failed_peer_just_beyond_10s(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # age == 10.001s -> FAILED
        state = RobotState(robot_id="amr_b", timestamp=100.0)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=110.001)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.FAILED
        assert assessment.reason == "HEARTBEAT_TIMEOUT_FAILED"
        assert assessment.is_failed() is True

    def test_self_reported_failed_status(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # Fresh telemetry (age=0.5s) but status is explicitly FAILED -> FAILED
        state = RobotState(robot_id="amr_b", timestamp=100.0, status=RobotStatus.FAILED)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=100.5)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.FAILED
        assert assessment.reason == "SELF_REPORTED_FAILURE"

    def test_self_reported_emergency_stop_status(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # Fresh telemetry (age=0.5s) but status is EMERGENCY_STOP -> FAILED
        state = RobotState(robot_id="amr_b", timestamp=100.0, status=RobotStatus.EMERGENCY_STOP)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=100.5)
        assert assessment is not None
        assert assessment.status == PeerHealthStatus.FAILED
        assert assessment.reason == "SELF_REPORTED_EMERGENCY_STOP"

    def test_unknown_peer_returns_none(self, detector: FailureDetector, world_model: WorldModel) -> None:
        assert detector.evaluate_peer("amr_unknown", world_model, now=100.0) is None

    def test_future_timestamp_clamped_safely(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # Telemetry timestamp is ahead of now (e.g. slight clock skew)
        state = RobotState(robot_id="amr_b", timestamp=105.0)
        world_model.update_peer_state(state)

        assessment = detector.evaluate_peer("amr_b", world_model, now=100.0)
        assert assessment is not None
        assert assessment.age_seconds == 0.0
        assert assessment.status == PeerHealthStatus.HEALTHY


class TestFleetHealthEvaluation:
    """Tests evaluate_fleet() across multiple peers."""

    def test_empty_world_model_returns_empty_report(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        report = detector.evaluate_fleet(world_model, now=100.0)
        assert len(report.assessments) == 0
        assert report.suspected_robot_ids == []
        assert report.failed_robot_ids == []
        assert report.has_failures() is False
        assert report.has_suspicions() is False

    def test_multiple_peers_mixed_health(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        # AMR B: Healthy (age 1s)
        # AMR C: Suspected (age 5s)
        # AMR D: Failed (age 15s)
        # AMR E: Failed (Self-reported FAILED, age 1s)
        world_model.update_peer_state(RobotState("amr_b", timestamp=99.0))
        world_model.update_peer_state(RobotState("amr_c", timestamp=95.0))
        world_model.update_peer_state(RobotState("amr_d", timestamp=85.0))
        world_model.update_peer_state(RobotState("amr_e", timestamp=99.0, status=RobotStatus.FAILED))

        report = detector.evaluate_fleet(world_model, now=100.0)

        assert len(report.assessments) == 4
        assert report.assessments["amr_b"].status == PeerHealthStatus.HEALTHY
        assert report.assessments["amr_c"].status == PeerHealthStatus.SUSPECTED
        assert report.assessments["amr_d"].status == PeerHealthStatus.FAILED
        assert report.assessments["amr_e"].status == PeerHealthStatus.FAILED

        assert report.suspected_robot_ids == ["amr_c"]
        assert report.failed_robot_ids == ["amr_d", "amr_e"]
        assert report.has_failures() is True
        assert report.has_suspicions() is True

    def test_deterministic_ordering_of_ids(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        # Insert in reverse order
        world_model.update_peer_state(RobotState("amr_z", timestamp=50.0))
        world_model.update_peer_state(RobotState("amr_m", timestamp=50.0))
        world_model.update_peer_state(RobotState("amr_b", timestamp=50.0))

        report = detector.evaluate_fleet(world_model, now=100.0)
        assert report.failed_robot_ids == ["amr_b", "amr_m", "amr_z"]

    def test_peer_auto_recovery(self, detector: FailureDetector, world_model: WorldModel) -> None:
        # Initially failed at now=100.0
        world_model.update_peer_state(RobotState("amr_b", timestamp=80.0))
        report1 = detector.evaluate_fleet(world_model, now=100.0)
        assert "amr_b" in report1.failed_robot_ids

        # Robot reboots and sends fresh state at timestamp=105.0
        world_model.update_peer_state(RobotState("amr_b", timestamp=105.0))
        report2 = detector.evaluate_fleet(world_model, now=106.0)
        assert report2.assessments["amr_b"].status == PeerHealthStatus.HEALTHY
        assert "amr_b" not in report2.failed_robot_ids


class TestTaskReclaimAndAllocation:
    """Tests reclaim_failed_robot_tasks() and end-to-end task reassignment."""

    def test_reclaim_active_tasks_for_failed_robot(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        # Add 3 tasks: one assigned to amr_b, one in_progress with amr_b, one assigned to amr_c
        t1 = Task(task_id="task_1", assigned_robot="amr_b", status=TaskStatus.ASSIGNED)
        t2 = Task(task_id="task_2", assigned_robot="amr_b", status=TaskStatus.IN_PROGRESS)
        t3 = Task(task_id="task_3", assigned_robot="amr_c", status=TaskStatus.ASSIGNED)

        world_model.add_task(t1)
        world_model.add_task(t2)
        world_model.add_task(t3)

        reclaimed = detector.reclaim_failed_robot_tasks("amr_b", world_model, now=100.0)

        assert sorted(reclaimed) == ["task_1", "task_2"]
        assert world_model.get_task("task_1").status == TaskStatus.FAILED  # type: ignore
        assert world_model.get_task("task_2").status == TaskStatus.FAILED  # type: ignore
        assert world_model.get_task("task_3").status == TaskStatus.ASSIGNED  # type: ignore

    def test_completed_or_unassigned_tasks_not_reclaimed(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        t_completed = Task(task_id="task_comp", assigned_robot="amr_b", status=TaskStatus.COMPLETED)
        t_unassigned = Task(task_id="task_unassigned", assigned_robot=None, status=TaskStatus.ANNOUNCED)

        world_model.add_task(t_completed)
        world_model.add_task(t_unassigned)

        reclaimed = detector.reclaim_failed_robot_tasks("amr_b", world_model, now=100.0)
        assert reclaimed == []
        assert world_model.get_task("task_comp").status == TaskStatus.COMPLETED  # type: ignore
        assert world_model.get_task("task_unassigned").status == TaskStatus.ANNOUNCED  # type: ignore

    def test_reclaim_with_empty_robot_id_is_noop(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        assert detector.reclaim_failed_robot_tasks("", world_model) == []

    def test_end_to_end_failure_reassignment_flow(
        self, detector: FailureDetector, world_model: WorldModel, custom_config: CoordinationConfig
    ) -> None:
        """Complete vertical test: Failure detected -> task reclaimed -> TaskAllocator assigns to healthy peer."""
        allocator = TaskAllocator(config=custom_config)

        # 1. Setup fleet: amr_a (local, healthy), amr_b (failed), amr_c (healthy peer)
        world_model.set_own_state(
            RobotState(robot_id="amr_a", timestamp=100.0, battery_percent=90.0, status=RobotStatus.IDLE)
        )
        # AMR B last seen 20s ago -> FAILED
        world_model.update_peer_state(
            RobotState(robot_id="amr_b", timestamp=80.0, battery_percent=100.0, status=RobotStatus.NAVIGATING)
        )
        # AMR C fresh -> HEALTHY
        world_model.update_peer_state(
            RobotState(robot_id="amr_c", timestamp=99.5, battery_percent=70.0, status=RobotStatus.IDLE)
        )

        # 2. Add an active task assigned to amr_b
        active_task = Task(
            task_id="task_critical_pack",
            priority=8,
            assigned_robot="amr_b",
            status=TaskStatus.IN_PROGRESS,
        )
        world_model.add_task(active_task)

        # 3. Run failure detection
        health_report = detector.evaluate_fleet(world_model, now=100.0)
        assert "amr_b" in health_report.failed_robot_ids

        # 4. Reclaim tasks from failed AMR B
        reclaimed = detector.reclaim_failed_robot_tasks("amr_b", world_model, now=100.0)
        assert reclaimed == ["task_critical_pack"]

        reclaimed_task = world_model.get_task("task_critical_pack")
        assert reclaimed_task is not None
        assert reclaimed_task.status == TaskStatus.FAILED
        assert reclaimed_task.is_assignable() is True

        # 5. TaskAllocator re-evaluates the failed task
        decision = allocator.evaluate_task(reclaimed_task, world_model, now=100.0)
        assert decision.accepted is True
        # AMR B is excluded because its telemetry is stale (>5s) and failed
        assert decision.winner_id in ("amr_a", "amr_c")
        assert decision.winner_id == "amr_a"  # amr_a has higher battery (90% vs 70%)

        # 6. Apply assignment
        assigned = allocator.assign_task("task_critical_pack", world_model, decision)
        assert assigned is True
        assert world_model.get_task("task_critical_pack").assigned_robot == "amr_a"  # type: ignore
        assert world_model.get_task("task_critical_pack").status == TaskStatus.ASSIGNED  # type: ignore


class TestRobustnessAndValidation:
    """Tests validation, numeric edge cases, and idempotency."""

    def test_invalid_now_raises_value_error(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            detector.evaluate_peer("amr_b", world_model, now=-1.0)

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            detector.evaluate_fleet(world_model, now=float("nan"))

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            detector.evaluate_fleet(world_model, now=float("inf"))

    def test_repeated_evaluation_is_idempotent(
        self, detector: FailureDetector, world_model: WorldModel
    ) -> None:
        world_model.update_peer_state(RobotState("amr_b", timestamp=100.0))
        eval1 = detector.evaluate_peer("amr_b", world_model, now=105.0)
        eval2 = detector.evaluate_peer("amr_b", world_model, now=105.0)

        assert eval1 == eval2
