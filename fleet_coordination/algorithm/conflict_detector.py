"""
ConflictDetector — Pure Algorithmic Coordination Conflict Detection.
====================================================================

Evaluates whether the local robot's future motion plan conflicts with peer
robots' broadcast intents or scheduled reservations over shared spatial resources.

ARCHITECTURAL PRINCIPLES:
1. Coordination Criterion: A ConflictReport is generated when the configured
   coordination detection criteria are satisfied. This is a discrete resource
   coordination tool and does NOT provide certified physical collision avoidance.
2. Read-Only: ConflictDetector reads from WorldModel and never modifies state.
3. Zero Resolution: Detects conflicts only. Does not calculate priorities,
   select winners, or grant/deny claims (delegated to PriorityEngine & ReservationManager).
4. Evidence Aggregation: Multi-source evidence (intent + reservation) is aggregated
   per (peer_id, resource_id) to produce a bounding conflict window [min_start, max_end].
5. Determinism: Given identical WorldModel state and timestamp 'now', output is
   sorted deterministically by severity rank, earliest overlap start, and peer ID.
"""

from __future__ import annotations

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import ConflictDetectionConfig
from fleet_coordination.models.conflict import ConflictReport, ConflictSeverity
from fleet_coordination.models.robot_intent import RobotIntent


class ConflictDetector:
    """Pure algorithmic conflict detection engine."""

    def __init__(self, config: ConflictDetectionConfig | None = None) -> None:
        """Initialize ConflictDetector with optional tuning configuration.

        Args:
            config: Detection parameters (min overlap, planning horizon).
                    If None, default ConflictDetectionConfig is used.
        """
        self._config: ConflictDetectionConfig = (
            config if config is not None else ConflictDetectionConfig()
        )

    @property
    def config(self) -> ConflictDetectionConfig:
        """Active detection configuration."""
        return self._config

    def detect_conflicts(
        self,
        world_model: WorldModel,
        now: float,
    ) -> list[ConflictReport]:
        """Detect all spatial and temporal coordination conflicts for the local robot.

        A ConflictReport is generated when the configured coordination detection
        criteria are satisfied:
        1. Spatial Contention: Own intent and peer intent/reservation target the
           same non-empty resource_id.
        2. Temporal Contention: Time intervals overlap under open-interval semantics
           (own_start < peer_end and peer_start < own_end).
        3. Threshold Compliance: Overlap duration meets or exceeds min_temporal_overlap_seconds.
        4. Planning Horizon: Earliest conflict onset is within planning_horizon_seconds.

        Args:
            world_model: The local robot's WorldModel (read-only).
            now: Current reference timestamp (Unix epoch seconds).

        Returns:
            Deterministically sorted list of ConflictReports.
        """
        own_intent = world_model.get_own_intent()
        if own_intent is None:
            return []

        resource_id = own_intent.target_resource_id
        if not resource_id:
            return []

        default_duration = world_model.config.timeouts.default_reservation_duration_seconds
        own_window = self._derive_intent_window(own_intent, now, default_duration)
        if own_window is None:
            return []

        own_start, own_end = own_window
        min_overlap = self._config.min_temporal_overlap_seconds
        horizon_limit = now + self._config.planning_horizon_seconds

        # Map: peer_robot_id -> list of overlapping intervals (overlap_start, overlap_end)
        evidence_map: dict[str, list[tuple[float, float]]] = {}

        # ---------------------------------------------------------------------
        # 1. Collect Intent Evidence
        # ---------------------------------------------------------------------
        peer_intents = world_model.get_intents_for_resource(resource_id, now)
        for peer_intent in peer_intents:
            if peer_intent.robot_id == world_model.robot_id:
                continue

            peer_window = self._derive_intent_window(peer_intent, now, default_duration)
            if peer_window is None:
                continue

            peer_start, peer_end = peer_window
            if self._intervals_overlap(own_start, own_end, peer_start, peer_end):
                o_start = max(own_start, peer_start)
                o_end = min(own_end, peer_end)
                if (o_end - o_start) >= min_overlap:
                    evidence_map.setdefault(peer_intent.robot_id, []).append(
                        (o_start, o_end)
                    )

        # ---------------------------------------------------------------------
        # 2. Collect Reservation Evidence
        # ---------------------------------------------------------------------
        reservations = world_model.get_reservations_for_resource(resource_id, now)
        for res in reservations:
            # Own reservations are not conflicts; peer reservations are evaluated
            if res.robot_id == world_model.robot_id:
                continue

            res_start, res_end = res.start_time, res.end_time
            if self._intervals_overlap(own_start, own_end, res_start, res_end):
                o_start = max(own_start, res_start)
                o_end = min(own_end, res_end)
                if (o_end - o_start) >= min_overlap:
                    evidence_map.setdefault(res.robot_id, []).append(
                        (o_start, o_end)
                    )

        # ---------------------------------------------------------------------
        # 3. Aggregate Evidence per Peer & Build Reports
        # ---------------------------------------------------------------------
        conflicts: list[ConflictReport] = []

        for peer_id, intervals in evidence_map.items():
            if not intervals:
                continue

            # Earliest conflict onset determines severity and horizon check
            bounding_start = min(s for s, e in intervals)
            bounding_end = max(e for s, e in intervals)

            if bounding_start > horizon_limit:
                continue

            severity = self._compute_severity(bounding_start, now)
            report = ConflictReport(
                robot_a_id=world_model.robot_id,
                robot_b_id=peer_id,
                resource_id=resource_id,
                overlap_start=bounding_start,
                overlap_end=bounding_end,
                severity=severity,
                detected_at=now,
            )
            conflicts.append(report)

        # ---------------------------------------------------------------------
        # 4. Deterministic Ordering
        # ---------------------------------------------------------------------
        conflicts.sort(
            key=lambda c: (
                self._severity_rank(c.severity),
                c.overlap_start,
                c.robot_b_id,
            )
        )
        return conflicts

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _derive_intent_window(
        self,
        intent: RobotIntent,
        now: float,
        default_duration: float,
    ) -> tuple[float, float] | None:
        """Derive the expected resource occupancy interval [T_start, T_end].

        Option C Occupancy Model:
        - T_start: If eta is provided and >= now, T_start = eta. If eta is None or
                   < now, T_start = now (conservative prototype assumption).
        - T_end: min(T_start + default_duration, intent.valid_until).

        Returns:
            (T_start, T_end) tuple, or None if the interval is invalid (T_end <= T_start).
        """
        start = intent.eta if (intent.eta is not None and intent.eta >= now) else now
        end = min(start + default_duration, intent.valid_until)
        if end <= start:
            return None
        return (start, end)

    @staticmethod
    def _intervals_overlap(
        a_start: float, a_end: float, b_start: float, b_end: float
    ) -> bool:
        """Open-interval overlap check: a_start < b_end and b_start < a_end."""
        return a_start < b_end and b_start < a_end

    @staticmethod
    def _compute_severity(overlap_start: float, now: float) -> ConflictSeverity:
        """Compute severity based on temporal proximity to the conflict onset."""
        time_to_conflict = overlap_start - now
        if time_to_conflict <= 0.0:
            return ConflictSeverity.CRITICAL
        elif time_to_conflict <= 10.0:
            return ConflictSeverity.HIGH
        elif time_to_conflict <= 30.0:
            return ConflictSeverity.MEDIUM
        else:
            return ConflictSeverity.LOW

    @staticmethod
    def _severity_rank(severity: ConflictSeverity) -> int:
        """Sort priority rank (CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3)."""
        ranks = {
            ConflictSeverity.CRITICAL: 0,
            ConflictSeverity.HIGH: 1,
            ConflictSeverity.MEDIUM: 2,
            ConflictSeverity.LOW: 3,
        }
        return ranks.get(severity, 99)
