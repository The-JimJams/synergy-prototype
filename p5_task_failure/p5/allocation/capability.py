"""
P5 Capability Checker — Phase 3
================================

Determines whether a specific robot is ELIGIBLE to perform a specific task.

This is a FILTER only.  It answers:

    "Can this robot perform this task?"

It does NOT answer:

    "Which robot should perform this task?"

That second question belongs to Phase 4 (bidding) and Phase 5 (winner
selection), which are deliberately deferred and remain stubs.

Design principles
-----------------
- Pure: never mutates Robot or Task.
- Deterministic: same inputs always produce the same result.
- No side effects: does not assign tasks, create bids, or select winners.
- No external dependencies: works with the P5 Robot and Task models only.
- All checks: accumulates all failure reasons so debugging is easy.

Short-circuit policy
--------------------
The checker does NOT short-circuit after the first failure.  Instead it
evaluates ALL applicable checks and collects every reason code that
applies.  This makes it easier to diagnose multi-failure scenarios (e.g.
a robot that is both FAILED and has insufficient payload).

Reason codes
------------
ROBOT_UNAVAILABLE   — robot status is BUSY (parallel work not supported)
ROBOT_FAILED        — robot status is FAILED
ROBOT_OFFLINE       — robot status is OFFLINE
ROBOT_CHARGING      — robot status is CHARGING
PAYLOAD_INSUFFICIENT — robot.payload_capacity < task.required_payload
MISSING_CAPABILITY   — robot lacks a tag required by the task
TASK_INVALID        — task is None or has an invalid required_payload
TASK_CANCELLED      — task.status is CANCELLED
TASK_COMPLETED      — task.status is COMPLETED

Phase boundary
--------------
Phase 3: CapabilityChecker — eligibility checking.  IMPLEMENTED.
Phase 4: Bidder            — bid score calculation.  STUB (not implemented).
Phase 5: WinnerSelector    — winner selection.       STUB (not implemented).
"""

from __future__ import annotations

import dataclasses
from typing import List, Optional, Tuple

from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus


# ---------------------------------------------------------------------------
# Reason codes (deterministic string constants — never randomised)
# ---------------------------------------------------------------------------

ROBOT_UNAVAILABLE    = "ROBOT_UNAVAILABLE"
ROBOT_FAILED         = "ROBOT_FAILED"
ROBOT_OFFLINE        = "ROBOT_OFFLINE"
ROBOT_CHARGING       = "ROBOT_CHARGING"
PAYLOAD_INSUFFICIENT = "PAYLOAD_INSUFFICIENT"
MISSING_CAPABILITY   = "MISSING_CAPABILITY"
TASK_INVALID         = "TASK_INVALID"
TASK_CANCELLED       = "TASK_CANCELLED"
TASK_COMPLETED       = "TASK_COMPLETED"


# ---------------------------------------------------------------------------
# CapabilityResult
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class CapabilityResult:
    """Immutable result of a single capability check.

    Attributes
    ----------
    eligible : bool
        True only if the robot passed ALL capability checks for the task.
    robot_id : str
        The robot that was checked (``"<none>"`` if robot was None).
    task_id : str
        The task that was checked (``"<none>"`` if task was None).
    reasons : Tuple[str, ...]
        Ordered, deduplicated tuple of reason codes explaining why
        ``eligible`` is False.  Empty when ``eligible`` is True.

    Examples
    --------
    Eligible result::

        CapabilityResult(
            eligible=True,
            robot_id="A",
            task_id="T01",
            reasons=(),
        )

    Ineligible result::

        CapabilityResult(
            eligible=False,
            robot_id="B",
            task_id="T01",
            reasons=("PAYLOAD_INSUFFICIENT",),
        )
    """

    eligible: bool
    robot_id: str
    task_id: str
    reasons: Tuple[str, ...]

    def __str__(self) -> str:
        if self.eligible:
            return (
                f"CapabilityResult(ELIGIBLE  robot={self.robot_id!r}"
                f"  task={self.task_id!r})"
            )
        return (
            f"CapabilityResult(NOT ELIGIBLE  robot={self.robot_id!r}"
            f"  task={self.task_id!r}"
            f"  reasons={list(self.reasons)})"
        )


# ---------------------------------------------------------------------------
# CapabilityChecker
# ---------------------------------------------------------------------------

class CapabilityChecker:
    """Checks whether a robot is eligible to perform a task.

    This is a stateless, pure checker.  Instantiate once and call
    ``check()`` (or the legacy ``is_eligible()``) as many times as needed.

    Usage
    -----
    ::

        checker = CapabilityChecker()

        result = checker.check(robot_a, task_t01)

        if result.eligible:
            print("Robot A is eligible")
        else:
            print("Robot A is not eligible:", result.reasons)

    Short-circuit policy
    --------------------
    All applicable checks are evaluated.  No early-exit after the first
    failure.  This gives callers the full picture in one call.

    Determinism guarantee
    ---------------------
    ``check(robot, task)`` called with the same robot and task objects
    (same field values) will always return an identical ``CapabilityResult``.
    There is no randomness, no global state, and no time-dependent logic.
    """

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def check(self, robot: Optional[Robot], task: Optional[Task]) -> CapabilityResult:
        """Evaluate whether *robot* is eligible to perform *task*.

        Parameters
        ----------
        robot : Robot | None
            The robot to check.  Passing ``None`` produces an ineligible
            result with reason ``TASK_INVALID`` (invalid input).
        task : Task | None
            The task to check.  Passing ``None`` produces an ineligible
            result with reason ``TASK_INVALID`` (invalid input).

        Returns
        -------
        CapabilityResult
            Always returns a well-formed result — never raises an
            ``AttributeError`` on None inputs.
        """
        robot_id = robot.robot_id if robot is not None else "<none>"
        task_id  = task.task_id  if task  is not None else "<none>"

        reasons: List[str] = []

        # ---- Guard: None inputs ----
        if robot is None or task is None:
            reasons.append(TASK_INVALID)
            return CapabilityResult(
                eligible=False,
                robot_id=robot_id,
                task_id=task_id,
                reasons=tuple(reasons),
            )

        # ---- Task validity check ----
        # Reject invalid required_payload (negative values are nonsensical).
        if task.required_payload < 0:
            reasons.append(TASK_INVALID)

        # ---- Task status checks ----
        if task.status == TaskStatus.CANCELLED:
            reasons.append(TASK_CANCELLED)
        elif task.status == TaskStatus.COMPLETED:
            reasons.append(TASK_COMPLETED)

        # ---- Robot status checks ----
        if robot.status == RobotStatus.FAILED:
            reasons.append(ROBOT_FAILED)
        elif robot.status == RobotStatus.OFFLINE:
            reasons.append(ROBOT_OFFLINE)
        elif robot.status == RobotStatus.CHARGING:
            reasons.append(ROBOT_CHARGING)
        elif robot.status == RobotStatus.BUSY:
            # BUSY robots are not eligible for new tasks in this architecture.
            # Parallel task assignment is not supported in P5.
            # This policy is documented here and enforced in Phase 3.
            reasons.append(ROBOT_UNAVAILABLE)
        # AVAILABLE and RECOVERED are eligible from a status perspective.

        # ---- Payload check ----
        # task.required_payload <= robot.payload_capacity to pass.
        if task.required_payload > robot.payload_capacity:
            reasons.append(PAYLOAD_INSUFFICIENT)

        # ---- Capability tag check ----
        for cap in task.required_capabilities:
            if cap not in robot.capabilities:
                if MISSING_CAPABILITY not in reasons:
                    reasons.append(MISSING_CAPABILITY)

        eligible = len(reasons) == 0
        return CapabilityResult(
            eligible=eligible,
            robot_id=robot_id,
            task_id=task_id,
            reasons=tuple(reasons),
        )

    # ------------------------------------------------------------------
    # Legacy compatibility shim
    # ------------------------------------------------------------------

    def is_eligible(self, robot: Optional[Robot], task: Optional[Task]) -> bool:
        """Return True if the robot is eligible for the task.

        This is a convenience wrapper around ``check()``.  Prefer
        ``check()`` when reason codes are needed.

        Previously raised ``NotImplementedError`` in Phase 1.
        Now fully implemented in Phase 3.
        """
        return self.check(robot, task).eligible
