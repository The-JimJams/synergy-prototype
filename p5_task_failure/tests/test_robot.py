"""
P5 Unit Tests — Robot Model
============================

Tests that the Robot dataclass and RobotStatus enum behave correctly.

No ROS 2, Gazebo, Nav2, or other external dependency is required.
All test data comes from conftest.py fixtures (deterministic).
"""

from __future__ import annotations

import pytest
from p5.models.robot import Robot, RobotStatus


# ---------------------------------------------------------------------------
# RobotStatus enum
# ---------------------------------------------------------------------------

class TestRobotStatus:
    def test_all_expected_values_exist(self):
        """All required status values must be defined."""
        expected = {"AVAILABLE", "BUSY", "CHARGING", "OFFLINE", "FAILED", "RECOVERED"}
        actual = {s.value for s in RobotStatus}
        assert expected == actual, f"Missing: {expected - actual}"

    def test_status_is_string_valued(self):
        """Each enum value must be a plain string."""
        for status in RobotStatus:
            assert isinstance(status.value, str)

    def test_status_by_value(self):
        """Enum can be looked up by value string."""
        assert RobotStatus("AVAILABLE") is RobotStatus.AVAILABLE
        assert RobotStatus("FAILED") is RobotStatus.FAILED


# ---------------------------------------------------------------------------
# Robot dataclass construction
# ---------------------------------------------------------------------------

class TestRobotCreation:
    def test_robot_a_fields(self, robot_a: Robot):
        """Robot A is constructed with the expected field values."""
        assert robot_a.robot_id == "A"
        assert robot_a.position == (2.0, 2.0)
        assert robot_a.battery == 90.0
        assert robot_a.payload_capacity == 500.0
        assert robot_a.current_task is None
        assert robot_a.workload == 0
        assert robot_a.status == RobotStatus.AVAILABLE
        assert "CARRY" in robot_a.capabilities
        assert "LIFT" in robot_a.capabilities

    def test_robot_b_fields(self, robot_b: Robot):
        """Robot B is constructed with the expected field values."""
        assert robot_b.robot_id == "B"
        assert robot_b.position == (8.0, 3.0)
        assert robot_b.battery == 65.0
        assert robot_b.status == RobotStatus.AVAILABLE

    def test_robot_c_busy(self, robot_c: Robot):
        """Robot C is BUSY with task T02."""
        assert robot_c.status == RobotStatus.BUSY
        assert robot_c.current_task == "T02"
        assert robot_c.workload == 1

    def test_capabilities_is_tuple(self, robot_a: Robot):
        """Capabilities must be stored as a tuple (immutable)."""
        assert isinstance(robot_a.capabilities, tuple)


# ---------------------------------------------------------------------------
# Robot helper methods
# ---------------------------------------------------------------------------

class TestRobotHelpers:
    def test_is_available_true(self, robot_a: Robot):
        """An AVAILABLE robot with no current task reports is_available()."""
        assert robot_a.is_available() is True

    def test_is_available_false_busy(self, robot_c: Robot):
        """A BUSY robot does not report is_available()."""
        assert robot_c.is_available() is False

    def test_distance_to_same_position(self, robot_a: Robot):
        """Distance from a robot to its own position is zero."""
        assert robot_a.distance_to(robot_a.position) == pytest.approx(0.0)

    def test_distance_to_known_target(self, robot_a: Robot):
        """Robot A at (2,2) to (5,6) = sqrt(9+16) = 5.0."""
        assert robot_a.distance_to((5.0, 6.0)) == pytest.approx(5.0)

    def test_has_capability_true(self, robot_a: Robot):
        """Robot A has the CARRY capability."""
        assert robot_a.has_capability("CARRY") is True

    def test_has_capability_false(self, robot_a: Robot):
        """Robot A does not have the HAZMAT capability."""
        assert robot_a.has_capability("HAZMAT") is False

    def test_can_carry_within_limit(self, robot_a: Robot):
        """Robot A (capacity 500) can carry payload 100."""
        assert robot_a.can_carry(100.0) is True

    def test_can_carry_at_limit(self, robot_a: Robot):
        """Robot A (capacity 500) can carry payload 500."""
        assert robot_a.can_carry(500.0) is True

    def test_can_carry_over_limit(self, robot_a: Robot):
        """Robot A (capacity 500) cannot carry payload 501."""
        assert robot_a.can_carry(501.0) is False

    def test_str_contains_robot_id(self, robot_a: Robot):
        """__str__ includes robot_id."""
        assert "A" in str(robot_a)

    def test_str_contains_status(self, robot_a: Robot):
        """__str__ includes status value."""
        assert "AVAILABLE" in str(robot_a)
