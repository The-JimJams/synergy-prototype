"""
NetworkManager — Communication Health & Coordination Mode State Machine.
========================================================================

Pure algorithmic evaluator for network quality (latency, packet loss, telemetry age).
Determines the local AMR's coordination mode (CONNECTED, DEGRADED, DISCONNECTED, RECOVERY).

ARCHITECTURAL PRINCIPLES:
1. Local State Machine: Evaluates the communication health of the local AMR's
   links. Does NOT manage robot hardware or motion.
2. Separation of Failures: Network disconnection != robot hardware failure.
3. Deterministic Transitions: Transition rules strictly follow CoordinationConfig.network
   thresholds with explicit recovery confirmation counts.
4. ROS-Free: Zero rclpy / ROS 2 / Gazebo imports.
"""

from __future__ import annotations

import math

from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.network import (
    LinkMetrics,
    NetworkMode,
    NetworkStatusReport,
)


class NetworkManager:
    """Evaluates network telemetry and tracks local AMR communication mode."""

    def __init__(self, config: CoordinationConfig | None = None) -> None:
        """Initialize NetworkManager with coordination configuration.

        Args:
            config: Coordination configuration containing NetworkThresholds.
                    Defaults to CoordinationConfig().
        """
        self._config: CoordinationConfig = (
            config if config is not None else CoordinationConfig()
        )
        self._current_mode: NetworkMode = NetworkMode.CONNECTED
        self._consecutive_healthy_checks: int = 0

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    @property
    def current_mode(self) -> NetworkMode:
        """Current operational communication mode."""
        return self._current_mode

    @property
    def consecutive_healthy_checks(self) -> int:
        """Number of consecutive healthy telemetry evaluations recorded during recovery."""
        return self._consecutive_healthy_checks

    def reset(self) -> None:
        """Reset internal state machine to default CONNECTED state."""
        self._current_mode = NetworkMode.CONNECTED
        self._consecutive_healthy_checks = 0

    def evaluate_network(
        self,
        links: list[LinkMetrics],
        now: float,
    ) -> NetworkStatusReport:
        """Evaluate network telemetry and update the local AMR's NetworkMode.

        Transition Rules:
        - If links is empty: remains in current mode (or CONNECTED), increments recovery checks if recovering.
        - Disconnected Condition: max_latency > 2.0s OR max_loss > 0.50 OR max_age > 2.0s.
        - Degraded Condition: max_latency > 0.5s OR max_loss > 0.10.
        - Healthy Condition: All link latencies <= 0.5s AND losses <= 0.10 AND ages <= 2.0s.
        - Disconnected -> Recovery: Triggered on first healthy check after Disconnected.
        - Recovery -> Connected: Requires recovery_confirmation_count (default 3) consecutive healthy checks.
        - Any degradation during Recovery -> immediately transitions back to Disconnected.

        Args:
            links: List of LinkMetrics snapshots across known peer connections.
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            NetworkStatusReport detailing current mode, aggregate metrics, and transition rationale.

        Raises:
            ValueError: If now is NaN, infinite, or negative.
        """
        if not math.isfinite(now) or now < 0.0:
            raise ValueError(f"Invalid reference time 'now': {now}")

        thresholds = self._config.network
        recovery_required = thresholds.recovery_confirmation_count

        # 1. Handle empty link metrics (single robot or no peer telemetry)
        if not links:
            if self._current_mode == NetworkMode.RECOVERY:
                self._consecutive_healthy_checks += 1
                if self._consecutive_healthy_checks >= recovery_required:
                    self._current_mode = NetworkMode.CONNECTED
                    reason = "RECOVERY_COMPLETE_CONNECTED"
                else:
                    reason = f"RECOVERY_CHECK_{self._consecutive_healthy_checks}_OF_{recovery_required}"
            else:
                reason = "NOMINAL_NO_PEERS"

            return NetworkStatusReport(
                mode=self._current_mode,
                avg_latency_seconds=0.0,
                max_packet_loss_rate=0.0,
                link_reports={},
                consecutive_healthy_checks=self._consecutive_healthy_checks,
                reason=reason,
                evaluated_at=now,
            )

        # 2. Compute aggregate metrics
        avg_latency = sum(l.latency_seconds for l in links) / len(links)
        max_loss = max(l.packet_loss_rate for l in links)
        max_latency = max(l.latency_seconds for l in links)
        max_age = max(l.last_message_age_seconds for l in links)

        # 3. Classify instantaneous link quality
        is_disconnected = (
            max_latency > thresholds.disconnected_latency_threshold
            or max_loss > thresholds.disconnected_loss_threshold
            or max_age > thresholds.disconnected_latency_threshold
        )
        is_degraded = (
            max_latency > thresholds.degraded_latency_threshold
            or max_loss > thresholds.degraded_loss_threshold
        )
        is_healthy = not is_disconnected and not is_degraded

        # 4. State Machine Transitions
        if self._current_mode == NetworkMode.CONNECTED:
            if is_disconnected:
                self._current_mode = NetworkMode.DISCONNECTED
                self._consecutive_healthy_checks = 0
                reason = "DISCONNECTED_THRESHOLD_EXCEEDED"
            elif is_degraded:
                self._current_mode = NetworkMode.DEGRADED
                self._consecutive_healthy_checks = 0
                reason = "DEGRADED_THRESHOLD_EXCEEDED"
            else:
                self._consecutive_healthy_checks = 0
                reason = "NOMINAL"

        elif self._current_mode == NetworkMode.DEGRADED:
            if is_disconnected:
                self._current_mode = NetworkMode.DISCONNECTED
                self._consecutive_healthy_checks = 0
                reason = "DISCONNECTED_THRESHOLD_EXCEEDED"
            elif is_healthy:
                self._current_mode = NetworkMode.CONNECTED
                self._consecutive_healthy_checks = 0
                reason = "NOMINAL_RECOVERED"
            else:
                self._consecutive_healthy_checks = 0
                reason = "DEGRADED_CONTINUED"

        elif self._current_mode == NetworkMode.DISCONNECTED:
            if is_healthy:
                self._current_mode = NetworkMode.RECOVERY
                self._consecutive_healthy_checks = 1
                if self._consecutive_healthy_checks >= recovery_required:
                    self._current_mode = NetworkMode.CONNECTED
                    reason = "RECOVERY_COMPLETE_CONNECTED"
                else:
                    reason = f"RECOVERY_STARTED_CHECK_1_OF_{recovery_required}"
            else:
                self._consecutive_healthy_checks = 0
                reason = "DISCONNECTED_CONTINUED"

        elif self._current_mode == NetworkMode.RECOVERY:
            if is_disconnected or is_degraded:
                self._current_mode = NetworkMode.DISCONNECTED
                self._consecutive_healthy_checks = 0
                reason = "RECOVERY_INTERRUPTED_DEGRADED"
            else:
                self._consecutive_healthy_checks += 1
                if self._consecutive_healthy_checks >= recovery_required:
                    self._current_mode = NetworkMode.CONNECTED
                    reason = "RECOVERY_COMPLETE_CONNECTED"
                else:
                    reason = f"RECOVERY_CHECK_{self._consecutive_healthy_checks}_OF_{recovery_required}"

        # 5. Build ordered dictionary of link reports
        link_dict = {
            link.peer_id: link for link in sorted(links, key=lambda l: l.peer_id)
        }

        return NetworkStatusReport(
            mode=self._current_mode,
            avg_latency_seconds=avg_latency,
            max_packet_loss_rate=max_loss,
            link_reports=link_dict,
            consecutive_healthy_checks=self._consecutive_healthy_checks,
            reason=reason,
            evaluated_at=now,
        )
