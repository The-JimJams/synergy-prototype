"""
PriorityDecision — the output of the PriorityEngine.
====================================================

Represents the deterministic resolution of a coordination conflict between
two competing robots over a shared spatial resource.

Consumed by:
- ReservationManager (to grant/deny resource claims based on winner)
- DecisionLogger (to record explainable audit trails)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class PriorityDecision:
    """Result of resolving a coordination conflict between two AMRs."""

    # Reference to the resolved conflict
    conflict_id: str

    # Competing robot identities & target resource
    robot_a_id: str
    robot_b_id: str
    resource_id: str

    # Raw composite priority scores
    score_a: float
    score_b: float

    # Detailed normalized factor breakdowns for auditability / explainability
    # e.g., {"task_priority": 0.8, "deadline_urgency": 0.5, "waiting_time": 0.2, "battery_urgency": 0.1}
    factors_a: dict[str, float] = field(default_factory=dict)
    factors_b: dict[str, float] = field(default_factory=dict)

    # Resolution outcome
    winner_id: str = ""
    loser_id: str = ""
    tie_broken_by_id: bool = False

    # Resolution metadata
    decided_at: float = field(default_factory=time.time)

    def is_winner(self, robot_id: str) -> bool:
        """Check if a specific robot won this priority arbitration."""
        return robot_id == self.winner_id

    def __repr__(self) -> str:
        tie_str = " (tie-break)" if self.tie_broken_by_id else ""
        return (
            f"PriorityDecision({self.robot_a_id} vs {self.robot_b_id} at {self.resource_id!r}: "
            f"winner={self.winner_id!r}{tie_str}, scores=[{self.score_a:.3f}, {self.score_b:.3f}])"
        )
