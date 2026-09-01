"""
Tests for dashboard.simulator — Phase 3 verification.

Covers:
- Scenario definitions loading
- FleetSimulator lifecycle (start, stop, step progression)
- DataStore population via simulator actions
- All 6 mock scenarios (normal, conflict, reroute, failure, network, full_demo)
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_store import DataStore
from simulator.scenarios import get_scenario, AVAILABLE_SCENARIOS
from simulator.fleet_simulator import FleetSimulator


def test_available_scenarios():
    assert "normal" in AVAILABLE_SCENARIOS
    assert "conflict" in AVAILABLE_SCENARIOS
    assert "reroute" in AVAILABLE_SCENARIOS
    assert "failure" in AVAILABLE_SCENARIOS
    assert "network" in AVAILABLE_SCENARIOS
    assert "full_demo" in AVAILABLE_SCENARIOS

    for name in AVAILABLE_SCENARIOS:
        steps = get_scenario(name)
        assert len(steps) > 0
        assert "delay" in steps[0]
        assert "actions" in steps[0]


def test_simulator_execution():
    store = DataStore()
    sim = FleetSimulator(store, speed_multiplier=100.0, loop=False)

    # Load small test scenario
    custom_scenario = [
        {
            "delay": 0.01,
            "description": "Step 1",
            "actions": [
                {
                    "type": "update_robot",
                    "data": {"robot_id": "A", "x": 1.0, "y": 2.0, "status": "MOVING"},
                },
                {
                    "type": "add_event",
                    "data": {"event_type": "INFO", "message": "Simulator started"},
                },
            ],
        },
        {
            "delay": 0.01,
            "description": "Step 2",
            "actions": [
                {
                    "type": "update_reservation",
                    "data": {"resource_id": "I1", "robot_id": "A", "status": "ACTIVE"},
                }
            ],
        },
    ]

    sim.load_scenario(custom_scenario)
    assert not sim.is_running()

    sim.start()
    assert sim.is_running()

    # Wait for completion (fast playback)
    time.sleep(0.2)
    sim.stop()

    assert not sim.is_running()

    # Check store populated
    robot_a = store.get_robot_state("A")
    assert robot_a is not None
    assert robot_a["x"] == 1.0
    assert robot_a["status"] == "MOVING"

    events = store.get_events()
    assert len(events) == 1
    assert events[0]["message"] == "Simulator started"

    reservations = store.get_reservations()
    assert len(reservations) == 1
    assert reservations[0]["resource_id"] == "I1"
    assert reservations[0]["robot_id"] == "A"


def test_full_demo_scenario_runs():
    store = DataStore()
    sim = FleetSimulator(store, speed_multiplier=200.0, loop=False)
    sim.load_scenario("full_demo")
    sim.start()

    time.sleep(0.5)
    sim.stop()

    summary = store.get_summary()
    assert summary["robots_tracked"] >= 3
    assert summary["events_stored"] > 5
    assert summary["tasks_tracked"] >= 3
