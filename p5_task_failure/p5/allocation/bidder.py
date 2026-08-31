"""
P5 Bidder — Phase 4 Stub
=========================

DEFERRED to Phase 4.

Future responsibility:
  Implement the BidCalculator protocol.  Given a Robot and a Task,
  calculate a composite bid score and return a populated Bid object.

Algorithm outline (Phase 4):
  score = (
      w_dist      * (1 / (distance + ε))       +
      w_battery   * (robot.battery / 100)       +
      w_workload  * (1 / (robot.workload + 1))  +
      w_priority  * task.priority
  )

  Where weights (w_*) are configurable constants.
  ε prevents division by zero when distance is 0.
"""

from __future__ import annotations

from p5.models.robot import Robot
from p5.models.task import Task
from p5.models.bid import Bid


class Bidder:
    """Calculates a bid for a (robot, task) pair.

    Phase 1: Not yet implemented — raises NotImplementedError.
    Phase 4: Will implement BidCalculator protocol.
    """

    def calculate_bid(self, robot: Robot, task: Task) -> Bid:
        """Calculate and return a Bid for the given robot-task pair.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 4.
        """
        raise NotImplementedError(
            "Bidder.calculate_bid() is deferred to Phase 4. "
            "See docs/p5_architecture.md for the deferred work list."
        )
