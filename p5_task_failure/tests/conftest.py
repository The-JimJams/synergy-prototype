"""
P5 Test Suite — Shared Fixtures (conftest.py)
=============================================

Provides deterministic, reusable test fixtures for all P5 unit tests.

All values are hard-coded constants so tests are repeatable and
independent of runtime state (no random seeds, no timestamps from
datetime.now(), no external data sources).

Three robots (A, B, C) and two tasks (T01, T02) are defined.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.models.bid import Bid
from p5.models.heartbeat import Heartbeat, HeartbeatStatus
from p5.models.events import P5Event, P5EventType

# ---------------------------------------------------------------------------
# Deterministic timestamp (always the same — no datetime.now())
# ---------------------------------------------------------------------------
FIXED_UTC = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Robot fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def robot_a() -> Robot:
    """Robot A — AVAILABLE, high battery, at (2, 2)."""
    return Robot(
        robot_id="A",
        position=(2.0, 2.0),
        battery=90.0,
        payload_capacity=500.0,
        current_task=None,
        workload=0,
        status=RobotStatus.AVAILABLE,
        capabilities=("CARRY", "LIFT"),
    )


@pytest.fixture()
def robot_b() -> Robot:
    """Robot B — AVAILABLE, mid battery, at (8, 3)."""
    return Robot(
        robot_id="B",
        position=(8.0, 3.0),
        battery=65.0,
        payload_capacity=300.0,
        current_task=None,
        workload=0,
        status=RobotStatus.AVAILABLE,
        capabilities=("CARRY",),
    )


@pytest.fixture()
def robot_c() -> Robot:
    """Robot C — BUSY with T02, at (15, 10)."""
    return Robot(
        robot_id="C",
        position=(15.0, 10.0),
        battery=45.0,
        payload_capacity=400.0,
        current_task="T02",
        workload=1,
        status=RobotStatus.BUSY,
        capabilities=("CARRY", "HAZMAT"),
    )


# ---------------------------------------------------------------------------
# Task fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def task_t01() -> Task:
    """Task T01 — high priority, AVAILABLE, no assigned robot."""
    return Task(
        task_id="T01",
        pickup_location=(10.0, 4.0),
        dropoff_location=(18.0, 9.0),
        priority=7,
        deadline=60.0,
        required_payload=100.0,
        status=TaskStatus.AVAILABLE,
        assigned_robot=None,
        required_capabilities=("CARRY",),
    )


@pytest.fixture()
def task_t02() -> Task:
    """Task T02 — lower priority, IN_PROGRESS, assigned to Robot C."""
    return Task(
        task_id="T02",
        pickup_location=(5.0, 5.0),
        dropoff_location=(12.0, 8.0),
        priority=3,
        deadline=120.0,
        required_payload=200.0,
        status=TaskStatus.IN_PROGRESS,
        assigned_robot="C",
        required_capabilities=("CARRY",),
    )


# ---------------------------------------------------------------------------
# Bid fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_bid(robot_a: Robot, task_t01: Task) -> Bid:
    """A sample Bid — Robot A bidding on T01, Phase 1 placeholder values."""
    return Bid(
        task_id=task_t01.task_id,
        robot_id=robot_a.robot_id,
        score=0.0,       # Phase 4 will compute real scores
        estimated_time=0.0,
        distance=robot_a.distance_to(task_t01.pickup_location),
        battery_cost=0.0,
        valid=True,
        timestamp=FIXED_UTC,
    )


# ---------------------------------------------------------------------------
# Heartbeat fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def heartbeat_alive() -> Heartbeat:
    """A heartbeat indicating Robot A is ALIVE."""
    return Heartbeat(
        robot_id="A",
        timestamp=FIXED_UTC,
        status=HeartbeatStatus.ALIVE,
    )


@pytest.fixture()
def heartbeat_failed() -> Heartbeat:
    """A heartbeat indicating Robot B is FAILED."""
    return Heartbeat(
        robot_id="B",
        timestamp=FIXED_UTC,
        status=HeartbeatStatus.FAILED,
    )


# ---------------------------------------------------------------------------
# Event fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def event_task_announced(task_t01: Task) -> P5Event:
    """A TASK_ANNOUNCED event for T01."""
    return P5Event(
        event_type=P5EventType.TASK_ANNOUNCED,
        timestamp=FIXED_UTC,
        source_robot=None,
        task_id=task_t01.task_id,
        payload=None,
    )
