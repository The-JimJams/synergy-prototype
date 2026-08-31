"""
P5 Unit Tests — Heartbeat Model
================================

Tests that the Heartbeat frozen dataclass and HeartbeatStatus enum
behave correctly.

No ROS 2, Gazebo, Nav2, or other external dependency is required.
"""

from __future__ import annotations

import dataclasses
import pytest
from datetime import datetime, timezone

from p5.models.heartbeat import Heartbeat, HeartbeatStatus


# ---------------------------------------------------------------------------
# HeartbeatStatus enum
# ---------------------------------------------------------------------------

class TestHeartbeatStatus:
    def test_all_four_states_exist(self):
        """All required heartbeat states must be defined."""
        expected = {"ALIVE", "SUSPECTED", "FAILED", "RECOVERED"}
        actual = {s.value for s in HeartbeatStatus}
        assert expected == actual, f"Missing: {expected - actual}"

    def test_status_values_are_strings(self):
        for s in HeartbeatStatus:
            assert isinstance(s.value, str)

    def test_lookup_by_value(self):
        assert HeartbeatStatus("ALIVE") is HeartbeatStatus.ALIVE
        assert HeartbeatStatus("FAILED") is HeartbeatStatus.FAILED


# ---------------------------------------------------------------------------
# Heartbeat dataclass
# ---------------------------------------------------------------------------

class TestHeartbeatCreation:
    def test_alive_heartbeat_fields(self, heartbeat_alive: Heartbeat):
        """ALIVE heartbeat has the correct robot_id, timestamp, and status."""
        assert heartbeat_alive.robot_id == "A"
        assert heartbeat_alive.status == HeartbeatStatus.ALIVE
        assert isinstance(heartbeat_alive.timestamp, datetime)

    def test_failed_heartbeat_fields(self, heartbeat_failed: Heartbeat):
        """FAILED heartbeat has the correct robot_id and status."""
        assert heartbeat_failed.robot_id == "B"
        assert heartbeat_failed.status == HeartbeatStatus.FAILED

    def test_heartbeat_is_frozen(self, heartbeat_alive: Heartbeat):
        """Heartbeat dataclass must be frozen (immutable)."""
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            heartbeat_alive.status = HeartbeatStatus.FAILED  # type: ignore[misc]

    def test_heartbeat_timestamp_is_aware(self, heartbeat_alive: Heartbeat):
        """Heartbeat timestamp must be timezone-aware."""
        assert heartbeat_alive.timestamp.tzinfo is not None

    def test_two_identical_heartbeats_are_equal(self):
        """Two Heartbeats with identical fields should compare equal (frozen dataclass)."""
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        h1 = Heartbeat(robot_id="X", timestamp=ts, status=HeartbeatStatus.ALIVE)
        h2 = Heartbeat(robot_id="X", timestamp=ts, status=HeartbeatStatus.ALIVE)
        assert h1 == h2

    def test_different_robot_ids_are_not_equal(self):
        """Heartbeats with different robot_ids must not be equal."""
        ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
        h1 = Heartbeat(robot_id="A", timestamp=ts, status=HeartbeatStatus.ALIVE)
        h2 = Heartbeat(robot_id="B", timestamp=ts, status=HeartbeatStatus.ALIVE)
        assert h1 != h2


# ---------------------------------------------------------------------------
# Heartbeat string representation
# ---------------------------------------------------------------------------

class TestHeartbeatStr:
    def test_str_contains_robot_id(self, heartbeat_alive: Heartbeat):
        assert "A" in str(heartbeat_alive)

    def test_str_contains_status(self, heartbeat_alive: Heartbeat):
        assert "ALIVE" in str(heartbeat_alive)
