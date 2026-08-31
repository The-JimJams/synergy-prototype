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


class TaskRecoveryManager:
    """Releases and re-announces tasks after a robot failure.

    Phase 1: Stub only — methods raise NotImplementedError.
    Phase 14: Will implement TaskRecoveryManager protocol.
    """

    def release_task(self, task_id: str) -> None:
        """Move task to RECOVERY state and clear assigned_robot.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 11.
        """
        raise NotImplementedError(
            "TaskRecoveryManager.release_task() is deferred to Phase 11."
        )

    def re_announce_task(self, task_id: str) -> None:
        """Re-announce the task so remaining robots can bid.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 12.
        """
        raise NotImplementedError(
            "TaskRecoveryManager.re_announce_task() is deferred to Phase 12."
        )
