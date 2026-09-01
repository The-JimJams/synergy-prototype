"""
Tests for dashboard.adapters — Phase 16 & 17 verification.

Covers:
- MockAdapter lifecycle and scenario switching
- ROS2Adapter conversion functions (isolated dictionary / message parsing)
- Graceful behavior when ROS 2 (rclpy) is absent
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_store import DataStore
from adapters.mock_adapter import MockAdapter
from adapters.ros2_adapter import (
    ROS2Adapter,
    robot_state_from_ros,
    robot_intent_from_ros,
    reservation_from_ros,
    event_from_ros,
    network_from_ros,
)


def test_mock_adapter():
    store = DataStore()
    adapter = MockAdapter(store, scenario="conflict", speed=100.0)

    adapter.start()
    assert adapter.is_active()

    adapter.stop()
    assert not adapter.is_active()


def test_ros2_conversions():
    # Test dictionary / message conversion helpers
    raw_state = {"robot_id": "A", "x": 4.2, "y": 7.1, "yaw": 1.57, "velocity": 0.8, "battery": 82, "status": "MOVING"}
    rs = robot_state_from_ros(raw_state)
    assert rs.robot_id == "A"
    assert rs.x == 4.2
    assert rs.status == "MOVING"

    raw_intent = {"robot_id": "B", "resource_id": "I1", "eta": 2.3}
    ri = robot_intent_from_ros(raw_intent)
    assert ri.robot_id == "B"
    assert ri.resource_id == "I1"
    assert ri.eta == 2.3

    raw_res = {"resource_id": "I1", "robot_id": "A", "status": "ACTIVE"}
    res = reservation_from_ros(raw_res)
    assert res.resource_id == "I1"
    assert res.status == "ACTIVE"

    raw_event = {"event_type": "CONFLICT", "robot_id": "A", "message": "Conflict at I1"}
    ev = event_from_ros(raw_event)
    assert ev.event_type == "CONFLICT"
    assert ev.message == "Conflict at I1"

    raw_net = {"status": "DEGRADED", "latency_ms": 120.0, "packet_loss_percent": 5.0, "active_peers": 2}
    net = network_from_ros(raw_net)
    assert net.status == "DEGRADED"
    assert net.latency_ms == 120.0


def test_ros2_adapter_absent_ros():
    store = DataStore()
    adapter = ROS2Adapter(store)

    # When rclpy is absent, adapter gracefully handles start without crashing
    adapter.start()
    assert not adapter.is_active()
    adapter.stop()
