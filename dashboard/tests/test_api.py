"""
Tests for dashboard.app — Phase 4 verification.

Covers:
- All GET endpoints return JSON (200 OK)
- Response structures match API data contract
- Query param filtering for /api/events
- Safety check: control endpoints (stop_robot, assign_task) return 404
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from data_store import DataStore
from models import RobotState, Event, Task, Reservation, RobotIntent


@pytest.fixture
def client():
    store = DataStore()

    # Pre-populate store with known data
    store.update_robot(RobotState(robot_id="A", x=1.0, y=2.0, status="MOVING"))
    store.update_robot(RobotState(robot_id="B", x=3.0, y=4.0, status="WAITING"))
    store.update_intent(RobotIntent(robot_id="A", resource_id="I1", eta=2.0))
    store.update_reservation(Reservation(resource_id="I1", robot_id="A", status="ACTIVE"))
    store.update_task(Task(task_id="T01", pickup="S1", dropoff="S2", assigned_robot="A"))
    store.add_event(Event(event_type="CONFLICT", robot_id="A", related_robot_id="B", message="Conflict at I1"))
    store.add_event(Event(event_type="INFO", robot_id="B", message="B waiting"))

    # Use ros2 mode in unit tests to prevent mock simulator from auto-overwriting fixture store data
    app, _, _ = create_app(mode="ros2", store=store)

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["robots_tracked"] == 2


def test_api_state(client):
    res = client.get("/api/state")
    assert res.status_code == 200
    data = res.get_json()
    assert "robots" in data
    assert "A" in data["robots"]
    assert data["robots"]["A"]["x"] == 1.0


def test_api_robots(client):
    res = client.get("/api/robots")
    assert res.status_code == 200
    data = res.get_json()
    assert "robots" in data
    assert data["robots"]["B"]["status"] == "WAITING"


def test_api_intents(client):
    res = client.get("/api/intents")
    assert res.status_code == 200
    data = res.get_json()
    assert "intents" in data
    assert len(data["intents"]) == 1
    assert data["intents"][0]["resource_id"] == "I1"


def test_api_reservations(client):
    res = client.get("/api/reservations")
    assert res.status_code == 200
    data = res.get_json()
    assert "reservations" in data
    assert len(data["reservations"]) == 1
    assert data["reservations"][0]["robot_id"] == "A"


def test_api_tasks(client):
    res = client.get("/api/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["task_id"] == "T01"


def test_api_events(client):
    res = client.get("/api/events")
    assert res.status_code == 200
    data = res.get_json()
    assert "events" in data
    assert len(data["events"]) == 2

    # Test filtering by event_type
    res_filtered = client.get("/api/events?event_type=CONFLICT")
    data_filtered = res_filtered.get_json()
    assert len(data_filtered["events"]) == 1
    assert data_filtered["events"][0]["event_type"] == "CONFLICT"


def test_api_network(client):
    res = client.get("/api/network")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data
    assert data["status"] == "NORMAL"


def test_api_metrics(client):
    res = client.get("/api/metrics")
    assert res.status_code == 200
    data = res.get_json()
    assert "mode" in data


def test_api_experiments(client):
    res = client.get("/api/experiments")
    assert res.status_code == 200
    data = res.get_json()
    assert "experiments" in data


def test_no_control_endpoints_exist(client):
    """Ensure dashboard remains read-only and no command routes exist."""
    assert client.post("/stop_robot").status_code == 404
    assert client.post("/api/assign_task").status_code == 404
    assert client.post("/api/reserve_resource").status_code == 404


def test_api_mode_switch(client):
    """Test hot-swapping modes via /api/mode/switch."""
    # Invalid mode
    res = client.post("/api/mode/switch", json={"mode": "invalid"})
    assert res.status_code == 400

    # Switch to mock
    res = client.post("/api/mode/switch", json={"mode": "mock", "scenario": "normal"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["mode"] == "mock"
    assert data["scenario"] == "normal"

    # Switch to same mode
    res = client.post("/api/mode/switch", json={"mode": "mock"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "no_change"

