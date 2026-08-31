"""
P5 Capability Checker — Phase 3 Stub
=====================================

DEFERRED to Phase 3.

Future responsibility:
  Given a Robot and a Task, determine whether the robot possesses all
  required capabilities and sufficient payload capacity to accept the task.

Algorithm outline (Phase 3):
  1. Check robot.capabilities against task.required_capabilities.
  2. Check robot.payload_capacity >= task.required_payload.
  3. Check robot.battery above a minimum threshold.
  4. Return True only if ALL checks pass.
"""

from __future__ import annotations

from p5.models.robot import Robot
from p5.models.task import Task


class CapabilityChecker:
    """Checks whether a robot is eligible to bid on a task.

    Phase 1: Not yet implemented — raises NotImplementedError.
    Phase 3: Will implement the full eligibility check.
    """

    def is_eligible(self, robot: Robot, task: Task) -> bool:
        """Return True if the robot meets all task requirements.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 3.
        """
        raise NotImplementedError(
            "CapabilityChecker.is_eligible() is deferred to Phase 3. "
            "See docs/p5_architecture.md for the deferred work list."
        )
