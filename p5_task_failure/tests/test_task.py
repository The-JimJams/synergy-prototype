"""
P5 Unit Tests — Task Model
===========================

Tests that the Task dataclass, TaskStatus enum, and transition map
behave correctly.

No ROS 2, Gazebo, Nav2, or other external dependency is required.
"""

from __future__ import annotations

import pytest
from p5.models.task import Task, TaskStatus, TASK_TRANSITIONS


# ---------------------------------------------------------------------------
# TaskStatus enum
# ---------------------------------------------------------------------------

class TestTaskStatus:
    def test_all_nine_states_defined(self):
        """All 9 required task states must be present."""
        expected = {
            "AVAILABLE", "ANNOUNCED", "BIDDING", "ASSIGNED",
            "IN_PROGRESS", "COMPLETED", "FAILED", "RECOVERY", "CANCELLED",
        }
        actual = {s.value for s in TaskStatus}
        assert expected == actual, f"Missing: {expected - actual}"

    def test_status_values_are_strings(self):
        """Each status value must be a plain string."""
        for s in TaskStatus:
            assert isinstance(s.value, str)

    def test_lookup_by_value(self):
        """Enum members can be retrieved by value."""
        assert TaskStatus("AVAILABLE") is TaskStatus.AVAILABLE
        assert TaskStatus("RECOVERY") is TaskStatus.RECOVERY


# ---------------------------------------------------------------------------
# Transition map
# ---------------------------------------------------------------------------

class TestTaskTransitions:
    def test_all_states_have_transition_entry(self):
        """Every TaskStatus must have an entry in TASK_TRANSITIONS."""
        for state in TaskStatus:
            assert state in TASK_TRANSITIONS, f"{state} missing from TASK_TRANSITIONS"

    def test_terminal_states_have_no_transitions(self):
        """COMPLETED and CANCELLED are terminal — no outgoing transitions."""
        assert len(TASK_TRANSITIONS[TaskStatus.COMPLETED]) == 0
        assert len(TASK_TRANSITIONS[TaskStatus.CANCELLED]) == 0

    def test_available_can_be_announced(self):
        """AVAILABLE -> ANNOUNCED must be allowed."""
        assert TaskStatus.ANNOUNCED in TASK_TRANSITIONS[TaskStatus.AVAILABLE]

    def test_in_progress_can_complete_or_fail(self):
        """IN_PROGRESS -> COMPLETED and IN_PROGRESS -> FAILED must be allowed."""
        transitions = TASK_TRANSITIONS[TaskStatus.IN_PROGRESS]
        assert TaskStatus.COMPLETED in transitions
        assert TaskStatus.FAILED in transitions

    def test_failed_can_enter_recovery(self):
        """FAILED -> RECOVERY must be allowed."""
        assert TaskStatus.RECOVERY in TASK_TRANSITIONS[TaskStatus.FAILED]

    def test_recovery_can_be_re_announced(self):
        """RECOVERY -> ANNOUNCED must be allowed (task re-announced after recovery)."""
        assert TaskStatus.ANNOUNCED in TASK_TRANSITIONS[TaskStatus.RECOVERY]


# ---------------------------------------------------------------------------
# Task dataclass construction
# ---------------------------------------------------------------------------

class TestTaskCreation:
    def test_t01_fields(self, task_t01: Task):
        """Task T01 is constructed with the expected field values."""
        assert task_t01.task_id == "T01"
        assert task_t01.pickup_location == (10.0, 4.0)
        assert task_t01.dropoff_location == (18.0, 9.0)
        assert task_t01.priority == 7
        assert task_t01.deadline == 60.0
        assert task_t01.required_payload == 100.0
        assert task_t01.status == TaskStatus.AVAILABLE
        assert task_t01.assigned_robot is None
        assert "CARRY" in task_t01.required_capabilities

    def test_t02_assigned(self, task_t02: Task):
        """Task T02 is IN_PROGRESS and assigned to Robot C."""
        assert task_t02.status == TaskStatus.IN_PROGRESS
        assert task_t02.assigned_robot == "C"

    def test_capabilities_is_tuple(self, task_t01: Task):
        """required_capabilities must be a tuple (immutable)."""
        assert isinstance(task_t01.required_capabilities, tuple)


# ---------------------------------------------------------------------------
# Task helper methods
# ---------------------------------------------------------------------------

class TestTaskHelpers:
    def test_transport_distance_t01(self, task_t01: Task):
        """T01: pickup(10,4) -> dropoff(18,9) = sqrt(64+25) = sqrt(89) ≈ 9.434."""
        expected = (8.0 ** 2 + 5.0 ** 2) ** 0.5
        assert task_t01.transport_distance() == pytest.approx(expected)

    def test_is_terminal_available(self, task_t01: Task):
        """An AVAILABLE task is not terminal."""
        assert task_t01.is_terminal() is False

    def test_is_terminal_completed(self, task_t01: Task):
        """A COMPLETED task is terminal."""
        import dataclasses
        completed = dataclasses.replace(task_t01, status=TaskStatus.COMPLETED)
        assert completed.is_terminal() is True

    def test_is_terminal_cancelled(self, task_t01: Task):
        """A CANCELLED task is terminal."""
        import dataclasses
        cancelled = dataclasses.replace(task_t01, status=TaskStatus.CANCELLED)
        assert cancelled.is_terminal() is True

    def test_needs_recovery_failed(self, task_t01: Task):
        """A FAILED task needs recovery."""
        import dataclasses
        failed = dataclasses.replace(task_t01, status=TaskStatus.FAILED)
        assert failed.needs_recovery() is True

    def test_needs_recovery_available(self, task_t01: Task):
        """An AVAILABLE task does not need recovery."""
        assert task_t01.needs_recovery() is False

    def test_allowed_transitions_available(self, task_t01: Task):
        """Task T01 (AVAILABLE) has ANNOUNCED and CANCELLED as allowed transitions."""
        allowed = task_t01.allowed_transitions()
        assert TaskStatus.ANNOUNCED in allowed
        assert TaskStatus.CANCELLED in allowed

    def test_str_contains_task_id(self, task_t01: Task):
        """__str__ includes task_id."""
        assert "T01" in str(task_t01)

    def test_str_contains_status(self, task_t01: Task):
        """__str__ includes the status value."""
        assert "AVAILABLE" in str(task_t01)
