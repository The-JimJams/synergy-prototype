"""
P5 Task Recovery Manager — Phase 11–14 Stub
=============================================

DEFERRED to Phase 11 (task release), Phase 12 (re-announcement),
Phase 13 (reassignment), Phase 14 (full recovery).

Future responsibility:
  Implement the TaskRecoveryManager protocol.

Recovery flow (Phase 14):
  1. FailureDetector reports robot_id as FAILED.
  2. TaskRecoveryManager.release_task(task_id):
       - Set task.status = RECOVERY
       - Clear task.assigned_robot
  3. TaskRecoveryManager.re_announce_task(task_id):
       - Set task.status = ANNOUNCED
       - Trigger a new bid round via the allocation system
  4. BidCalculator + WinnerSelector determine the new winner.
  5. New robot is assigned and navigation goal is sent.
"""

from __future__ import annotations


from p5.models.task import Task, TaskStatus
from p5.models.robot import Robot, RobotStatus

class TaskRecoveryManager:
    def recover(self, task: Task, failed_robot: Robot) -> None:
        if task.assigned_robot == failed_robot.robot_id:
            task.assigned_robot = None
            task.status = TaskStatus.AVAILABLE
            
        if failed_robot.current_task == task.task_id:
            failed_robot.current_task = None
