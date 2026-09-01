"""
Unit tests for the data models.

These tests verify that dataclasses construct correctly, helper methods
work, and edge cases are handled. No algorithm logic is tested here —
only the data vocabulary.
"""

import math

from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.task import Task, TaskType, TaskStatus
from fleet_coordination.models.conflict import ConflictReport, ConflictSeverity
from fleet_coordination.tests.conftest import FIXED_TIME


# ===========================================================================
# Pose2D
# ===========================================================================

class TestPose2D:
    """Tests for Pose2D dataclass."""

    def test_construction_default_theta(self):
        """Theta defaults to 0.0 if not specified."""
        p = Pose2D(x=1.0, y=2.0)
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.theta == 0.0

    def test_construction_with_theta(self):
        p = Pose2D(x=1.0, y=2.0, theta=1.57)
        assert p.theta == 1.57

    def test_frozen_immutability(self):
        """Pose2D is frozen — cannot modify after creation."""
        p = Pose2D(x=1.0, y=2.0)
        try:
            p.x = 5.0
            assert False, "Should have raised FrozenInstanceError"
        except AttributeError:
            pass  # Expected

    def test_distance_to_origin(self):
        """Classic 3-4-5 right triangle."""
        origin = Pose2D(0.0, 0.0)
        point = Pose2D(3.0, 4.0)
        assert math.isclose(origin.distance_to(point), 5.0)

    def test_distance_to_self(self):
        p = Pose2D(3.0, 4.0)
        assert p.distance_to(p) == 0.0

    def test_distance_is_symmetric(self):
        a = Pose2D(1.0, 2.0)
        b = Pose2D(4.0, 6.0)
        assert math.isclose(a.distance_to(b), b.distance_to(a))

    def test_distance_ignores_theta(self):
        """Orientation should not affect Euclidean distance."""
        a = Pose2D(0.0, 0.0, theta=0.0)
        b = Pose2D(0.0, 0.0, theta=3.14)
        assert a.distance_to(b) == 0.0

    def test_equality(self):
        """Two Pose2D with same values should be equal (frozen dataclass)."""
        a = Pose2D(1.0, 2.0, 0.5)
        b = Pose2D(1.0, 2.0, 0.5)
        assert a == b

    def test_repr_readable(self):
        p = Pose2D(1.0, 2.0, 1.57)
        r = repr(p)
        assert "Pose2D" in r
        assert "1.00" in r


# ===========================================================================
# RobotState
# ===========================================================================

class TestRobotState:
    """Tests for RobotState dataclass."""

    def test_construction_minimal(self):
        """Construct with only robot_id — everything else has defaults."""
        s = RobotState(robot_id="amr_01")
        assert s.robot_id == "amr_01"
        assert s.status == RobotStatus.IDLE
        assert s.battery_percent == 100.0
        assert s.current_task_id is None

    def test_age_with_fixed_time(self):
        """Age calculation using explicit 'now' for determinism."""
        s = RobotState(robot_id="amr_01", timestamp=100.0)
        assert s.age(now=105.0) == 5.0

    def test_age_zero_when_current(self):
        s = RobotState(robot_id="amr_01", timestamp=100.0)
        assert s.age(now=100.0) == 0.0

    def test_is_available_when_idle(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.IDLE)
        assert s.is_available() is True

    def test_is_available_when_waiting(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.WAITING)
        assert s.is_available() is True

    def test_not_available_when_navigating(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.NAVIGATING)
        assert s.is_available() is False

    def test_not_available_when_failed(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.FAILED)
        assert s.is_available() is False

    def test_not_available_when_charging(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.CHARGING)
        assert s.is_available() is False

    def test_not_available_when_emergency_stop(self):
        s = RobotState(robot_id="amr_01", status=RobotStatus.EMERGENCY_STOP)
        assert s.is_available() is False

    def test_all_robot_statuses_exist(self):
        """Verify all expected statuses are defined."""
        expected = {"IDLE", "NAVIGATING", "WAITING", "CHARGING", "FAILED", "EMERGENCY_STOP"}
        actual = {s.name for s in RobotStatus}
        assert actual == expected


# ===========================================================================
# RobotIntent
# ===========================================================================

class TestRobotIntent:
    """Tests for RobotIntent dataclass."""

    def test_construction_minimal(self):
        i = RobotIntent(robot_id="amr_01")
        assert i.robot_id == "amr_01"
        assert i.target_resource_id is None
        assert i.planned_waypoints == []

    def test_is_expired_when_past_valid_until(self):
        i = RobotIntent(
            robot_id="amr_01",
            valid_until=100.0,
        )
        assert i.is_expired(now=101.0) is True

    def test_not_expired_when_before_valid_until(self):
        i = RobotIntent(
            robot_id="amr_01",
            valid_until=100.0,
        )
        assert i.is_expired(now=99.0) is False

    def test_expired_exactly_at_valid_until(self):
        """At exactly valid_until, now > valid_until is False, so NOT expired."""
        i = RobotIntent(
            robot_id="amr_01",
            valid_until=100.0,
        )
        assert i.is_expired(now=100.0) is False

    def test_age_calculation(self):
        i = RobotIntent(robot_id="amr_01", timestamp=100.0)
        assert i.age(now=115.0) == 15.0

    def test_default_waypoints_empty_list(self):
        """planned_waypoints defaults to empty list, not shared mutable."""
        a = RobotIntent(robot_id="amr_01")
        b = RobotIntent(robot_id="amr_02")
        assert a.planned_waypoints == []
        assert a.planned_waypoints is not b.planned_waypoints  # Not shared!

    def test_zero_valid_until_is_immediately_expired(self):
        """Default valid_until=0.0 means intent is expired unless now <= 0."""
        i = RobotIntent(robot_id="amr_01")  # valid_until=0.0
        assert i.is_expired(now=1.0) is True


# ===========================================================================
# Reservation
# ===========================================================================

class TestReservation:
    """Tests for Reservation dataclass."""

    def test_construction(self):
        r = Reservation(
            resource_id="I1",
            robot_id="amr_01",
            start_time=100.0,
            end_time=130.0,
            priority=5.0,
            expires_at=200.0,
        )
        assert r.resource_id == "I1"
        assert r.robot_id == "amr_01"

    def test_claim_id_auto_generated(self):
        """Each reservation gets a unique claim_id."""
        a = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=0, end_time=10, priority=1, expires_at=20)
        b = Reservation(resource_id="I1", robot_id="amr_02",
                        start_time=0, end_time=10, priority=1, expires_at=20)
        assert a.claim_id != b.claim_id

    def test_is_expired(self):
        r = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=150)
        assert r.is_expired(now=151.0) is True
        assert r.is_expired(now=149.0) is False

    def test_is_active_within_window(self):
        r = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=200)
        assert r.is_active(now=115.0) is True

    def test_not_active_before_start(self):
        r = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=200)
        assert r.is_active(now=99.0) is False

    def test_not_active_after_end(self):
        r = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=200)
        assert r.is_active(now=131.0) is False

    def test_not_active_when_expired(self):
        """Even if within [start, end], expired reservations are not active."""
        r = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=110)
        assert r.is_active(now=115.0) is False  # expired_at=110 < now=115

    def test_overlaps_temporally_true(self):
        a = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=130, priority=5, expires_at=200)
        b = Reservation(resource_id="I1", robot_id="amr_02",
                        start_time=120, end_time=150, priority=3, expires_at=200)
        assert a.overlaps_temporally(b) is True
        assert b.overlaps_temporally(a) is True  # symmetric

    def test_overlaps_temporally_false_sequential(self):
        """A ends exactly when B starts — no overlap (open interval)."""
        a = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=120, priority=5, expires_at=200)
        b = Reservation(resource_id="I1", robot_id="amr_02",
                        start_time=120, end_time=150, priority=3, expires_at=200)
        assert a.overlaps_temporally(b) is False

    def test_overlaps_temporally_false_disjoint(self):
        a = Reservation(resource_id="I1", robot_id="amr_01",
                        start_time=100, end_time=110, priority=5, expires_at=200)
        b = Reservation(resource_id="I1", robot_id="amr_02",
                        start_time=200, end_time=210, priority=3, expires_at=300)
        assert a.overlaps_temporally(b) is False


# ===========================================================================
# Task
# ===========================================================================

class TestTask:
    """Tests for Task dataclass."""

    def test_construction(self):
        t = Task(task_id="task_001")
        assert t.task_id == "task_001"
        assert t.task_type == TaskType.PICKUP_AND_DELIVERY
        assert t.priority == 5
        assert t.status == TaskStatus.ANNOUNCED

    def test_is_assignable_announced(self):
        t = Task(task_id="t1", status=TaskStatus.ANNOUNCED)
        assert t.is_assignable() is True

    def test_is_assignable_bidding(self):
        t = Task(task_id="t1", status=TaskStatus.BIDDING)
        assert t.is_assignable() is True

    def test_is_assignable_failed(self):
        """Failed tasks can be reassigned."""
        t = Task(task_id="t1", status=TaskStatus.FAILED)
        assert t.is_assignable() is True

    def test_not_assignable_in_progress(self):
        t = Task(task_id="t1", status=TaskStatus.IN_PROGRESS)
        assert t.is_assignable() is False

    def test_not_assignable_completed(self):
        t = Task(task_id="t1", status=TaskStatus.COMPLETED)
        assert t.is_assignable() is False

    def test_deadline_urgency_no_deadline(self):
        t = Task(task_id="t1", deadline=None)
        assert t.deadline_urgency(now=FIXED_TIME) == 0.0

    def test_deadline_urgency_far_deadline(self):
        """300 seconds remaining — low urgency."""
        t = Task(task_id="t1", deadline=FIXED_TIME + 300.0)
        urgency = t.deadline_urgency(now=FIXED_TIME)
        assert 0.0 < urgency < 0.01  # Very small

    def test_deadline_urgency_tight_deadline(self):
        """5 seconds remaining — higher urgency."""
        t = Task(task_id="t1", deadline=FIXED_TIME + 5.0)
        urgency = t.deadline_urgency(now=FIXED_TIME)
        assert urgency == 1.0 / 5.0  # = 0.2

    def test_deadline_urgency_past_deadline(self):
        """Past deadline — maximum urgency (1.0)."""
        t = Task(task_id="t1", deadline=FIXED_TIME - 10.0)
        urgency = t.deadline_urgency(now=FIXED_TIME)
        assert urgency == 1.0

    def test_all_task_types_exist(self):
        expected = {"PICKUP", "DELIVERY", "PICKUP_AND_DELIVERY", "CHARGING", "INSPECTION"}
        actual = {t.name for t in TaskType}
        assert actual == expected

    def test_all_task_statuses_exist(self):
        expected = {"ANNOUNCED", "BIDDING", "ASSIGNED", "IN_PROGRESS",
                    "COMPLETED", "FAILED", "REASSIGNED"}
        actual = {s.name for s in TaskStatus}
        assert actual == expected


# ===========================================================================
# ConflictReport
# ===========================================================================

class TestConflictReport:
    """Tests for ConflictReport dataclass."""

    def test_construction(self):
        c = ConflictReport(
            robot_a_id="amr_01",
            robot_b_id="amr_02",
            resource_id="I1",
            overlap_start=100.0,
            overlap_end=110.0,
            severity=ConflictSeverity.HIGH,
        )
        assert c.robot_a_id == "amr_01"
        assert c.resource_id == "I1"

    def test_overlap_duration(self):
        c = ConflictReport(
            robot_a_id="amr_01", robot_b_id="amr_02",
            resource_id="I1",
            overlap_start=100.0, overlap_end=115.0,
        )
        assert c.overlap_duration() == 15.0

    def test_overlap_duration_zero_when_equal(self):
        c = ConflictReport(
            robot_a_id="amr_01", robot_b_id="amr_02",
            resource_id="I1",
            overlap_start=100.0, overlap_end=100.0,
        )
        assert c.overlap_duration() == 0.0

    def test_involves_robot_true(self):
        c = ConflictReport(
            robot_a_id="amr_01", robot_b_id="amr_02",
            resource_id="I1",
            overlap_start=100.0, overlap_end=110.0,
        )
        assert c.involves_robot("amr_01") is True
        assert c.involves_robot("amr_02") is True

    def test_involves_robot_false(self):
        c = ConflictReport(
            robot_a_id="amr_01", robot_b_id="amr_02",
            resource_id="I1",
            overlap_start=100.0, overlap_end=110.0,
        )
        assert c.involves_robot("amr_03") is False

    def test_unique_conflict_ids(self):
        a = ConflictReport(robot_a_id="amr_01", robot_b_id="amr_02",
                           resource_id="I1", overlap_start=100, overlap_end=110)
        b = ConflictReport(robot_a_id="amr_01", robot_b_id="amr_02",
                           resource_id="I1", overlap_start=100, overlap_end=110)
        assert a.conflict_id != b.conflict_id

    def test_all_severity_levels_exist(self):
        expected = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        actual = {s.name for s in ConflictSeverity}
        assert actual == expected
