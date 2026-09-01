"""
P5 Unit Tests — Phase 3 Capability Checking
=============================================

Tests every rule implemented in CapabilityChecker.

Test matrix
-----------
Case 01  — valid AVAILABLE robot, sufficient payload              → eligible
Case 02  — exact payload match (capacity == required)             → eligible
Case 03  — insufficient payload                                   → not eligible (PAYLOAD_INSUFFICIENT)
Case 04  — FAILED robot                                           → not eligible (ROBOT_FAILED)
Case 05  — OFFLINE robot                                          → not eligible (ROBOT_OFFLINE)
Case 06  — CHARGING robot                                         → not eligible (ROBOT_CHARGING)
Case 07  — BUSY robot                                             → not eligible (ROBOT_UNAVAILABLE)
Case 08  — CANCELLED task                                         → not eligible (TASK_CANCELLED)
Case 09  — COMPLETED task                                         → not eligible (TASK_COMPLETED)
Case 10  — None robot                                             → not eligible (TASK_INVALID)
Case 11  — None task                                              → not eligible (TASK_INVALID)
Case 12  — RECOVERED robot (should be eligible from status)       → eligible (if payload ok)
Case 13  — task in ANNOUNCED/BIDDING/IN_PROGRESS/ASSIGNED/FAILED/RECOVERY
           (active non-terminal states — eligible from task-status perspective)
Case 14  — missing capability tag                                 → not eligible (MISSING_CAPABILITY)
Case 15  — multiple failure reasons (FAILED robot + bad payload)  → both reason codes present
Case 16  — determinism (identical inputs → identical output twice)
Case 17  — checker does not mutate Robot or Task
Case 18  — negative required_payload on task                      → TASK_INVALID
Case 19  — legacy is_eligible() wraps check()
Case 20  — CapabilityResult __str__ smoke test

No ROS 2, Gazebo, Nav2, or any external dependency is required.
All test data comes from conftest.py fixtures and local construction.
"""

from __future__ import annotations

import dataclasses

import pytest

from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.allocation.capability import (
    CapabilityChecker,
    CapabilityResult,
    ROBOT_UNAVAILABLE,
    ROBOT_FAILED,
    ROBOT_OFFLINE,
    ROBOT_CHARGING,
    PAYLOAD_INSUFFICIENT,
    MISSING_CAPABILITY,
    TASK_INVALID,
    TASK_CANCELLED,
    TASK_COMPLETED,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _robot(
    *,
    robot_id: str = "X",
    status: RobotStatus = RobotStatus.AVAILABLE,
    payload_capacity: float = 500.0,
    capabilities: tuple = ("CARRY",),
) -> Robot:
    """Build a minimal Robot for testing."""
    return Robot(
        robot_id=robot_id,
        position=(0.0, 0.0),
        battery=80.0,
        payload_capacity=payload_capacity,
        current_task=None,
        workload=0,
        status=status,
        capabilities=capabilities,
    )


def _task(
    *,
    task_id: str = "T99",
    status: TaskStatus = TaskStatus.AVAILABLE,
    required_payload: float = 100.0,
    required_capabilities: tuple = ("CARRY",),
) -> Task:
    """Build a minimal Task for testing."""
    return Task(
        task_id=task_id,
        pickup_location=(1.0, 1.0),
        dropoff_location=(5.0, 5.0),
        priority=5,
        deadline=60.0,
        required_payload=required_payload,
        status=status,
        assigned_robot=None,
        required_capabilities=required_capabilities,
    )


# ---------------------------------------------------------------------------
# Shared checker instance
# ---------------------------------------------------------------------------

@pytest.fixture()
def checker() -> CapabilityChecker:
    """A shared CapabilityChecker instance (stateless)."""
    return CapabilityChecker()


# ===========================================================================
# CASE 01 — Valid AVAILABLE robot, sufficient payload
# ===========================================================================

class TestCase01ValidAvailableRobot:
    def test_eligible(self, checker: CapabilityChecker):
        """AVAILABLE robot with capacity 500 vs required 100 → eligible."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is True
        assert result.reasons == ()

    def test_robot_id_in_result(self, checker: CapabilityChecker):
        """robot_id field matches."""
        robot = _robot(robot_id="A")
        task  = _task(task_id="T01")
        result = checker.check(robot, task)
        assert result.robot_id == "A"
        assert result.task_id  == "T01"


# ===========================================================================
# CASE 02 — Exact payload match (capacity == required)
# ===========================================================================

class TestCase02ExactPayloadMatch:
    def test_equal_payload_is_eligible(self, checker: CapabilityChecker):
        """capacity 100, required 100 → eligible (uses <=)."""
        robot = _robot(payload_capacity=100.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is True
        assert PAYLOAD_INSUFFICIENT not in result.reasons

    def test_one_under_limit(self, checker: CapabilityChecker):
        """capacity 99, required 100 → NOT eligible."""
        robot = _robot(payload_capacity=99.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert PAYLOAD_INSUFFICIENT in result.reasons


# ===========================================================================
# CASE 03 — Insufficient payload
# ===========================================================================

class TestCase03InsufficientPayload:
    def test_ineligible(self, checker: CapabilityChecker):
        """capacity 50, required 100 → PAYLOAD_INSUFFICIENT."""
        robot = _robot(payload_capacity=50.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert PAYLOAD_INSUFFICIENT in result.reasons

    def test_exactly_one_reason(self, checker: CapabilityChecker):
        """Only payload is wrong — exactly one reason code."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=50.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.reasons == (PAYLOAD_INSUFFICIENT,)


# ===========================================================================
# CASE 04 — FAILED robot
# ===========================================================================

class TestCase04FailedRobot:
    def test_ineligible(self, checker: CapabilityChecker):
        """FAILED robot → not eligible."""
        robot = _robot(status=RobotStatus.FAILED, payload_capacity=500.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert ROBOT_FAILED in result.reasons

    def test_reason_code_is_robot_failed(self, checker: CapabilityChecker):
        """Reason code is ROBOT_FAILED, not ROBOT_UNAVAILABLE."""
        robot = _robot(status=RobotStatus.FAILED)
        task  = _task()
        result = checker.check(robot, task)
        assert ROBOT_FAILED in result.reasons
        assert ROBOT_UNAVAILABLE not in result.reasons


# ===========================================================================
# CASE 05 — OFFLINE robot
# ===========================================================================

class TestCase05OfflineRobot:
    def test_ineligible(self, checker: CapabilityChecker):
        """OFFLINE robot → not eligible."""
        robot = _robot(status=RobotStatus.OFFLINE)
        task  = _task()
        result = checker.check(robot, task)
        assert result.eligible is False
        assert ROBOT_OFFLINE in result.reasons

    def test_reason_is_robot_offline(self, checker: CapabilityChecker):
        robot = _robot(status=RobotStatus.OFFLINE)
        task  = _task()
        result = checker.check(robot, task)
        assert ROBOT_OFFLINE in result.reasons
        assert ROBOT_FAILED not in result.reasons


# ===========================================================================
# CASE 06 — CHARGING robot
# ===========================================================================

class TestCase06ChargingRobot:
    def test_ineligible(self, checker: CapabilityChecker):
        """CHARGING robot → not eligible."""
        robot = _robot(status=RobotStatus.CHARGING)
        task  = _task()
        result = checker.check(robot, task)
        assert result.eligible is False
        assert ROBOT_CHARGING in result.reasons

    def test_reason_is_robot_charging(self, checker: CapabilityChecker):
        robot = _robot(status=RobotStatus.CHARGING)
        task  = _task()
        result = checker.check(robot, task)
        assert ROBOT_CHARGING in result.reasons
        assert ROBOT_OFFLINE not in result.reasons


# ===========================================================================
# CASE 07 — BUSY robot
# ===========================================================================

class TestCase07BusyRobot:
    """Phase 2 establishes that BUSY robots are not eligible for new tasks.

    P5 does not support parallel task assignment in this architecture.
    BUSY robots produce ROBOT_UNAVAILABLE.
    """

    def test_ineligible(self, checker: CapabilityChecker):
        """BUSY robot → not eligible (parallel work not supported)."""
        robot = _robot(status=RobotStatus.BUSY)
        task  = _task()
        result = checker.check(robot, task)
        assert result.eligible is False
        assert ROBOT_UNAVAILABLE in result.reasons

    def test_reason_is_unavailable_not_failed(self, checker: CapabilityChecker):
        robot = _robot(status=RobotStatus.BUSY)
        task  = _task()
        result = checker.check(robot, task)
        assert ROBOT_UNAVAILABLE in result.reasons
        assert ROBOT_FAILED not in result.reasons


# ===========================================================================
# CASE 08 — CANCELLED task
# ===========================================================================

class TestCase08CancelledTask:
    def test_ineligible(self, checker: CapabilityChecker):
        """CANCELLED task → not eligible."""
        robot = _robot(status=RobotStatus.AVAILABLE)
        task  = _task(status=TaskStatus.CANCELLED)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert TASK_CANCELLED in result.reasons

    def test_reason_is_task_cancelled(self, checker: CapabilityChecker):
        robot = _robot()
        task  = _task(status=TaskStatus.CANCELLED)
        result = checker.check(robot, task)
        assert TASK_CANCELLED in result.reasons
        assert TASK_COMPLETED not in result.reasons


# ===========================================================================
# CASE 09 — COMPLETED task
# ===========================================================================

class TestCase09CompletedTask:
    def test_ineligible(self, checker: CapabilityChecker):
        """COMPLETED task → not eligible."""
        robot = _robot(status=RobotStatus.AVAILABLE)
        task  = _task(status=TaskStatus.COMPLETED)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert TASK_COMPLETED in result.reasons

    def test_reason_is_task_completed(self, checker: CapabilityChecker):
        robot = _robot()
        task  = _task(status=TaskStatus.COMPLETED)
        result = checker.check(robot, task)
        assert TASK_COMPLETED in result.reasons
        assert TASK_CANCELLED not in result.reasons


# ===========================================================================
# CASE 10 — Invalid input (None)
# ===========================================================================

class TestCase10InvalidInput:
    def test_none_robot_does_not_crash(self, checker: CapabilityChecker):
        """None robot → clean rejection, no AttributeError."""
        task = _task()
        result = checker.check(None, task)
        assert isinstance(result, CapabilityResult)
        assert result.eligible is False
        assert TASK_INVALID in result.reasons

    def test_none_task_does_not_crash(self, checker: CapabilityChecker):
        """None task → clean rejection, no AttributeError."""
        robot = _robot()
        result = checker.check(robot, None)
        assert isinstance(result, CapabilityResult)
        assert result.eligible is False
        assert TASK_INVALID in result.reasons

    def test_none_robot_robot_id_is_placeholder(self, checker: CapabilityChecker):
        """robot_id is '<none>' when robot is None."""
        result = checker.check(None, _task())
        assert result.robot_id == "<none>"

    def test_none_task_task_id_is_placeholder(self, checker: CapabilityChecker):
        """task_id is '<none>' when task is None."""
        result = checker.check(_robot(), None)
        assert result.task_id == "<none>"

    def test_both_none_does_not_crash(self, checker: CapabilityChecker):
        """Both None → clean rejection."""
        result = checker.check(None, None)
        assert result.eligible is False
        assert TASK_INVALID in result.reasons


# ===========================================================================
# CASE 11 — RECOVERED robot (eligible from status perspective)
# ===========================================================================

class TestCase11RecoveredRobot:
    def test_eligible_when_payload_ok(self, checker: CapabilityChecker):
        """RECOVERED robot with sufficient payload → eligible."""
        robot = _robot(status=RobotStatus.RECOVERED, payload_capacity=500.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is True
        assert result.reasons == ()

    def test_no_status_reason_for_recovered(self, checker: CapabilityChecker):
        """RECOVERED is not penalised with a status reason code."""
        robot = _robot(status=RobotStatus.RECOVERED)
        task  = _task()
        result = checker.check(robot, task)
        assert ROBOT_FAILED      not in result.reasons
        assert ROBOT_OFFLINE     not in result.reasons
        assert ROBOT_CHARGING    not in result.reasons
        assert ROBOT_UNAVAILABLE not in result.reasons


# ===========================================================================
# CASE 12 — Active (non-terminal) task statuses
# ===========================================================================

class TestCase12ActiveTaskStatuses:
    """Tasks in AVAILABLE, ANNOUNCED, BIDDING, ASSIGNED, IN_PROGRESS,
    FAILED, or RECOVERY are NOT rejected on task-status alone.
    Only CANCELLED and COMPLETED are rejected."""

    @pytest.mark.parametrize("status", [
        TaskStatus.AVAILABLE,
        TaskStatus.ANNOUNCED,
        TaskStatus.BIDDING,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
        TaskStatus.FAILED,
        TaskStatus.RECOVERY,
    ])
    def test_active_status_not_rejected_by_task_check(
        self, checker: CapabilityChecker, status: TaskStatus
    ):
        """Task in active state is not blocked by task-status check."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(status=status, required_payload=100.0)
        result = checker.check(robot, task)
        # Task status itself should not add any rejection reason
        assert TASK_CANCELLED not in result.reasons
        assert TASK_COMPLETED not in result.reasons
        assert TASK_INVALID   not in result.reasons


# ===========================================================================
# CASE 13 — Missing capability tag
# ===========================================================================

class TestCase13MissingCapability:
    def test_missing_capability_ineligible(self, checker: CapabilityChecker):
        """Robot lacks a required capability tag → MISSING_CAPABILITY."""
        robot = _robot(capabilities=("CARRY",))
        task  = _task(required_capabilities=("CARRY", "LIFT"))
        result = checker.check(robot, task)
        assert result.eligible is False
        assert MISSING_CAPABILITY in result.reasons

    def test_all_capabilities_present(self, checker: CapabilityChecker):
        """Robot has all required tags → no MISSING_CAPABILITY."""
        robot = _robot(capabilities=("CARRY", "LIFT", "HAZMAT"))
        task  = _task(required_capabilities=("CARRY", "LIFT"))
        result = checker.check(robot, task)
        assert MISSING_CAPABILITY not in result.reasons

    def test_no_required_capabilities(self, checker: CapabilityChecker):
        """Task with empty required_capabilities → no tag check failure."""
        robot = _robot(capabilities=())
        task  = _task(required_capabilities=())
        result = checker.check(robot, task)
        assert MISSING_CAPABILITY not in result.reasons

    def test_missing_capability_reason_appears_once(self, checker: CapabilityChecker):
        """Even if two tags are missing, MISSING_CAPABILITY appears only once."""
        robot = _robot(capabilities=())
        task  = _task(required_capabilities=("CARRY", "LIFT"))
        result = checker.check(robot, task)
        assert result.reasons.count(MISSING_CAPABILITY) == 1


# ===========================================================================
# CASE 14 — Multiple failure reasons
# ===========================================================================

class TestCase14MultipleFailureReasons:
    def test_failed_robot_plus_bad_payload(self, checker: CapabilityChecker):
        """FAILED robot AND insufficient payload → both reason codes present."""
        robot = _robot(status=RobotStatus.FAILED, payload_capacity=50.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert ROBOT_FAILED         in result.reasons
        assert PAYLOAD_INSUFFICIENT in result.reasons

    def test_cancelled_task_plus_bad_payload(self, checker: CapabilityChecker):
        """CANCELLED task AND bad payload → both reasons reported."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=10.0)
        task  = _task(status=TaskStatus.CANCELLED, required_payload=100.0)
        result = checker.check(robot, task)
        assert TASK_CANCELLED       in result.reasons
        assert PAYLOAD_INSUFFICIENT in result.reasons

    def test_no_duplicate_reason_codes(self, checker: CapabilityChecker):
        """Reason codes must not be duplicated in the result."""
        robot = _robot(status=RobotStatus.FAILED, payload_capacity=50.0)
        task  = _task(required_payload=100.0)
        result = checker.check(robot, task)
        assert len(result.reasons) == len(set(result.reasons)), (
            f"Duplicate reason codes found: {result.reasons}"
        )


# ===========================================================================
# CASE 15 — Negative required_payload (invalid task data)
# ===========================================================================

class TestCase15NegativePayload:
    def test_negative_payload_is_invalid(self, checker: CapabilityChecker):
        """required_payload < 0 → TASK_INVALID reason code."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(required_payload=-1.0)
        result = checker.check(robot, task)
        assert result.eligible is False
        assert TASK_INVALID in result.reasons

    def test_zero_payload_is_valid(self, checker: CapabilityChecker):
        """required_payload == 0.0 is valid — a task with no payload requirement."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(required_payload=0.0)
        result = checker.check(robot, task)
        assert TASK_INVALID not in result.reasons


# ===========================================================================
# CASE 16 — Determinism
# ===========================================================================

class TestCase16Determinism:
    def test_same_inputs_same_result_eligible(self, checker: CapabilityChecker):
        """Calling check() twice with eligible inputs returns identical results."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(required_payload=100.0)
        result1 = checker.check(robot, task)
        result2 = checker.check(robot, task)
        assert result1 == result2

    def test_same_inputs_same_result_ineligible(self, checker: CapabilityChecker):
        """Calling check() twice with ineligible inputs returns identical results."""
        robot = _robot(status=RobotStatus.FAILED, payload_capacity=50.0)
        task  = _task(required_payload=100.0)
        result1 = checker.check(robot, task)
        result2 = checker.check(robot, task)
        assert result1 == result2

    def test_multiple_calls_with_none(self, checker: CapabilityChecker):
        """None input returns same result each time."""
        result1 = checker.check(None, _task())
        result2 = checker.check(None, _task())
        assert result1 == result2

    def test_10_repeated_calls(self, checker: CapabilityChecker):
        """Ten consecutive calls with the same data produce identical results."""
        robot = _robot()
        task  = _task()
        results = [checker.check(robot, task) for _ in range(10)]
        assert all(r == results[0] for r in results), (
            "Non-deterministic output detected across repeated calls"
        )


# ===========================================================================
# CASE 17 — Checker does not mutate Robot or Task
# ===========================================================================

class TestCase17Immutability:
    def test_robot_not_mutated(self, checker: CapabilityChecker):
        """CapabilityChecker must not change any Robot field."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        original_status   = robot.status
        original_task     = robot.current_task
        original_workload = robot.workload
        original_capacity = robot.payload_capacity

        checker.check(robot, _task())

        assert robot.status           == original_status
        assert robot.current_task     == original_task
        assert robot.workload         == original_workload
        assert robot.payload_capacity == original_capacity

    def test_task_not_mutated(self, checker: CapabilityChecker):
        """CapabilityChecker must not change any Task field."""
        task = _task(status=TaskStatus.AVAILABLE)
        original_status   = task.status
        original_robot    = task.assigned_robot
        original_payload  = task.required_payload

        checker.check(_robot(), task)

        assert task.status          == original_status
        assert task.assigned_robot  == original_robot
        assert task.required_payload == original_payload


# ===========================================================================
# CASE 18 — Legacy is_eligible() compatibility
# ===========================================================================

class TestCase18LegacyIsEligible:
    def test_is_eligible_returns_true_when_eligible(self, checker: CapabilityChecker):
        """is_eligible() returns True for a valid robot-task pair."""
        robot = _robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0)
        task  = _task(required_payload=100.0)
        assert checker.is_eligible(robot, task) is True

    def test_is_eligible_returns_false_when_ineligible(self, checker: CapabilityChecker):
        """is_eligible() returns False for FAILED robot."""
        robot = _robot(status=RobotStatus.FAILED)
        task  = _task()
        assert checker.is_eligible(robot, task) is False

    def test_is_eligible_consistent_with_check(self, checker: CapabilityChecker):
        """is_eligible() result must always match check().eligible."""
        pairs = [
            (_robot(status=RobotStatus.AVAILABLE, payload_capacity=500.0), _task()),
            (_robot(status=RobotStatus.FAILED), _task()),
            (_robot(payload_capacity=10.0), _task(required_payload=100.0)),
            (_robot(status=RobotStatus.CHARGING), _task()),
        ]
        for robot, task in pairs:
            assert checker.is_eligible(robot, task) == checker.check(robot, task).eligible


# ===========================================================================
# CASE 19 — CapabilityResult fields and __str__
# ===========================================================================

class TestCase19CapabilityResult:
    def test_result_is_frozen_dataclass(self, checker: CapabilityChecker):
        """CapabilityResult is immutable (frozen dataclass)."""
        result = checker.check(_robot(), _task())
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.eligible = not result.eligible  # type: ignore[misc]

    def test_str_eligible(self, checker: CapabilityChecker):
        """__str__ of an eligible result contains 'ELIGIBLE'."""
        robot = _robot()
        task  = _task()
        result = checker.check(robot, task)
        assert "ELIGIBLE" in str(result)

    def test_str_ineligible_shows_reasons(self, checker: CapabilityChecker):
        """__str__ of an ineligible result contains the reason code."""
        robot = _robot(status=RobotStatus.FAILED)
        task  = _task()
        result = checker.check(robot, task)
        assert "ROBOT_FAILED" in str(result)

    def test_reasons_is_tuple(self, checker: CapabilityChecker):
        """reasons field is always a tuple, never a list."""
        result = checker.check(_robot(), _task())
        assert isinstance(result.reasons, tuple)


# ===========================================================================
# CASE 20 — conftest fixture integration
# ===========================================================================

class TestCase20FixtureIntegration:
    """Verify that the checker works correctly with the shared conftest fixtures."""

    def test_robot_a_eligible_for_t01(
        self,
        checker: CapabilityChecker,
        robot_a: Robot,
        task_t01: Task,
    ):
        """Robot A (AVAILABLE, capacity 500) is eligible for T01 (required 100)."""
        result = checker.check(robot_a, task_t01)
        assert result.eligible is True

    def test_robot_b_eligible_for_t01(
        self,
        checker: CapabilityChecker,
        robot_b: Robot,
        task_t01: Task,
    ):
        """Robot B (AVAILABLE, capacity 300) is eligible for T01 (required 100)."""
        result = checker.check(robot_b, task_t01)
        assert result.eligible is True

    def test_robot_c_ineligible_busy(
        self,
        checker: CapabilityChecker,
        robot_c: Robot,
        task_t01: Task,
    ):
        """Robot C is BUSY → not eligible for a new task."""
        result = checker.check(robot_c, task_t01)
        assert result.eligible is False
        assert ROBOT_UNAVAILABLE in result.reasons
