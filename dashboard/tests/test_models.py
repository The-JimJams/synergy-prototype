"""
Tests for dashboard.models — Phase 1 verification.

These tests confirm that every normalized data model:
- can be instantiated with defaults
- can be instantiated with full kwargs
- round-trips through to_dict() → from_dict() without data loss
- handles missing / optional fields gracefully
"""

import sys, os

# Ensure the dashboard package is importable regardless of working directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Task,
    Event,
    NetworkStatus,
    ExperimentMetrics,
)


# ── RobotState ──────────────────────────────────────────────────────────────

class TestRobotState:
    def test_defaults(self):
        rs = RobotState(robot_id="A")
        assert rs.robot_id == "A"
        assert rs.x == 0.0
        assert rs.y == 0.0
        assert rs.yaw == 0.0
        assert rs.velocity == 0.0
        assert rs.battery == 100.0
        assert rs.status == "IDLE"
        assert rs.task_id is None
        assert rs.timestamp  # not empty

    def test_full_kwargs(self):
        rs = RobotState(
            robot_id="B", x=3.5, y=7.2, yaw=1.57, velocity=0.8,
            battery=65.0, status="MOVING", task_id="T02",
            timestamp="2026-01-01T00:00:00+00:00",
        )
        assert rs.x == 3.5
        assert rs.status == "MOVING"
        assert rs.task_id == "T02"

    def test_round_trip(self):
        original = RobotState(robot_id="C", x=1.0, y=2.0, status="WAITING")
        d = original.to_dict()
        restored = RobotState.from_dict(d)
        assert restored.robot_id == original.robot_id
        assert restored.x == original.x
        assert restored.status == original.status

    def test_from_dict_missing_fields(self):
        """from_dict should fill sensible defaults for missing keys."""
        rs = RobotState.from_dict({"robot_id": "X"})
        assert rs.robot_id == "X"
        assert rs.battery == 100.0
        assert rs.status == "UNKNOWN"

    def test_from_dict_completely_empty(self):
        rs = RobotState.from_dict({})
        assert rs.robot_id == "UNKNOWN"


# ── RobotIntent ─────────────────────────────────────────────────────────────

class TestRobotIntent:
    def test_defaults(self):
        ri = RobotIntent(robot_id="A", resource_id="I1")
        assert ri.robot_id == "A"
        assert ri.resource_id == "I1"
        assert ri.eta is None

    def test_with_eta(self):
        ri = RobotIntent(robot_id="B", resource_id="I2", eta=3.5)
        assert ri.eta == 3.5

    def test_round_trip(self):
        original = RobotIntent(robot_id="C", resource_id="I3", eta=1.2)
        restored = RobotIntent.from_dict(original.to_dict())
        assert restored.resource_id == "I3"
        assert restored.eta == 1.2


# ── Reservation ─────────────────────────────────────────────────────────────

class TestReservation:
    def test_free_by_default(self):
        r = Reservation(resource_id="I1")
        assert r.status == "FREE"
        assert r.robot_id is None

    def test_active_reservation(self):
        r = Reservation(resource_id="I1", robot_id="A", status="ACTIVE")
        assert r.robot_id == "A"
        assert r.status == "ACTIVE"

    def test_round_trip(self):
        original = Reservation(resource_id="I2", robot_id="B", status="ACTIVE",
                               start_time="2026-01-01T00:00:00+00:00")
        restored = Reservation.from_dict(original.to_dict())
        assert restored.resource_id == "I2"
        assert restored.start_time == "2026-01-01T00:00:00+00:00"


# ── Task ────────────────────────────────────────────────────────────────────

class TestTask:
    def test_defaults(self):
        t = Task(task_id="T01")
        assert t.task_id == "T01"
        assert t.status == "ANNOUNCED"
        assert t.assigned_robot is None
        assert t.completed_at is None

    def test_completed_task(self):
        t = Task(task_id="T02", pickup="Station1", dropoff="Station2",
                 assigned_robot="A", status="COMPLETED",
                 completed_at="2026-01-01T00:05:00+00:00")
        assert t.status == "COMPLETED"
        assert t.completed_at is not None

    def test_round_trip(self):
        original = Task(task_id="T03", pickup="P", dropoff="D",
                        assigned_robot="C", status="IN_PROGRESS")
        restored = Task.from_dict(original.to_dict())
        assert restored.task_id == "T03"
        assert restored.assigned_robot == "C"


# ── Event ───────────────────────────────────────────────────────────────────

class TestEvent:
    def test_defaults(self):
        e = Event()
        assert e.event_type == "INFO"
        assert e.robot_id is None
        assert e.message == ""

    def test_conflict_event(self):
        e = Event(
            event_type="CONFLICT",
            robot_id="A",
            related_robot_id="B",
            resource_id="I1",
            message="Conflict detected at I1",
        )
        assert e.event_type == "CONFLICT"
        assert e.related_robot_id == "B"

    def test_round_trip(self):
        original = Event(event_type="FAILURE", robot_id="A",
                         message="Heartbeat timeout")
        restored = Event.from_dict(original.to_dict())
        assert restored.event_type == "FAILURE"
        assert restored.message == "Heartbeat timeout"


# ── NetworkStatus ───────────────────────────────────────────────────────────

class TestNetworkStatus:
    def test_defaults(self):
        ns = NetworkStatus()
        assert ns.status == "NORMAL"
        assert ns.latency_ms is None

    def test_degraded(self):
        ns = NetworkStatus(status="DEGRADED", latency_ms=120.0,
                           packet_loss_percent=5.0, active_peers=2)
        assert ns.status == "DEGRADED"
        assert ns.active_peers == 2

    def test_round_trip(self):
        original = NetworkStatus(status="DISCONNECTED", latency_ms=999.0)
        restored = NetworkStatus.from_dict(original.to_dict())
        assert restored.status == "DISCONNECTED"


# ── ExperimentMetrics ───────────────────────────────────────────────────────

class TestExperimentMetrics:
    def test_defaults(self):
        m = ExperimentMetrics()
        assert m.mode == "proposed"
        assert m.total_task_time == 0.0
        assert m.collision_count == 0
        assert m.run_id  # auto-generated, non-empty

    def test_baseline_run(self):
        m = ExperimentMetrics(
            mode="baseline",
            total_task_time=100.2,
            average_wait_time=15.1,
            tasks_completed=3,
            collision_count=0,
            scenario="conflict",
        )
        assert m.mode == "baseline"
        assert m.total_task_time == 100.2

    def test_round_trip(self):
        original = ExperimentMetrics(
            mode="proposed", total_task_time=78.4,
            average_wait_time=7.2, tasks_completed=3,
        )
        restored = ExperimentMetrics.from_dict(original.to_dict())
        assert restored.total_task_time == 78.4
        assert restored.tasks_completed == 3

    def test_from_dict_missing_fields(self):
        m = ExperimentMetrics.from_dict({})
        assert m.mode == "proposed"
        assert m.total_task_time == 0.0
