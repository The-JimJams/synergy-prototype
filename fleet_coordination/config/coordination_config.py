"""
Fleet Coordination Configuration
================================

Single source of truth for all tunable parameters, weights, timeouts,
and thresholds used by the coordination algorithms.

DESIGN RULES:
- No magic numbers in algorithm files. Import from here.
- Every parameter has a docstring explaining what it controls.
- All thresholds are experimental — not certified safety limits.
- Parameters can be overridden at runtime for testing.
"""

from dataclasses import dataclass, field


@dataclass
class PriorityWeights:
    """Weights for the deterministic priority scoring function.

    priority_score =
        w_task * task_priority
      + w_deadline * deadline_urgency
      + w_wait * waiting_time
      + w_battery * battery_urgency

    All weights must be non-negative. The absolute values don't matter —
    only the ratios between them affect the ranking.
    """

    w_task: float = 1.0
    w_deadline: float = 0.8
    w_wait: float = 0.5
    w_battery: float = 0.3

    # Normalization scale for intent commitment age (seconds)
    max_wait_seconds: float = 120.0

    # Tolerance threshold for floating-point near-equality before robot_id tie-break
    score_epsilon: float = 1e-9


@dataclass
class TaskBidWeights:
    """Weights and parameters for the deterministic task allocation bid scoring.

    bid_score = (
        w_battery * battery_factor
        + w_priority * priority_factor
        + w_deadline * deadline_factor
    ) / (w_battery + w_priority + w_deadline)
    """

    w_battery: float = 0.40
    w_priority: float = 0.35
    w_deadline: float = 0.25

    # Minimum battery percent required to be eligible for a task
    min_battery_percent: float = 20.0

    # Tolerance threshold for floating-point near-equality before robot_id tie-break
    score_epsilon: float = 1e-9


@dataclass
class TimeoutConfig:
    """Timeout thresholds for freshness, heartbeats, and reservations.

    WARNING: These are experimental tuning parameters for a simulation
    prototype. They are NOT certified safety limits.
    """

    # Peer state freshness: states older than this are considered stale
    peer_state_max_age_seconds: float = 5.0

    # Peer intent freshness: intents older than this are considered stale
    peer_intent_max_age_seconds: float = 10.0

    # Heartbeat: time after last heartbeat before a robot is SUSPECTED
    heartbeat_suspect_timeout_seconds: float = 3.0

    # Heartbeat: time after SUSPECTED before a robot is declared FAILED
    heartbeat_failure_timeout_seconds: float = 10.0

    # Reservation: default duration if not explicitly specified (seconds)
    default_reservation_duration_seconds: float = 30.0

    # Reservation: maximum allowed duration (seconds)
    max_reservation_duration_seconds: float = 120.0

    # Task bidding: how long to wait for all bids before selecting winner
    bid_collection_timeout_seconds: float = 5.0


@dataclass
class NetworkThresholds:
    """Thresholds for network quality assessment.

    These determine transitions between coordination modes:
    CONNECTED -> DEGRADED -> DISCONNECTED -> RECOVERY

    WARNING: These are experimental. Actual values depend on the
    network characteristics of the deployment environment.
    """

    # Latency above this (seconds) triggers DEGRADED mode
    degraded_latency_threshold: float = 0.5

    # Packet loss rate above this (0.0–1.0) triggers DEGRADED mode
    degraded_loss_threshold: float = 0.1

    # Latency above this (seconds) triggers DISCONNECTED mode
    disconnected_latency_threshold: float = 2.0

    # Packet loss rate above this (0.0–1.0) triggers DISCONNECTED mode
    disconnected_loss_threshold: float = 0.5

    # Number of consecutive healthy checks before returning to CONNECTED
    recovery_confirmation_count: int = 3

    # How often to measure network quality (seconds)
    measurement_interval_seconds: float = 1.0


@dataclass
class ConflictDetectionConfig:
    """Parameters for the conflict detection algorithm."""

    # Minimum temporal overlap (seconds) to consider a conflict
    # Below this, robots likely won't actually collide
    min_temporal_overlap_seconds: float = 1.0

    # How far into the future to check for conflicts (seconds)
    planning_horizon_seconds: float = 60.0


@dataclass
class CoordinationConfig:
    """Top-level configuration aggregating all parameter groups.

    Usage:
        config = CoordinationConfig()  # all defaults
        config = CoordinationConfig(
            priority_weights=PriorityWeights(w_task=2.0),
            timeouts=TimeoutConfig(peer_state_max_age_seconds=3.0),
        )
    """

    priority_weights: PriorityWeights = field(default_factory=PriorityWeights)
    task_bid_weights: TaskBidWeights = field(default_factory=TaskBidWeights)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    network: NetworkThresholds = field(default_factory=NetworkThresholds)
    conflict_detection: ConflictDetectionConfig = field(
        default_factory=ConflictDetectionConfig
    )

    # Fleet-wide constants
    # Maximum number of robots expected in the fleet
    max_fleet_size: int = 10

    # Deterministic tie-breaker: when True, lower robot_id wins ties
    # This must be the same on ALL robots for determinism
    lower_id_wins_ties: bool = True
