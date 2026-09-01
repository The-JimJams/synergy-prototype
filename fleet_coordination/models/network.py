"""
Network Telemetry & Coordination Mode Data Models.
==================================================

Represents link-level communication metrics and fleet coordination modes
under network degradation and recovery.

Zero ROS imports — pure dataclasses.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto


class NetworkMode(Enum):
    """Operational communication modes of the local AMR."""

    CONNECTED = auto()     # Normal low-latency, reliable communication
    DEGRADED = auto()      # Elevated latency or packet loss (>thresholds)
    DISCONNECTED = auto()  # Severe latency, high loss, or total loss of peer telemetry
    RECOVERY = auto()      # Link restored; reconciling state across fleet before CONNECTED


@dataclass(frozen=True)
class LinkMetrics:
    """Telemetry snapshot of a point-to-point or multicast communication link."""

    peer_id: str
    latency_seconds: float = 0.0
    packet_loss_rate: float = 0.0  # 0.0 to 1.0
    last_message_age_seconds: float = 0.0
    measured_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.peer_id:
            raise ValueError("peer_id must be a non-empty string")
        if self.latency_seconds < 0.0:
            raise ValueError("latency_seconds cannot be negative")
        if not (0.0 <= self.packet_loss_rate <= 1.0):
            raise ValueError(f"packet_loss_rate must be between 0.0 and 1.0, got {self.packet_loss_rate}")
        if self.last_message_age_seconds < 0.0:
            raise ValueError("last_message_age_seconds cannot be negative")

    def __repr__(self) -> str:
        return (
            f"LinkMetrics(peer={self.peer_id!r}, latency={self.latency_seconds*1000:.1f}ms, "
            f"loss={self.packet_loss_rate*100:.1f}%, age={self.last_message_age_seconds:.2f}s)"
        )


@dataclass
class NetworkStatusReport:
    """Comprehensive communication status evaluation for the local AMR."""

    mode: NetworkMode
    avg_latency_seconds: float
    max_packet_loss_rate: float
    link_reports: dict[str, LinkMetrics] = field(default_factory=dict)
    consecutive_healthy_checks: int = 0
    reason: str = ""
    evaluated_at: float = field(default_factory=time.time)

    def is_connected(self) -> bool:
        """Check if network is in nominal CONNECTED mode."""
        return self.mode == NetworkMode.CONNECTED

    def is_degraded(self) -> bool:
        """Check if network is in DEGRADED mode."""
        return self.mode == NetworkMode.DEGRADED

    def is_disconnected(self) -> bool:
        """Check if network is DISCONNECTED."""
        return self.mode == NetworkMode.DISCONNECTED

    def is_recovering(self) -> bool:
        """Check if network is in RECOVERY mode."""
        return self.mode == NetworkMode.RECOVERY

    def __repr__(self) -> str:
        return (
            f"NetworkStatusReport(mode={self.mode.name}, avg_latency={self.avg_latency_seconds*1000:.1f}ms, "
            f"max_loss={self.max_packet_loss_rate*100:.1f}%, checks={self.consecutive_healthy_checks}, "
            f"reason={self.reason!r})"
        )
