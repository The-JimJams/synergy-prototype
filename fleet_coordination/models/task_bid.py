"""
TaskBid — Individual robot bid valuation for an announced task.
===============================================================

Represents the computed bid score and eligibility factors for a single AMR
evaluating a candidate task.

Zero ROS imports — pure immutable dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TaskBid:
    """Computed bid score and factor breakdown for one robot on a specific task."""

    task_id: str
    robot_id: str
    bid_score: float
    eligible: bool
    factors: dict[str, float] = field(default_factory=dict)
    ineligibility_reason: str | None = None

    def __repr__(self) -> str:
        status_str = f"score={self.bid_score:.3f}" if self.eligible else f"ineligible ({self.ineligibility_reason})"
        return f"TaskBid(task={self.task_id!r}, robot={self.robot_id!r}, {status_str})"
