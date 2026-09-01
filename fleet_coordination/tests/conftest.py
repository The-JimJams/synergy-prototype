"""
Shared test fixtures for the fleet coordination test suite.

These fixtures provide deterministic, reusable test data.
All timestamps are fixed (not time.time()) so tests are reproducible.

Usage in tests:
    def test_something(sample_pose, sample_robot_state):
        assert sample_robot_state.robot_id == "amr_01"
"""

import pytest

from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.task import Task, TaskType, TaskStatus


# ---------------------------------------------------------------------------
# Fixed timestamp for deterministic tests
# ---------------------------------------------------------------------------
FIXED_TIME = 1_000_000.0  # Arbitrary fixed Unix epoch for all test data


# ---------------------------------------------------------------------------
# Pose fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def origin_pose() -> Pose2D:
    """Pose at the origin."""
    return Pose2D(x=0.0, y=0.0, theta=0.0)


@pytest.fixture
def sample_pose() -> Pose2D:
    """A pose away from the origin."""
    return Pose2D(x=3.0, y=4.0, theta=1.57)


@pytest.fixture
def distant_pose() -> Pose2D:
    """A pose far from the origin (for distance tests)."""
    return Pose2D(x=10.0, y=10.0, theta=0.0)


# ---------------------------------------------------------------------------
# RobotState fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def idle_robot() -> RobotState:
    """An idle robot with full battery at the origin."""
    return RobotState(
        robot_id="amr_01",
        timestamp=FIXED_TIME,
        pose=Pose2D(0.0, 0.0, 0.0),
        battery_percent=100.0,
        status=RobotStatus.IDLE,
    )


@pytest.fixture
def navigating_robot() -> RobotState:
    """A robot actively navigating with a task."""
    return RobotState(
        robot_id="amr_02",
        timestamp=FIXED_TIME,
        pose=Pose2D(5.0, 3.0, 0.78),
        linear_velocity=0.5,
        angular_velocity=0.0,
        battery_percent=75.0,
        current_task_id="task_001",
        status=RobotStatus.NAVIGATING,
    )


@pytest.fixture
def low_battery_robot() -> RobotState:
    """A robot with critically low battery."""
    return RobotState(
        robot_id="amr_03",
        timestamp=FIXED_TIME,
        pose=Pose2D(8.0, 2.0, 3.14),
        battery_percent=10.0,
        status=RobotStatus.IDLE,
    )


# ---------------------------------------------------------------------------
# RobotIntent fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def intent_for_intersection_1() -> RobotIntent:
    """Robot amr_01 intends to use intersection I1."""
    return RobotIntent(
        robot_id="amr_01",
        timestamp=FIXED_TIME,
        task_id="task_001",
        target_resource_id="I1",
        eta=FIXED_TIME + 10.0,
        priority=5.0,
        valid_until=FIXED_TIME + 60.0,
    )


@pytest.fixture
def competing_intent_for_intersection_1() -> RobotIntent:
    """Robot amr_02 ALSO intends to use intersection I1 — conflict!"""
    return RobotIntent(
        robot_id="amr_02",
        timestamp=FIXED_TIME,
        task_id="task_002",
        target_resource_id="I1",
        eta=FIXED_TIME + 12.0,
        priority=7.0,
        valid_until=FIXED_TIME + 60.0,
    )


@pytest.fixture
def expired_intent() -> RobotIntent:
    """An intent that has already expired."""
    return RobotIntent(
        robot_id="amr_03",
        timestamp=FIXED_TIME - 120.0,
        target_resource_id="I2",
        priority=10.0,
        valid_until=FIXED_TIME - 60.0,  # expired 60s ago
    )


# ---------------------------------------------------------------------------
# Reservation fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def active_reservation() -> Reservation:
    """A currently active reservation on I1."""
    return Reservation(
        resource_id="I1",
        robot_id="amr_01",
        start_time=FIXED_TIME - 5.0,
        end_time=FIXED_TIME + 25.0,
        priority=5.0,
        claim_id="claim_001",
        created_at=FIXED_TIME - 10.0,
        expires_at=FIXED_TIME + 60.0,
    )


@pytest.fixture
def expired_reservation() -> Reservation:
    """A reservation that has expired."""
    return Reservation(
        resource_id="I2",
        robot_id="amr_02",
        start_time=FIXED_TIME - 100.0,
        end_time=FIXED_TIME - 70.0,
        priority=3.0,
        claim_id="claim_expired",
        created_at=FIXED_TIME - 110.0,
        expires_at=FIXED_TIME - 60.0,  # expired
    )


# ---------------------------------------------------------------------------
# Task fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_task() -> Task:
    """A standard pickup-and-delivery task."""
    return Task(
        task_id="task_001",
        task_type=TaskType.PICKUP_AND_DELIVERY,
        priority=5,
        deadline=FIXED_TIME + 300.0,
        payload_kg=2.5,
        source_location="SHELF_A3",
        target_location="PACKING_1",
        announced_at=FIXED_TIME,
    )


@pytest.fixture
def urgent_task() -> Task:
    """A high-priority task with a tight deadline."""
    return Task(
        task_id="task_urgent",
        task_type=TaskType.DELIVERY,
        priority=9,
        deadline=FIXED_TIME + 30.0,  # 30 seconds!
        payload_kg=0.5,
        source_location="SHELF_B1",
        target_location="DISPATCH_2",
        announced_at=FIXED_TIME,
    )
