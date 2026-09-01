"""
Unit tests for NetworkManager and ReconciliationManager.
=========================================================

Validates network mode transitions (CONNECTED -> DEGRADED -> DISCONNECTED -> RECOVERY),
recovery confirmation count thresholds, deterministic state reconciliation (states, intents,
reservations, tasks), and failure separation invariants.
"""

from __future__ import annotations

import math
import pytest

from fleet_coordination.algorithm.failure_detector import FailureDetector
from fleet_coordination.algorithm.network_manager import NetworkManager
from fleet_coordination.algorithm.reconciliation_manager import ReconciliationManager
from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import (
    CoordinationConfig,
    NetworkThresholds,
)
from fleet_coordination.models.network import (
    LinkMetrics,
    NetworkMode,
    NetworkStatusReport,
)
from fleet_coordination.models.reconciliation import ReconciliationReport
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.task import Task, TaskStatus, TaskType


FIXED_TIME = 1000.0


@pytest.fixture
def config() -> CoordinationConfig:
    return CoordinationConfig(
        network=NetworkThresholds(
            degraded_latency_threshold=0.5,
            degraded_loss_threshold=0.1,
            disconnected_latency_threshold=2.0,
            disconnected_loss_threshold=0.5,
            recovery_confirmation_count=3,
        )
    )


@pytest.fixture
def net_manager(config: CoordinationConfig) -> NetworkManager:
    return NetworkManager(config=config)


@pytest.fixture
def recon_manager(config: CoordinationConfig) -> ReconciliationManager:
    return ReconciliationManager(config=config)


@pytest.fixture
def world_model(config: CoordinationConfig) -> WorldModel:
    return WorldModel(robot_id="amr_a", config=config)


# =============================================================================
# 1. NetworkManager State Transitions & Thresholds Tests
# =============================================================================

class TestNetworkManagerModes:
    """Tests NetworkManager evaluation and mode transitions."""

    def test_connected_nominal_state(self, net_manager: NetworkManager) -> None:
        links = [
            LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.0, last_message_age_seconds=0.1),
            LinkMetrics("amr_c", latency_seconds=0.15, packet_loss_rate=0.02, last_message_age_seconds=0.2),
        ]
        report = net_manager.evaluate_network(links, now=FIXED_TIME)
        assert report.mode == NetworkMode.CONNECTED
        assert report.is_connected() is True
        assert report.avg_latency_seconds == pytest.approx(0.125)
        assert report.max_packet_loss_rate == pytest.approx(0.02)
        assert report.reason == "NOMINAL"

    def test_latency_degraded_boundary(self, net_manager: NetworkManager) -> None:
        # Exactly 0.5s is CONNECTED
        links_exact = [LinkMetrics("amr_b", latency_seconds=0.5, packet_loss_rate=0.0)]
        rep1 = net_manager.evaluate_network(links_exact, now=FIXED_TIME)
        assert rep1.mode == NetworkMode.CONNECTED

        # 0.501s is DEGRADED
        links_over = [LinkMetrics("amr_b", latency_seconds=0.501, packet_loss_rate=0.0)]
        rep2 = net_manager.evaluate_network(links_over, now=FIXED_TIME)
        assert rep2.mode == NetworkMode.DEGRADED
        assert rep2.is_degraded() is True

    def test_packet_loss_degraded_boundary(self, net_manager: NetworkManager) -> None:
        # Exactly 10% loss is CONNECTED
        links_exact = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.10)]
        rep1 = net_manager.evaluate_network(links_exact, now=FIXED_TIME)
        assert rep1.mode == NetworkMode.CONNECTED

        # 10.1% loss is DEGRADED
        links_over = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.101)]
        rep2 = net_manager.evaluate_network(links_over, now=FIXED_TIME)
        assert rep2.mode == NetworkMode.DEGRADED

    def test_latency_disconnected_boundary(self, net_manager: NetworkManager) -> None:
        # Exactly 2.0s is DEGRADED
        links_exact = [LinkMetrics("amr_b", latency_seconds=2.0, packet_loss_rate=0.0)]
        rep1 = net_manager.evaluate_network(links_exact, now=FIXED_TIME)
        assert rep1.mode == NetworkMode.DEGRADED

        # 2.001s is DISCONNECTED
        links_over = [LinkMetrics("amr_b", latency_seconds=2.001, packet_loss_rate=0.0)]
        rep2 = net_manager.evaluate_network(links_over, now=FIXED_TIME)
        assert rep2.mode == NetworkMode.DISCONNECTED
        assert rep2.is_disconnected() is True

    def test_packet_loss_disconnected_boundary(self, net_manager: NetworkManager) -> None:
        # Exactly 50% loss is DEGRADED
        links_exact = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.50)]
        rep1 = net_manager.evaluate_network(links_exact, now=FIXED_TIME)
        assert rep1.mode == NetworkMode.DEGRADED

        # 50.1% loss is DISCONNECTED
        links_over = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.501)]
        rep2 = net_manager.evaluate_network(links_over, now=FIXED_TIME)
        assert rep2.mode == NetworkMode.DISCONNECTED

    def test_message_age_triggers_disconnected(self, net_manager: NetworkManager) -> None:
        # Low latency and 0% loss, but silence > 2.0s
        links = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.0, last_message_age_seconds=2.5)]
        report = net_manager.evaluate_network(links, now=FIXED_TIME)
        assert report.mode == NetworkMode.DISCONNECTED

    def test_recovery_requires_three_consecutive_healthy_checks(
        self, net_manager: NetworkManager
    ) -> None:
        # 1. Drive to DISCONNECTED
        links_dead = [LinkMetrics("amr_b", latency_seconds=5.0, packet_loss_rate=0.9)]
        net_manager.evaluate_network(links_dead, now=FIXED_TIME)
        assert net_manager.current_mode == NetworkMode.DISCONNECTED

        # 2. Link becomes healthy -> Check 1/3 (RECOVERY)
        links_healthy = [LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.0)]
        rep1 = net_manager.evaluate_network(links_healthy, now=FIXED_TIME + 1.0)
        assert rep1.mode == NetworkMode.RECOVERY
        assert rep1.is_recovering() is True
        assert rep1.consecutive_healthy_checks == 1

        # 3. Check 2/3 (RECOVERY)
        rep2 = net_manager.evaluate_network(links_healthy, now=FIXED_TIME + 2.0)
        assert rep2.mode == NetworkMode.RECOVERY
        assert rep2.consecutive_healthy_checks == 2

        # 4. Check 3/3 (CONNECTED)
        rep3 = net_manager.evaluate_network(links_healthy, now=FIXED_TIME + 3.0)
        assert rep3.mode == NetworkMode.CONNECTED
        assert rep3.is_connected() is True
        assert rep3.consecutive_healthy_checks == 3

    def test_recovery_interrupted_by_degradation(self, net_manager: NetworkManager) -> None:
        # Drive to DISCONNECTED
        net_manager.evaluate_network([LinkMetrics("amr_b", latency_seconds=5.0)], now=FIXED_TIME)

        # Check 1 of recovery
        net_manager.evaluate_network([LinkMetrics("amr_b", latency_seconds=0.1)], now=FIXED_TIME + 1.0)
        assert net_manager.current_mode == NetworkMode.RECOVERY

        # Jitter/degradation occurs during check 2 -> immediately drops back to DISCONNECTED
        rep_drop = net_manager.evaluate_network([LinkMetrics("amr_b", latency_seconds=0.6)], now=FIXED_TIME + 2.0)
        assert rep_drop.mode == NetworkMode.DISCONNECTED
        assert rep_drop.consecutive_healthy_checks == 0

    def test_empty_links_stays_connected_or_advances_recovery(
        self, net_manager: NetworkManager
    ) -> None:
        rep = net_manager.evaluate_network([], now=FIXED_TIME)
        assert rep.mode == NetworkMode.CONNECTED
        assert rep.link_reports == {}

    def test_multiple_peers_mixed_metrics(self, net_manager: NetworkManager) -> None:
        # AMR B is healthy, AMR C is degraded (>0.5s) -> Overall mode is DEGRADED
        links = [
            LinkMetrics("amr_b", latency_seconds=0.1, packet_loss_rate=0.0),
            LinkMetrics("amr_c", latency_seconds=0.7, packet_loss_rate=0.05),
        ]
        report = net_manager.evaluate_network(links, now=FIXED_TIME)
        assert report.mode == NetworkMode.DEGRADED
        assert len(report.link_reports) == 2


# =============================================================================
# 2. Failure vs Communication Disconnection Separation Tests
# =============================================================================

class TestFailureVsCommunicationSeparation:
    """Verifies that NetworkManager and FailureDetector remain strictly decoupled."""

    def test_network_disconnected_does_not_mutate_failure_detector(
        self, net_manager: NetworkManager, world_model: WorldModel
    ) -> None:
        detector = FailureDetector()

        # AMR B telemetry received 1s ago (healthy state)
        world_model.update_peer_state(RobotState("amr_b", timestamp=FIXED_TIME - 1.0))

        # Local network drops completely to DISCONNECTED
        net_manager.evaluate_network([LinkMetrics("amr_b", latency_seconds=10.0, packet_loss_rate=1.0)], now=FIXED_TIME)
        assert net_manager.current_mode == NetworkMode.DISCONNECTED

        # FailureDetector independently evaluates peer state based on heartbeat age
        assessment = detector.evaluate_peer("amr_b", world_model, now=FIXED_TIME)
        assert assessment is not None
        assert assessment.status.name == "HEALTHY"


# =============================================================================
# 3. ReconciliationManager Tests
# =============================================================================

class TestReconciliationManager:
    """Tests deterministic post-partition state, intent, reservation, and task reconciliation."""

    def test_reconcile_peer_states_monotonic_rule(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Initially store amr_b state at t=100.0
        world_model.update_peer_state(RobotState("amr_b", timestamp=100.0, battery_percent=80.0))

        # Incoming snapshot contains:
        # - amr_b newer state (t=105.0) -> accept
        # - amr_b older state (t=95.0) -> reject
        # - own robot amr_a state -> reject (own state protected)
        incoming = [
            RobotState("amr_b", timestamp=105.0, battery_percent=78.0),
            RobotState("amr_b", timestamp=95.0, battery_percent=90.0),
            RobotState("amr_a", timestamp=200.0, battery_percent=50.0),
        ]

        upd, rej = recon_manager.reconcile_peer_states(incoming, world_model, now=FIXED_TIME)
        assert upd == 1
        assert rej == 2
        assert world_model.get_peer_state("amr_b").timestamp == 105.0  # type: ignore

    def test_reconcile_peer_intents_purges_expired(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        valid_intent = RobotIntent("amr_b", timestamp=FIXED_TIME, target_resource_id="I1", valid_until=FIXED_TIME + 30.0)
        expired_intent = RobotIntent("amr_c", timestamp=FIXED_TIME - 50.0, target_resource_id="I1", valid_until=FIXED_TIME - 10.0)

        upd, rej = recon_manager.reconcile_peer_intents([valid_intent, expired_intent], world_model, now=FIXED_TIME)
        assert upd == 1
        assert rej == 1
        assert world_model.get_peer_intent("amr_b") == valid_intent
        assert world_model.get_peer_intent("amr_c") is None

    def test_reconcile_conflicting_reservations_higher_priority_wins(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Two overlapping claims on Intersection I1
        r_low = Reservation("I1", "amr_b", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=1.0, claim_id="c_low", expires_at=FIXED_TIME + 60.0)
        r_high = Reservation("I1", "amr_c", start_time=FIXED_TIME + 5.0, end_time=FIXED_TIME + 25.0, priority=3.0, claim_id="c_high", expires_at=FIXED_TIME + 60.0)

        resolved = recon_manager.reconcile_reservations([r_low, r_high], world_model, now=FIXED_TIME)
        assert resolved == 1
        # High priority claim survived, low priority was purged
        assert world_model.get_reservation("c_high") is not None
        assert world_model.get_reservation("c_low") is None

    def test_reconcile_conflicting_reservations_earlier_timestamp_tiebreak(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Same priority (2.0), but r_early was created 5s earlier
        r_early = Reservation("I1", "amr_c", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=2.0, claim_id="c_early", created_at=FIXED_TIME - 10.0, expires_at=FIXED_TIME + 60.0)
        r_late = Reservation("I1", "amr_b", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=2.0, claim_id="c_late", created_at=FIXED_TIME - 5.0, expires_at=FIXED_TIME + 60.0)

        resolved = recon_manager.reconcile_reservations([r_early, r_late], world_model, now=FIXED_TIME)
        assert resolved == 1
        assert world_model.get_reservation("c_early") is not None
        assert world_model.get_reservation("c_late") is None

    def test_reconcile_conflicting_reservations_robot_id_tiebreak(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Identical priority and created_at -> amr_b wins over amr_c
        r_b = Reservation("I1", "amr_b", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=2.0, claim_id="c_b", created_at=FIXED_TIME, expires_at=FIXED_TIME + 60.0)
        r_c = Reservation("I1", "amr_c", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=2.0, claim_id="c_c", created_at=FIXED_TIME, expires_at=FIXED_TIME + 60.0)

        resolved = recon_manager.reconcile_reservations([r_b, r_c], world_model, now=FIXED_TIME)
        assert resolved == 1
        assert world_model.get_reservation("c_b") is not None
        assert world_model.get_reservation("c_c") is None

    def test_reconcile_tasks_lifecycle_precedence(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Local WorldModel has task_1 in ASSIGNED state
        world_model.add_task(Task(task_id="task_1", assigned_robot="amr_b", status=TaskStatus.ASSIGNED))

        # Incoming peer claims task_1 is COMPLETED
        incoming = [Task(task_id="task_1", assigned_robot="amr_b", status=TaskStatus.COMPLETED)]

        resolved = recon_manager.reconcile_tasks(incoming, world_model, now=FIXED_TIME)
        assert resolved == 1
        assert world_model.get_task("task_1").status == TaskStatus.COMPLETED  # type: ignore

    def test_reconcile_tasks_lower_robot_id_tiebreak(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        # Conflict: both claim ASSIGNED, but amr_b < amr_c
        world_model.add_task(Task(task_id="task_1", assigned_robot="amr_c", status=TaskStatus.ASSIGNED))
        incoming = [Task(task_id="task_1", assigned_robot="amr_b", status=TaskStatus.ASSIGNED)]

        resolved = recon_manager.reconcile_tasks(incoming, world_model, now=FIXED_TIME)
        assert resolved == 1
        assert world_model.get_task("task_1").assigned_robot == "amr_b"  # type: ignore

    def test_full_fleet_snapshot_reconciliation(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        states = [RobotState("amr_b", timestamp=FIXED_TIME)]
        intents = [RobotIntent("amr_b", timestamp=FIXED_TIME, target_resource_id="I1", valid_until=FIXED_TIME + 30.0)]
        reservations = [Reservation("I1", "amr_b", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=1.0, claim_id="c1", expires_at=FIXED_TIME + 60.0)]
        tasks = [Task("task_1", assigned_robot="amr_b", status=TaskStatus.IN_PROGRESS)]

        report = recon_manager.reconcile_fleet_snapshot(
            states, intents, reservations, tasks, world_model, now=FIXED_TIME
        )
        assert report.states_updated == 1
        assert report.intents_updated == 1
        assert report.is_clean is True
        assert report.total_modifications() >= 3

    def test_repeated_reconciliation_is_idempotent(
        self, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        states = [RobotState("amr_b", timestamp=FIXED_TIME)]
        intents = [RobotIntent("amr_b", timestamp=FIXED_TIME, target_resource_id="I1", valid_until=FIXED_TIME + 30.0)]
        reservations = [Reservation("I1", "amr_b", start_time=FIXED_TIME, end_time=FIXED_TIME + 20.0, priority=1.0, claim_id="c1", expires_at=FIXED_TIME + 60.0)]
        tasks = [Task("task_1", assigned_robot="amr_b", status=TaskStatus.IN_PROGRESS)]

        rep1 = recon_manager.reconcile_fleet_snapshot(states, intents, reservations, tasks, world_model, now=FIXED_TIME)
        rep2 = recon_manager.reconcile_fleet_snapshot(states, intents, reservations, tasks, world_model, now=FIXED_TIME)

        # On second run, states and intents are rejected because timestamps are identical
        assert rep2.stale_records_rejected >= 2


# =============================================================================
# 4. Validation & Numeric Safety Tests
# =============================================================================

class TestNumericSafety:
    """Tests validation of invalid timestamps and boundary parameters."""

    def test_invalid_now_raises_value_error(
        self, net_manager: NetworkManager, recon_manager: ReconciliationManager, world_model: WorldModel
    ) -> None:
        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            net_manager.evaluate_network([], now=-1.0)

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            recon_manager.reconcile_peer_states([], world_model, now=float("nan"))

        with pytest.raises(ValueError, match="Invalid reference time 'now'"):
            recon_manager.reconcile_reservations([], world_model, now=float("inf"))

    def test_invalid_link_metrics_validation(self) -> None:
        with pytest.raises(ValueError, match="peer_id must be a non-empty string"):
            LinkMetrics(peer_id="")

        with pytest.raises(ValueError, match="packet_loss_rate must be between 0.0 and 1.0"):
            LinkMetrics(peer_id="amr_b", packet_loss_rate=1.5)

        with pytest.raises(ValueError, match="latency_seconds cannot be negative"):
            LinkMetrics(peer_id="amr_b", latency_seconds=-0.5)
