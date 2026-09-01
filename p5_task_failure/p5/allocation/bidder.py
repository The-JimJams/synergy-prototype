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
    def create_bid(self, robot: Robot, task: Task) -> Bid:
        distance = robot.distance_to(task.pickup_location)
        estimated_time = distance / 1.0
        battery_cost = distance * 0.1
        score = distance + estimated_time + battery_cost
        
        from datetime import datetime, timezone
        return Bid(
            task_id=task.task_id,
            robot_id=robot.robot_id,
            score=score,
            estimated_time=estimated_time,
            distance=distance,
            battery_cost=battery_cost,
            valid=True,
            timestamp=datetime.now(timezone.utc)
        )
