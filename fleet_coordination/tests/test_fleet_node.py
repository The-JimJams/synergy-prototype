"""
Unit tests for FleetCoordinationNode and FleetCoordinationCore.
===============================================================

Tests odometry ingestion, WorldModel state tracking, JSON broadcasting,
peer telemetry reception, self-message filtering, and multi-robot mesh.
"""

from __future__ import annotations

import math
import pytest

from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.ros_interface.fleet_node import (
    FleetCoordinationCore,
    odometry_to_robot_state,
    quaternion_to_yaw,
)


class TestOdometryAndConversion:
    """Tests odometry conversion functions."""

    def test_quaternion_to_yaw_cardinal_angles(self) -> None:
        # Yaw = 0 (facing +X) -> q = (0, 0, 0, 1)
        assert quaternion_to_yaw(0, 0, 0, 1) == pytest.approx(0.0)

        # Yaw = +pi/2 (+90 deg, facing +Y) -> q_z = sin(pi/4) = 0.7071, q_w = cos(pi/4) = 0.7071
        assert quaternion_to_yaw(0, 0, 0.70710678, 0.70710678) == pytest.approx(math.pi / 2, abs=1e-4)

        # Yaw = -pi/2 (-90 deg, facing -Y) -> q_z = -0.7071, q_w = 0.7071
        assert quaternion_to_yaw(0, 0, -0.70710678, 0.70710678) == pytest.approx(-math.pi / 2, abs=1e-4)

        # Yaw = pi (180 deg, facing -X) -> q_z = 1.0, q_w = 0.0
        assert abs(quaternion_to_yaw(0, 0, 1.0, 0.0)) == pytest.approx(math.pi, abs=1e-4)

    def test_odometry_to_robot_state_idle(self) -> None:
        state = odometry_to_robot_state(
            robot_id="amr_a",
            pos_x=-3.5,
            pos_y=1.75,
            yaw=0.0,
            linear_vel=0.0,
            angular_vel=0.0,
            timestamp=1700000000.0,
        )

        assert state.robot_id == "amr_a"
        assert state.pose == Pose2D(-3.5, 1.75, 0.0)
        assert state.linear_velocity == 0.0
        assert state.status == RobotStatus.IDLE
        assert state.timestamp == 1700000000.0
        assert state.battery_percent == 100.0

    def test_odometry_to_robot_state_navigating(self) -> None:
        state = odometry_to_robot_state(
            robot_id="amr_b",
            pos_x=0.0,
            pos_y=5.5,
            yaw=-1.57,
            linear_vel=0.45,
            angular_vel=-0.05,
            timestamp=1700000010.0,
        )

        assert state.robot_id == "amr_b"
        assert state.pose.x == 0.0
        assert state.pose.y == 5.5
        assert state.pose.theta == -1.57
        assert state.linear_velocity == 0.45
        assert state.angular_velocity == -0.05
        assert state.status == RobotStatus.NAVIGATING


class TestFleetCoordinationCore:
    """Tests the decentralized agent logic core."""

    def test_init_validation(self) -> None:
        with pytest.raises(ValueError, match="robot_id cannot be empty"):
            FleetCoordinationCore(robot_id="")

        core = FleetCoordinationCore(robot_id="amr_a")
        assert core.robot_id == "amr_a"
        assert core.world_model.robot_id == "amr_a"
        assert core.world_model.get_own_state() is None

    def test_process_odometry_updates_world_model(self) -> None:
        core = FleetCoordinationCore(robot_id="amr_a")
        state = core.process_odometry(
            pos_x=-3.5,
            pos_y=1.75,
            yaw=0.0,
            linear_vel=0.5,
            angular_vel=0.0,
            timestamp=1700000001.0,
        )

        assert state.robot_id == "amr_a"
        own_state = core.world_model.get_own_state()
        assert own_state is not None
        assert own_state.pose == Pose2D(-3.5, 1.75, 0.0)
        assert own_state.status == RobotStatus.NAVIGATING

    def test_generate_state_broadcast_json(self) -> None:
        core = FleetCoordinationCore(robot_id="amr_a")
        assert core.generate_state_broadcast_json() is None

        core.process_odometry(
            pos_x=-3.5,
            pos_y=1.75,
            yaw=0.0,
            linear_vel=0.0,
            angular_vel=0.0,
            timestamp=1700000000.0,
        )
        json_str = core.generate_state_broadcast_json()
        assert json_str is not None
        assert '"robot_id": "amr_a"' in json_str
        assert '"status": "IDLE"' in json_str

    def test_self_message_filtering(self) -> None:
        core = FleetCoordinationCore(robot_id="amr_a")
        core.process_odometry(
            pos_x=-3.5, pos_y=1.75, yaw=0.0, linear_vel=0.0, angular_vel=0.0, timestamp=1700000000.0
        )
        self_json = core.generate_state_broadcast_json()
        assert self_json is not None

        # Process self-broadcast
        accepted, log_msg = core.handle_peer_state_json(self_json)
        assert accepted is False
        assert "Ignored self-broadcast" in log_msg
        # WorldModel peer states must remain empty
        assert len(core.world_model.get_all_peer_states()) == 0

    def test_peer_state_ingestion(self) -> None:
        core_a = FleetCoordinationCore(robot_id="amr_a")
        core_b = FleetCoordinationCore(robot_id="amr_b")

        # B moves
        core_b.process_odometry(
            pos_x=0.0, pos_y=5.0, yaw=-1.57, linear_vel=0.5, angular_vel=0.0, timestamp=1700000002.0
        )
        b_json = core_b.generate_state_broadcast_json()
        assert b_json is not None

        # A receives B's broadcast
        accepted, log_msg = core_a.handle_peer_state_json(b_json)
        assert accepted is True
        assert "Received state from amr_b" in log_msg

        # Verify A's WorldModel has B's state
        peer_b_state = core_a.world_model.get_peer_state("amr_b")
        assert peer_b_state is not None
        assert peer_b_state.robot_id == "amr_b"
        assert peer_b_state.pose == Pose2D(0.0, 5.0, -1.57)
        assert peer_b_state.status == RobotStatus.NAVIGATING


class TestMultiRobotMesh:
    """Simulates multi-robot decentralized gossip mesh across 3 AMRs."""

    def test_three_robot_gossip_mesh(self) -> None:
        node_a = FleetCoordinationCore(robot_id="amr_a")
        node_b = FleetCoordinationCore(robot_id="amr_b")
        node_c = FleetCoordinationCore(robot_id="amr_c")

        # 1. Update local odometry for all 3 robots
        node_a.process_odometry(-3.5, 1.75, 0.0, 0.5, 0.0, timestamp=1700000001.0)
        node_b.process_odometry(0.0, 6.0, -1.57, 0.4, 0.0, timestamp=1700000001.0)
        node_c.process_odometry(3.5, -4.0, 3.14, 0.0, 0.0, timestamp=1700000001.0)

        # 2. Generate JSON broadcast packets
        msg_a = node_a.generate_state_broadcast_json()
        msg_b = node_b.generate_state_broadcast_json()
        msg_c = node_c.generate_state_broadcast_json()

        assert msg_a is not None and msg_b is not None and msg_c is not None

        # 3. Simulate ROS 2 pub/sub broadcast channel (/fleet/robot_state)
        # Everyone receives every message (including their own)
        broadcast_channel = [msg_a, msg_b, msg_c]

        for msg in broadcast_channel:
            node_a.handle_peer_state_json(msg)
            node_b.handle_peer_state_json(msg)
            node_c.handle_peer_state_json(msg)

        # 4. Assert Node A view: own=A, peers={B, C}
        assert node_a.world_model.get_own_state().robot_id == "amr_a"  # type: ignore
        assert node_a.world_model.get_peer_state("amr_a") is None
        assert node_a.world_model.get_peer_state("amr_b") is not None
        assert node_a.world_model.get_peer_state("amr_b").pose.y == 6.0  # type: ignore
        assert node_a.world_model.get_peer_state("amr_c") is not None
        assert node_a.world_model.get_peer_state("amr_c").pose.x == 3.5  # type: ignore

        # 5. Assert Node B view: own=B, peers={A, C}
        assert node_b.world_model.get_own_state().robot_id == "amr_b"  # type: ignore
        assert node_b.world_model.get_peer_state("amr_b") is None
        assert node_b.world_model.get_peer_state("amr_a") is not None
        assert node_b.world_model.get_peer_state("amr_c") is not None

        # 6. Assert Node C view: own=C, peers={A, B}
        assert node_c.world_model.get_own_state().robot_id == "amr_c"  # type: ignore
        assert node_c.world_model.get_peer_state("amr_c") is None
        assert node_c.world_model.get_peer_state("amr_a") is not None
        assert node_c.world_model.get_peer_state("amr_b") is not None

        # 7. Check freshness at t = 1700000003.0 (age = 2s <= 5s)
        fresh_peers_a = node_a.world_model.get_fresh_peer_states(now=1700000003.0)
        assert len(fresh_peers_a) == 2
        assert "amr_b" in fresh_peers_a and "amr_c" in fresh_peers_a
