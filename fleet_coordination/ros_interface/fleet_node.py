"""
Fleet Coordination ROS 2 Node — Decentralized AMR Coordination Agent.
=====================================================================

Per-robot ROS 2 node that connects local robot telemetry (odometry) to
the local WorldModel, broadcasts RobotState over decentralized gossip channels,
and receives peer RobotState broadcasts.

ARCHITECTURAL RULES:
1. Decentralized: Every AMR runs its own independent instance of FleetCoordinationNode.
   There is NO master or central coordinator node.
2. Hard Boundary: This file lives in ros_interface/ and is the ONLY layer that
   interacts with ROS 2 (rclpy, subscribers, publishers, timers).
3. The algorithmic core (WorldModel, ConflictDetector, etc.) remains 100% pure Python.
"""

from __future__ import annotations

import math
import time
from typing import Any

from fleet_coordination.algorithm.world_model import WorldModel
from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.pose import Pose2D
from fleet_coordination.models.robot_state import RobotState, RobotStatus
from fleet_coordination.ros_interface.serialization import from_json, to_json

# Conditional rclpy import to allow unit testing on systems without ROS 2 installed
try:
    import rclpy
    from rclpy.node import Node
    from std_msgs.msg import String as StringMsg
    from nav_msgs.msg import Odometry as OdometryMsg

    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    Node = object  # type: ignore
    StringMsg = Any  # type: ignore
    OdometryMsg = Any  # type: ignore


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    """Extract 2D yaw angle (radians, [-pi, pi]) from a quaternion (x, y, z, w).

    Args:
        x: Quaternion x component.
        y: Quaternion y component.
        z: Quaternion z component.
        w: Quaternion w component.

    Returns:
        Yaw angle in radians.
    """
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def odometry_to_robot_state(
    robot_id: str,
    pos_x: float,
    pos_y: float,
    yaw: float,
    linear_vel: float,
    angular_vel: float,
    timestamp: float | None = None,
    battery_percent: float = 100.0,
    current_task_id: str | None = None,
    status: RobotStatus | None = None,
) -> RobotState:
    """Convert raw odometry components into a valid RobotState domain model.

    Args:
        robot_id: Unique string identifier of the robot (e.g. 'amr_a').
        pos_x: X position in map/world coordinates (metres).
        pos_y: Y position in map/world coordinates (metres).
        yaw: Heading orientation in radians.
        linear_vel: Linear velocity magnitude (m/s).
        angular_vel: Angular velocity (rad/s).
        timestamp: Unix epoch timestamp. Defaults to time.time().
        battery_percent: Battery charge (0-100%).
        current_task_id: Active task ID or None.
        status: Operational status. If None, derived from velocity.

    Returns:
        Populated RobotState instance.
    """
    if timestamp is None:
        timestamp = time.time()

    if status is None:
        status = RobotStatus.NAVIGATING if abs(linear_vel) > 0.02 or abs(angular_vel) > 0.05 else RobotStatus.IDLE

    return RobotState(
        robot_id=robot_id,
        timestamp=timestamp,
        pose=Pose2D(x=pos_x, y=pos_y, theta=yaw),
        linear_velocity=abs(linear_vel),
        angular_velocity=angular_vel,
        battery_percent=battery_percent,
        current_task_id=current_task_id,
        status=status,
    )


class FleetCoordinationCore:
    """Decoupled logic core for FleetCoordinationNode.

    Maintains local WorldModel, processes odometry, serializes own state,
    and ingests peer state. Testable without active ROS 2 runtime.
    """

    def __init__(
        self,
        robot_id: str,
        config: CoordinationConfig | None = None,
    ) -> None:
        """Initialize the coordination agent core.

        Args:
            robot_id: Unique identifier for this AMR (e.g. 'amr_a').
            config: Optional coordination configuration.
        """
        if not robot_id:
            raise ValueError("robot_id cannot be empty")

        self.robot_id: str = robot_id
        self.config: CoordinationConfig = config or CoordinationConfig()
        self.world_model: WorldModel = WorldModel(robot_id=self.robot_id, config=self.config)

    def process_odometry(
        self,
        pos_x: float,
        pos_y: float,
        yaw: float,
        linear_vel: float,
        angular_vel: float,
        timestamp: float | None = None,
    ) -> RobotState:
        """Update local robot state from odometry and store in WorldModel.

        Returns:
            The generated local RobotState.
        """
        state = odometry_to_robot_state(
            robot_id=self.robot_id,
            pos_x=pos_x,
            pos_y=pos_y,
            yaw=yaw,
            linear_vel=linear_vel,
            angular_vel=angular_vel,
            timestamp=timestamp,
        )
        self.world_model.set_own_state(state)
        return state

    def generate_state_broadcast_json(self) -> str | None:
        """Serialize current own state to JSON for broadcast.

        Returns:
            JSON string or None if own state has not been set yet.
        """
        own_state = self.world_model.get_own_state()
        if own_state is None:
            return None
        return to_json(own_state)

    def handle_peer_state_json(self, json_str: str, now: float | None = None) -> tuple[bool, str]:
        """Deserialize and ingest an incoming peer state broadcast.

        Self-messages (robot_id == self.robot_id) are safely ignored.

        Args:
            json_str: Serialized RobotState JSON string.
            now: Current reference time for logging/testing.

        Returns:
            (accepted, log_message) tuple.
        """
        try:
            peer_state = from_json(json_str, RobotState)
        except Exception as e:
            return False, f"[{self.robot_id}] Malformed peer state JSON: {e}"

        # Filter out self-broadcast
        if peer_state.robot_id == self.robot_id:
            return False, f"[{self.robot_id}] Ignored self-broadcast"

        updated = self.world_model.update_peer_state(peer_state)
        if updated:
            log_msg = (
                f"[{self.robot_id}] Received state from {peer_state.robot_id}: "
                f"x={peer_state.pose.x:.2f}, y={peer_state.pose.y:.2f}, "
                f"status={peer_state.status.name}, battery={peer_state.battery_percent:.1f}%"
            )
            return True, log_msg
        else:
            return False, f"[{self.robot_id}] Rejected stale/duplicate state from {peer_state.robot_id}"


if ROS2_AVAILABLE:

    class FleetCoordinationNode(Node):
        """ROS 2 Node wrapping the FleetCoordinationCore."""

        def __init__(self) -> None:
            super().__init__("fleet_coordination_node")

            # Declare and get robot_id parameter (default: 'amr_a')
            self.declare_parameter("robot_id", "amr_a")
            self.declare_parameter("publish_rate_hz", 10.0)

            robot_id: str = self.get_parameter("robot_id").get_parameter_value().string_value
            publish_rate: float = self.get_parameter("publish_rate_hz").get_parameter_value().double_value

            self.get_logger().info(f"Initializing FleetCoordinationNode for robot_id: '{robot_id}'")

            # Initialize coordination core and local WorldModel
            self.core = FleetCoordinationCore(robot_id=robot_id)

            # Subscriptions
            # 1. Local odometry from Gazebo/ROS bridge (e.g. /amr_a/odom)
            odom_topic = f"/{robot_id}/odom"
            self.odom_sub = self.create_subscription(
                OdometryMsg,
                odom_topic,
                self._odom_callback,
                10,
            )
            self.get_logger().info(f"Subscribed to local odometry: {odom_topic}")

            # 2. Peer fleet state broadcast channel
            self.state_sub = self.create_subscription(
                StringMsg,
                "/fleet/robot_state",
                self._peer_state_callback,
                10,
            )
            self.get_logger().info("Subscribed to fleet broadcast: /fleet/robot_state")

            # Publishers
            # Broadcast own state to the decentralized fleet topic
            self.state_pub = self.create_publisher(
                StringMsg,
                "/fleet/robot_state",
                10,
            )

            # Periodic state broadcast timer (10 Hz)
            timer_period = 1.0 / max(publish_rate, 1.0)
            self.timer = self.create_timer(timer_period, self._timer_callback)

        def _odom_callback(self, msg: Any) -> None:
            """Convert incoming ROS 2 Odometry message to local RobotState."""
            try:
                pos = msg.pose.pose.position
                ori = msg.pose.pose.orientation
                twist = msg.twist.twist

                yaw = quaternion_to_yaw(ori.x, ori.y, ori.z, ori.w)
                linear_vel = twist.linear.x
                angular_vel = twist.angular.z

                sec = getattr(msg.header.stamp, "sec", 0)
                nanosec = getattr(msg.header.stamp, "nanosec", 0)
                stamp = sec + nanosec * 1e-9 if (sec or nanosec) else time.time()

                self.core.process_odometry(
                    pos_x=pos.x,
                    pos_y=pos.y,
                    yaw=yaw,
                    linear_vel=linear_vel,
                    angular_vel=angular_vel,
                    timestamp=stamp,
                )
            except Exception as e:
                self.get_logger().error(f"Error processing odometry: {e}")

        def _timer_callback(self) -> None:
            """Periodic 10 Hz broadcast of local RobotState."""
            json_str = self.core.generate_state_broadcast_json()
            if json_str is not None:
                msg = StringMsg()
                msg.data = json_str
                self.state_pub.publish(msg)

        def _peer_state_callback(self, msg: Any) -> None:
            """Ingest peer RobotState broadcast."""
            accepted, log_msg = self.core.handle_peer_state_json(msg.data)
            if accepted:
                self.get_logger().info(log_msg)


def main(args: list[str] | None = None) -> None:
    """ROS 2 node main entrypoint."""
    if not ROS2_AVAILABLE:
        print("[-] Error: rclpy is not installed or available in this environment.")
        return

    rclpy.init(args=args)
    node = FleetCoordinationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
