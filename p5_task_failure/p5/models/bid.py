"""
P5 Bid Model
============

Represents a bid submitted by a single robot for a single task.

Phase 1: Data structure only.
Phase 4: BidCalculator will populate score, estimated_time, distance, battery_cost.
Phase 5: WinnerSelector will compare Bid objects to determine the winning robot.

The bid score is intentionally left at 0.0 in Phase 1 because the scoring
algorithm (distance weighting, battery penalty, priority bonus, etc.)
is deferred to Phase 4.

A higher score indicates a MORE suitable match (robot is closer, has more
battery, lower workload, etc.).  The exact formula is TBD.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime


@dataclasses.dataclass
class Bid:
    """Internal P5 representation of a robot's bid for a task.

    Attributes
    ----------
    task_id : str
        The task being bid on.
    robot_id : str
        The robot submitting this bid.
    score : float
        Composite bid score.  Higher = better candidate.
        Set to 0.0 in Phase 1 (algorithm deferred to Phase 4).
    estimated_time : float
        Estimated seconds to complete the task from current position.
    distance : float
        Euclidean distance from robot's current position to task pickup.
    battery_cost : float
        Estimated battery consumed (percent) to complete the task.
    valid : bool
        False if this robot is ineligible (insufficient payload, wrong
        capabilities, critically low battery, etc.).
    timestamp : datetime
        When this bid was created (UTC).

    Example
    -------
    >>> from datetime import datetime, timezone
    >>> b = Bid(
    ...     task_id="T01",
    ...     robot_id="A",
    ...     score=0.0,
    ...     estimated_time=0.0,
    ...     distance=0.0,
    ...     battery_cost=0.0,
    ...     valid=True,
    ...     timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ... )
    """

    task_id: str
    robot_id: str
    score: float
    estimated_time: float
    distance: float
    battery_cost: float
    valid: bool
    timestamp: datetime

    def __str__(self) -> str:
        validity = "VALID" if self.valid else "INVALID"
        return (
            f"Bid({self.robot_id!r} -> {self.task_id!r}, "
            f"score={self.score:.3f}, "
            f"dist={self.distance:.2f}, "
            f"eta={self.estimated_time:.1f}s, "
            f"bat_cost={self.battery_cost:.1f}%, "
            f"{validity})"
        )
