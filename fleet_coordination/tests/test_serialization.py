"""
Unit tests for the ROS 2 Serialization Bridge.
===============================================

Tests deterministic serialization and deserialization between domain dataclasses
and JSON strings / dictionaries for Phase 7.1.
"""

from __future__ import annotations

import json
import pytest

from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.ros_interface.serialization import (
    from_dict,
    from_json,
    to_dict,
    to_json,
)


class TestPose2DSerialization:
    """Tests serialization and deserialization for Pose2D."""

    def test_pose2d_round_trip(self) -> None:
        pose = Pose2D(x=1.23, y=-4.56, theta=0.785)
        json_str = to_json(pose)
        reconstructed = from_json(json_str, Pose2D)

        assert reconstructed == pose
        assert reconstructed.x == pytest.approx(1.23)
        assert reconstructed.y == pytest.approx(-4.56)
        assert reconstructed.theta == pytest.approx(0.785)

    def test_pose2d_default_theta(self) -> None:
        raw_dict = {"x": 2.0, "y": 3.5}
        reconstructed = from_dict(raw_dict, Pose2D)

        assert reconstructed.x == 2.0
        assert reconstructed.y == 3.5
        assert reconstructed.theta == 0.0

    def test_pose2d_missing_required_fields(self) -> None:
        with pytest.raises(ValueError, match="Missing required field 'x'"):
            from_dict({"y": 3.5}, Pose2D)

        with pytest.raises(ValueError, match="Missing required field 'y'"):
            from_dict({"x": 2.0}, Pose2D)


class TestRobotStateSerialization:
    """Tests serialization and deserialization for RobotState and RobotStatus."""

    def test_robot_state_round_trip_full(self) -> None:
        state = RobotState(
            robot_id="amr_a",
            timestamp=1700000000.5,
            pose=Pose2D(x=-3.5, y=1.75, theta=1.57),
            linear_velocity=0.45,
            angular_velocity=-0.12,
            battery_percent=88.5,
            current_task_id="task_pick_101",
            status=RobotStatus.NAVIGATING,
        )

        json_str = to_json(state)
        reconstructed = from_json(json_str, RobotState)

        assert reconstructed == state
        assert reconstructed.robot_id == "amr_a"
        assert reconstructed.timestamp == 1700000000.5
        assert reconstructed.pose == Pose2D(x=-3.5, y=1.75, theta=1.57)
        assert reconstructed.linear_velocity == 0.45
        assert reconstructed.angular_velocity == -0.12
        assert reconstructed.battery_percent == 88.5
        assert reconstructed.current_task_id == "task_pick_101"
        assert reconstructed.status == RobotStatus.NAVIGATING

    def test_robot_state_round_trip_defaults(self) -> None:
        state = RobotState(robot_id="amr_b")
        json_str = to_json(state)
        reconstructed = from_json(json_str, RobotState)

        assert reconstructed.robot_id == "amr_b"
        assert reconstructed.pose == Pose2D(0.0, 0.0, 0.0)
        assert reconstructed.status == RobotStatus.IDLE
        assert reconstructed.current_task_id is None
        assert reconstructed.battery_percent == 100.0

    def test_robot_state_all_status_enums(self) -> None:
        for status in RobotStatus:
            state = RobotState(robot_id="amr_c", status=status)
            json_str = to_json(state)
            reconstructed = from_json(json_str, RobotState)
            assert reconstructed.status == status

    def test_robot_state_invalid_enum(self) -> None:
        data = {
            "robot_id": "amr_a",
            "status": "FLYING",
        }
        with pytest.raises(ValueError, match="Invalid value 'FLYING' for enum RobotStatus"):
            from_dict(data, RobotState)

    def test_robot_state_missing_required_robot_id(self) -> None:
        data = {
            "linear_velocity": 0.5,
        }
        with pytest.raises(ValueError, match="Missing required field 'robot_id'"):
            from_dict(data, RobotState)


class TestRobotIntentSerialization:
    """Tests serialization and deserialization for RobotIntent."""

    def test_robot_intent_round_trip_full(self) -> None:
        intent = RobotIntent(
            robot_id="amr_b",
            timestamp=1700000100.0,
            task_id="task_99",
            target_resource_id="I1",
            eta=1700000115.0,
            priority=2.45,
            planned_waypoints=[
                Pose2D(x=0.0, y=5.0, theta=-1.57),
                Pose2D(x=0.0, y=3.0, theta=-1.57),
                Pose2D(x=0.0, y=1.75, theta=-1.57),
            ],
            valid_until=1700000160.0,
        )

        json_str = to_json(intent)
        reconstructed = from_json(json_str, RobotIntent)

        assert reconstructed == intent
        assert reconstructed.robot_id == "amr_b"
        assert reconstructed.task_id == "task_99"
        assert reconstructed.target_resource_id == "I1"
        assert reconstructed.eta == 1700000115.0
        assert reconstructed.priority == pytest.approx(2.45)
        assert len(reconstructed.planned_waypoints) == 3
        assert reconstructed.planned_waypoints[1] == Pose2D(x=0.0, y=3.0, theta=-1.57)
        assert reconstructed.valid_until == 1700000160.0

    def test_robot_intent_round_trip_minimal(self) -> None:
        intent = RobotIntent(robot_id="amr_a", valid_until=1700000050.0)
        json_str = to_json(intent)
        reconstructed = from_json(json_str, RobotIntent)

        assert reconstructed.robot_id == "amr_a"
        assert reconstructed.task_id is None
        assert reconstructed.target_resource_id is None
        assert reconstructed.eta is None
        assert reconstructed.priority == 0.0
        assert reconstructed.planned_waypoints == []
        assert reconstructed.valid_until == 1700000050.0

    def test_robot_intent_missing_robot_id(self) -> None:
        with pytest.raises(ValueError, match="Missing required field 'robot_id'"):
            from_dict({"target_resource_id": "I1"}, RobotIntent)


class TestSerializationRobustnessAndEdgeCases:
    """Tests invalid inputs, malformed JSON, and deterministic formatting."""

    def test_deterministic_json_keys(self) -> None:
        state = RobotState(robot_id="amr_a", linear_velocity=0.5)
        json1 = to_json(state)
        json2 = to_json(state)

        assert json1 == json2
        # Verify keys are sorted
        parsed = json.loads(json1)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_invalid_json_string(self) -> None:
        with pytest.raises(ValueError, match="Invalid JSON string"):
            from_json("{broken json", RobotState)

    def test_type_error_on_non_string_json(self) -> None:
        with pytest.raises(TypeError, match="Expected str for json_string"):
            from_json(12345, RobotState)  # type: ignore

    def test_type_error_on_non_dict_data(self) -> None:
        with pytest.raises(TypeError, match="Expected dictionary for from_dict"):
            from_dict(["not", "a", "dict"], RobotState)  # type: ignore

    def test_type_error_on_non_dataclass_target(self) -> None:
        with pytest.raises(TypeError, match="is not a dataclass type"):
            from_dict({"a": 1}, dict)  # type: ignore

    def test_numeric_type_mismatch(self) -> None:
        data = {
            "x": "not_a_number",
            "y": 1.0,
        }
        with pytest.raises(TypeError, match="Expected numeric"):
            from_dict(data, Pose2D)

    def test_waypoints_not_a_list(self) -> None:
        data = {
            "robot_id": "amr_a",
            "planned_waypoints": "not_a_list",
        }
        with pytest.raises(TypeError, match="Expected list"):
            from_dict(data, RobotIntent)

    def test_nested_pose_not_a_dict(self) -> None:
        data = {
            "robot_id": "amr_a",
            "pose": "0,0,0",
        }
        with pytest.raises(TypeError, match="Expected dict for dataclass Pose2D"):
            from_dict(data, RobotState)

    def test_unsupported_object_serialization(self) -> None:
        class ArbitraryObject:
            pass

        with pytest.raises(TypeError, match="is not serializable"):
            to_dict(ArbitraryObject())
