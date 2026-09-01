"""
P5 Unit Tests — Bid Model
==========================

Tests that the Bid dataclass behaves correctly.

Phase 1: Bid is a data structure only.
Phase 4: Score computation will be tested when Bidder is implemented.

No ROS 2, Gazebo, Nav2, or other external dependency is required.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from p5.models.bid import Bid
from p5.models.robot import Robot


# ---------------------------------------------------------------------------
# Bid construction
# ---------------------------------------------------------------------------

class TestBidCreation:
    def test_bid_fields(self, sample_bid: Bid):
        """sample_bid fixture has the expected field values."""
        assert sample_bid.task_id == "T01"
        assert sample_bid.robot_id == "A"
        assert sample_bid.score == pytest.approx(0.0)      # Phase 1 placeholder
        assert sample_bid.valid is True
        assert isinstance(sample_bid.timestamp, datetime)

    def test_bid_distance_is_float(self, sample_bid: Bid):
        """distance field must be a non-negative float."""
        assert isinstance(sample_bid.distance, float)
        assert sample_bid.distance >= 0.0

    def test_bid_distance_matches_manual_calc(self, sample_bid: Bid, robot_a: Robot):
        """Bid distance should equal Robot A's distance to T01 pickup (10,4)."""
        expected = robot_a.distance_to((10.0, 4.0))
        assert sample_bid.distance == pytest.approx(expected)

    def test_bid_timestamp_is_utc(self, sample_bid: Bid):
        """Bid timestamp must be timezone-aware UTC."""
        assert sample_bid.timestamp.tzinfo is not None

    def test_invalid_bid_can_be_created(self):
        """A Bid with valid=False is explicitly representable."""
        invalid_bid = Bid(
            task_id="T99",
            robot_id="Z",
            score=0.0,
            estimated_time=0.0,
            distance=9999.9,
            battery_cost=0.0,
            valid=False,
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        assert invalid_bid.valid is False
        assert "INVALID" in str(invalid_bid)


# ---------------------------------------------------------------------------
# Bid string representation
# ---------------------------------------------------------------------------

class TestBidStr:
    def test_str_contains_robot_id(self, sample_bid: Bid):
        """__str__ includes the robot_id."""
        assert "A" in str(sample_bid)

    def test_str_contains_task_id(self, sample_bid: Bid):
        """__str__ includes the task_id."""
        assert "T01" in str(sample_bid)

    def test_str_valid_bid_says_valid(self, sample_bid: Bid):
        """__str__ of a valid bid includes 'VALID'."""
        assert "VALID" in str(sample_bid)
