"""
P5 Task Manager — Phase 6 Stub
================================

DEFERRED to Phase 6.

Future responsibility:
  Implement the central P5 coordination loop (within-process only —
  NOT a centralised decision-making server).

  The TaskManager orchestrates the following in a decentralised way:
    - Receives task announcements from TaskSource.
    - For each task, asks each robot's local FleetAgent to calculate a bid.
    - Collects bids and passes them to WinnerSelector.
    - Publishes the assignment via EventSink.
    - Monitors heartbeats and triggers TaskRecoveryManager on failure.

  Decentralisation note:
    In the real distributed system, each robot runs its own FleetAgent.
    In standalone simulation, multiple FleetAgent instances run in a
    single Python process to allow testing without ROS 2.
"""

from __future__ import annotations


from typing import List
from p5.models.task import Task, TaskStatus
from p5.models.robot import Robot, RobotStatus
from p5.allocation.capability import CapabilityChecker
from p5.allocation.bidder import Bidder
from p5.allocation.winner import WinnerSelector

class TaskManager:
    def __init__(self):
        self.capability_checker = CapabilityChecker()
        self.bidder = Bidder()
        self.winner_selector = WinnerSelector()

    def allocate_task(self, task: Task, robots: List[Robot]) -> None:
        capable_robots = [r for r in robots if self.capability_checker.check(r, task).eligible]
        bids = [self.bidder.create_bid(r, task) for r in capable_robots]
        winner_bid = self.winner_selector.select_winner(bids)
        
        if winner_bid:
            task.assigned_robot = winner_bid.robot_id
            task.status = TaskStatus.ASSIGNED
            
            for r in robots:
                if r.robot_id == winner_bid.robot_id:
                    r.status = RobotStatus.BUSY
                    r.current_task = task.task_id
                    break
