"""
AssignmentDecision — Output of the TaskAllocator algorithm.
============================================================

Represents the deterministic winner and evaluation details of a task allocation
round across all candidate AMRs in the fleet.

reason codes:
  "ASSIGNED"            — Winner deterministically selected.
  "TASK_NOT_ASSIGNABLE" — Task status is not in (ANNOUNCED, BIDDING, FAILED, REASSIGNED).
  "NO_ELIGIBLE_ROBOT"   — No robot met all eligibility criteria.
  "ALREADY_ASSIGNED"    — Task is already assigned or in progress.
  "INVALID_TIMESTAMP"   — Timestamp now is NaN, infinite, or negative.

Zero ROS imports — pure dataclass.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from fleet_coordination.models.task_bid import TaskBid


@dataclass
class AssignmentDecision:
    """Result of evaluating and allocating a task across candidate AMRs."""

    task_id: str
    winner_id: str | None = None
    winner_score: float = 0.0
    all_bids: dict[str, TaskBid] = field(default_factory=dict)
    accepted: bool = False
    reason: str = ""
    tie_broken_by_id: bool = False
    decided_at: float = field(default_factory=time.time)

    def is_winner(self, robot_id: str) -> bool:
        """Check if a specific robot won this task allocation."""
        return self.accepted and (self.winner_id == robot_id)

    def __repr__(self) -> str:
        tie_str = " (tie-break)" if self.tie_broken_by_id else ""
        winner_str = f"winner={self.winner_id!r}{tie_str} (score={self.winner_score:.3f})" if self.accepted else f"unassigned ({self.reason})"
        return f"AssignmentDecision(task={self.task_id!r}, {winner_str})"
