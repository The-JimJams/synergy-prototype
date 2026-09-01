"""
Tests for dashboard.data_store — Phase 2 verification.

Covers:
- Robot state CRUD + staleness detection
- Intent update / clear
- Reservation update / release
- Task CRUD
- Event history (add, filter, bounded size, clear)
- Network status
- Metrics (live + archived experiment runs)
- Full reset
- Summary / health
"""

import sys, os, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_store import DataStore
from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Task,
    Event,
    NetworkStatus,
    ExperimentMetrics,
)


def _make_store(**kwargs) -> DataStore:
    """Convenience factory with small defaults for testing."""
    defaults = {"max_events": 10, "max_experiment_runs": 5}
    defaults.update(kwargs)
    return DataStore(**defaults)


# ── Robot State ─────────────────────────────────────────────────────────────

class TestRobotState:
    def test_update_and_get(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A", x=1.0, y=2.0))
        result = store.get_robot_state("A")
        assert result is not None
        assert result["robot_id"] == "A"
        assert result["x"] == 1.0

    def test_get_unknown_robot(self):
        store = _make_store()
        assert store.get_robot_state("Z") is None

    def test_latest_wins(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A", x=1.0))
        store.update_robot(RobotState(robot_id="A", x=5.0))
        result = store.get_robot_state("A")
        assert result["x"] == 5.0

    def test_multiple_robots(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A"))
        store.update_robot(RobotState(robot_id="B"))
        store.update_robot(RobotState(robot_id="C"))
        all_robots = store.get_all_robots()
        assert set(all_robots.keys()) == {"A", "B", "C"}

    def test_staleness_flag(self):
        store = _make_store()
        # Use a timestamp far in the past to trigger staleness
        store.update_robot(
            RobotState(robot_id="A", timestamp="2020-01-01T00:00:00+00:00")
        )
        result = store.get_robot_state("A", stale_threshold_s=5.0)
        assert result["_stale"] is True

    def test_fresh_not_stale(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A"))  # timestamp = now
        result = store.get_robot_state("A", stale_threshold_s=60.0)
        assert result["_stale"] is False


# ── Intents ─────────────────────────────────────────────────────────────────

class TestIntents:
    def test_update_and_get(self):
        store = _make_store()
        store.update_intent(RobotIntent(robot_id="A", resource_id="I1", eta=2.5))
        intents = store.get_intents()
        assert len(intents) == 1
        assert intents[0]["resource_id"] == "I1"
        assert intents[0]["eta"] == 2.5

    def test_clear_intent(self):
        store = _make_store()
        store.update_intent(RobotIntent(robot_id="A", resource_id="I1"))
        store.clear_intent("A")
        assert store.get_intents() == []

    def test_clear_nonexistent_is_safe(self):
        store = _make_store()
        store.clear_intent("Z")  # should not raise
        assert store.get_intents() == []

    def test_latest_intent_wins(self):
        store = _make_store()
        store.update_intent(RobotIntent(robot_id="A", resource_id="I1"))
        store.update_intent(RobotIntent(robot_id="A", resource_id="I2"))
        intents = store.get_intents()
        assert len(intents) == 1
        assert intents[0]["resource_id"] == "I2"


# ── Reservations ────────────────────────────────────────────────────────────

class TestReservations:
    def test_update_and_get(self):
        store = _make_store()
        store.update_reservation(
            Reservation(resource_id="I1", robot_id="A", status="ACTIVE")
        )
        res = store.get_reservations()
        assert len(res) == 1
        assert res[0]["status"] == "ACTIVE"
        assert res[0]["robot_id"] == "A"

    def test_release_reservation(self):
        store = _make_store()
        store.update_reservation(
            Reservation(resource_id="I1", robot_id="A", status="ACTIVE")
        )
        store.release_reservation("I1")
        res = store.get_reservations()
        assert len(res) == 1
        assert res[0]["status"] == "FREE"
        assert res[0]["robot_id"] is None

    def test_release_unknown_creates_free(self):
        store = _make_store()
        store.release_reservation("I99")
        res = store.get_reservations()
        assert len(res) == 1
        assert res[0]["resource_id"] == "I99"
        assert res[0]["status"] == "FREE"

    def test_multiple_resources(self):
        store = _make_store()
        store.update_reservation(
            Reservation(resource_id="I1", robot_id="A", status="ACTIVE")
        )
        store.update_reservation(
            Reservation(resource_id="I2", robot_id=None, status="FREE")
        )
        res = store.get_reservations()
        assert len(res) == 2


# ── Tasks ───────────────────────────────────────────────────────────────────

class TestTasks:
    def test_update_and_get_all(self):
        store = _make_store()
        store.update_task(Task(task_id="T01", pickup="S1", dropoff="S2",
                               assigned_robot="A", status="IN_PROGRESS"))
        tasks = store.get_tasks()
        assert len(tasks) == 1
        assert tasks[0]["task_id"] == "T01"
        assert tasks[0]["assigned_robot"] == "A"

    def test_get_single_task(self):
        store = _make_store()
        store.update_task(Task(task_id="T01"))
        assert store.get_task("T01") is not None
        assert store.get_task("T99") is None

    def test_task_status_update(self):
        store = _make_store()
        store.update_task(Task(task_id="T01", status="ASSIGNED"))
        store.update_task(Task(task_id="T01", status="COMPLETED",
                               completed_at="2026-01-01T00:05:00+00:00"))
        task = store.get_task("T01")
        assert task["status"] == "COMPLETED"
        assert task["completed_at"] is not None


# ── Events ──────────────────────────────────────────────────────────────────

class TestEvents:
    def test_add_and_get(self):
        store = _make_store()
        store.add_event(Event(event_type="CONFLICT", robot_id="A",
                              message="test conflict"))
        events = store.get_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "CONFLICT"

    def test_newest_first(self):
        store = _make_store()
        store.add_event(Event(event_type="FIRST", message="first"))
        store.add_event(Event(event_type="SECOND", message="second"))
        events = store.get_events()
        assert events[0]["event_type"] == "SECOND"
        assert events[1]["event_type"] == "FIRST"

    def test_limit(self):
        store = _make_store()
        for i in range(10):
            store.add_event(Event(event_type="INFO", message=f"evt-{i}"))
        events = store.get_events(limit=3)
        assert len(events) == 3

    def test_bounded_history(self):
        """Events beyond max_events are discarded (oldest first)."""
        store = _make_store(max_events=5)
        for i in range(10):
            store.add_event(Event(event_type="INFO", message=f"evt-{i}"))
        # Only 5 most recent should survive
        events = store.get_events(limit=100)
        assert len(events) == 5
        # Newest event should be evt-9
        assert events[0]["message"] == "evt-9"

    def test_filter_by_event_type(self):
        store = _make_store()
        store.add_event(Event(event_type="CONFLICT", message="c"))
        store.add_event(Event(event_type="FAILURE", message="f"))
        store.add_event(Event(event_type="CONFLICT", message="c2"))
        events = store.get_events(event_type="CONFLICT")
        assert len(events) == 2
        assert all(e["event_type"] == "CONFLICT" for e in events)

    def test_filter_by_robot_id(self):
        store = _make_store()
        store.add_event(Event(event_type="INFO", robot_id="A", message="a"))
        store.add_event(Event(event_type="INFO", robot_id="B", message="b"))
        store.add_event(Event(event_type="CONFLICT", robot_id="A",
                              related_robot_id="B", message="ab"))
        # Filter for robot B — should match event where B is primary OR related
        events = store.get_events(robot_id="B")
        assert len(events) == 2

    def test_clear_events(self):
        store = _make_store()
        store.add_event(Event(event_type="INFO", message="x"))
        store.clear_events()
        assert store.get_events() == []


# ── Network ─────────────────────────────────────────────────────────────────

class TestNetwork:
    def test_default(self):
        store = _make_store()
        net = store.get_network()
        assert net["status"] == "NORMAL"

    def test_update(self):
        store = _make_store()
        store.update_network(NetworkStatus(status="DEGRADED", latency_ms=120.0))
        net = store.get_network()
        assert net["status"] == "DEGRADED"
        assert net["latency_ms"] == 120.0


# ── Metrics / Experiments ───────────────────────────────────────────────────

class TestMetrics:
    def test_no_metrics_initially(self):
        store = _make_store()
        assert store.get_metrics() is None

    def test_update_live_metrics(self):
        store = _make_store()
        store.update_metrics(ExperimentMetrics(
            mode="proposed", total_task_time=78.4, tasks_completed=3
        ))
        m = store.get_metrics()
        assert m["mode"] == "proposed"
        assert m["total_task_time"] == 78.4

    def test_experiment_runs(self):
        store = _make_store()
        store.add_experiment_run(ExperimentMetrics(
            mode="baseline", total_task_time=100.0
        ))
        store.add_experiment_run(ExperimentMetrics(
            mode="proposed", total_task_time=78.0
        ))
        runs = store.get_experiment_runs()
        assert len(runs) == 2
        assert runs[0]["mode"] == "baseline"
        assert runs[1]["mode"] == "proposed"

    def test_experiment_runs_bounded(self):
        store = _make_store(max_experiment_runs=3)
        for i in range(6):
            store.add_experiment_run(
                ExperimentMetrics(mode="baseline", total_task_time=float(i))
            )
        runs = store.get_experiment_runs()
        assert len(runs) == 3
        # Oldest should be run with total_task_time=3.0
        assert runs[0]["total_task_time"] == 3.0


# ── Housekeeping ────────────────────────────────────────────────────────────

class TestHousekeeping:
    def test_reset(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A"))
        store.add_event(Event(event_type="INFO"))
        store.update_task(Task(task_id="T01"))
        store.update_intent(RobotIntent(robot_id="A", resource_id="I1"))
        store.update_reservation(Reservation(resource_id="I1", robot_id="A"))
        store.update_metrics(ExperimentMetrics())

        store.reset()

        assert store.get_all_robots() == {}
        assert store.get_intents() == []
        assert store.get_reservations() == []
        assert store.get_tasks() == []
        assert store.get_events() == []
        assert store.get_metrics() is None

    def test_summary(self):
        store = _make_store()
        store.update_robot(RobotState(robot_id="A"))
        store.update_robot(RobotState(robot_id="B"))
        store.update_reservation(
            Reservation(resource_id="I1", robot_id="A", status="ACTIVE")
        )
        store.update_reservation(
            Reservation(resource_id="I2", status="FREE")
        )
        store.add_event(Event(event_type="CONFLICT"))

        summary = store.get_summary()
        assert summary["status"] == "ok"
        assert summary["robots_tracked"] == 2
        assert summary["active_reservations"] == 1
        assert summary["total_reservations_tracked"] == 2
        assert summary["events_stored"] == 1
        assert summary["max_events"] == 10
