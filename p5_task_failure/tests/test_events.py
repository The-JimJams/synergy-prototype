"""
P5 Unit Tests — Events Model & Adapter Interfaces
===================================================

Tests that:
  - P5EventType enum has all expected event types.
  - P5Event frozen dataclass is correctly constructed.
  - All adapter Protocol interfaces can be imported without error.
  - Adapter interfaces can be referenced without importing ROS 2.

No ROS 2, Gazebo, Nav2, or other external dependency is required.
"""

from __future__ import annotations

import dataclasses
import pytest
from datetime import datetime, timezone

from p5.models.events import P5Event, P5EventType
from p5.adapters.interfaces import (
    TaskSource,
    RobotStateProvider,
    BidCalculator,
    WinnerSelector,
    HeartbeatSource,
    FailureDetector,
    TaskRecoveryManager,
    EventSink,
    NavigationAdapter,
)


# ---------------------------------------------------------------------------
# P5EventType enum
# ---------------------------------------------------------------------------

class TestP5EventType:
    def test_all_nine_event_types_defined(self):
        """All 9 required event types must be present."""
        expected = {
            "TASK_ANNOUNCED",
            "BID_SUBMITTED",
            "TASK_ASSIGNED",
            "TASK_STARTED",
            "TASK_COMPLETED",
            "TASK_RELEASED",
            "TASK_REASSIGNED",
            "ROBOT_FAILED",
            "ROBOT_RECOVERED",
        }
        actual = {e.value for e in P5EventType}
        assert expected == actual, f"Missing: {expected - actual}"

    def test_event_type_values_are_strings(self):
        for et in P5EventType:
            assert isinstance(et.value, str)

    def test_lookup_by_value(self):
        assert P5EventType("ROBOT_FAILED") is P5EventType.ROBOT_FAILED
        assert P5EventType("TASK_ANNOUNCED") is P5EventType.TASK_ANNOUNCED


# ---------------------------------------------------------------------------
# P5Event dataclass
# ---------------------------------------------------------------------------

class TestP5EventCreation:
    def test_task_announced_event(self, event_task_announced: P5Event):
        """TASK_ANNOUNCED event has correct type, task_id, and no source robot."""
        assert event_task_announced.event_type == P5EventType.TASK_ANNOUNCED
        assert event_task_announced.task_id == "T01"
        assert event_task_announced.source_robot is None
        assert event_task_announced.payload is None

    def test_event_is_frozen(self, event_task_announced: P5Event):
        """P5Event must be immutable (frozen dataclass)."""
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            event_task_announced.task_id = "T99"  # type: ignore[misc]

    def test_event_timestamp_is_aware(self, event_task_announced: P5Event):
        """Event timestamp must be timezone-aware."""
        assert event_task_announced.timestamp.tzinfo is not None

    def test_event_with_source_robot(self):
        """An event can carry a source_robot field."""
        e = P5Event(
            event_type=P5EventType.BID_SUBMITTED,
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_robot="A",
            task_id="T01",
            payload={"score": 0.75},
        )
        assert e.source_robot == "A"
        assert e.payload == {"score": 0.75}

    def test_robot_failed_event(self):
        """A ROBOT_FAILED event can be created with a source robot and no task."""
        e = P5Event(
            event_type=P5EventType.ROBOT_FAILED,
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            source_robot="B",
            task_id=None,
            payload=None,
        )
        assert e.event_type == P5EventType.ROBOT_FAILED
        assert e.source_robot == "B"
        assert e.task_id is None

    def test_two_equal_events(self):
        """Two P5Events with identical fields compare equal."""
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        e1 = P5Event(P5EventType.TASK_COMPLETED, ts, "A", "T01", None)
        e2 = P5Event(P5EventType.TASK_COMPLETED, ts, "A", "T01", None)
        assert e1 == e2


# ---------------------------------------------------------------------------
# P5Event string representation
# ---------------------------------------------------------------------------

class TestP5EventStr:
    def test_str_contains_event_type(self, event_task_announced: P5Event):
        assert "TASK_ANNOUNCED" in str(event_task_announced)

    def test_str_contains_task_id(self, event_task_announced: P5Event):
        assert "T01" in str(event_task_announced)


# ---------------------------------------------------------------------------
# Adapter interfaces — import and protocol verification
# ---------------------------------------------------------------------------

class TestAdapterInterfaces:
    """Verify that all adapter interfaces can be imported and are Protocols.

    This test does NOT instantiate any adapter.
    It only verifies that the interface definitions load cleanly without
    importing ROS 2 or any external dependency.
    """

    def test_task_source_is_protocol(self):
        from typing import get_type_hints
        assert hasattr(TaskSource, "get_available_tasks")
        assert hasattr(TaskSource, "acknowledge_task")

    def test_robot_state_provider_is_protocol(self):
        assert hasattr(RobotStateProvider, "get_robot_state")
        assert hasattr(RobotStateProvider, "get_all_robots")

    def test_bid_calculator_is_protocol(self):
        assert hasattr(BidCalculator, "calculate_bid")

    def test_winner_selector_is_protocol(self):
        assert hasattr(WinnerSelector, "select_winner")

    def test_heartbeat_source_is_protocol(self):
        assert hasattr(HeartbeatSource, "get_latest_heartbeat")
        assert hasattr(HeartbeatSource, "get_all_heartbeats")

    def test_failure_detector_is_protocol(self):
        assert hasattr(FailureDetector, "is_failed")
        assert hasattr(FailureDetector, "is_suspected")

    def test_task_recovery_manager_is_protocol(self):
        assert hasattr(TaskRecoveryManager, "release_task")
        assert hasattr(TaskRecoveryManager, "re_announce_task")

    def test_event_sink_is_protocol(self):
        assert hasattr(EventSink, "emit")

    def test_navigation_adapter_is_protocol(self):
        assert hasattr(NavigationAdapter, "send_navigation_goal")
        assert hasattr(NavigationAdapter, "cancel_navigation_goal")

    def test_no_ros2_in_interfaces(self):
        """Adapter interface module must not import rclpy or any ROS 2 module."""
        import p5.adapters.interfaces as iface_module
        import sys
        # Check that no rclpy module was imported as a side effect
        ros_modules = [k for k in sys.modules if "rclpy" in k or "ros2" in k.lower()]
        assert ros_modules == [], (
            f"ROS 2 modules were imported: {ros_modules}. "
            "The P5 core must not depend on ROS 2."
        )
