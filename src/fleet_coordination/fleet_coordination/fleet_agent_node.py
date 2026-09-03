#!/usr/bin/env python3
"""Per-robot telemetry publisher.

Publishes this robot's map-frame pose on ``/<robot_id>/state`` and a liveness
beat on ``/<robot_id>/heartbeat``.  It is a *reporter*: it makes no allocation,
conflict or navigation decisions.

Why the pose comes from TF and not from /odom
---------------------------------------------
Gazebo's DiffDrive plugin integrates odometry from zero at spawn, so /odom is an
odom-frame pose, not a world pose.  Measured in the running warehouse world:
``amr_blue`` spawns at (-3.5, 5.25) while ``/amr_blue/odom`` reports
x = 6.3e-17, y = -2.1e-33.  Publishing that as RobotState.x/y put all three
robots on top of the origin and made their motion read as straight-line drift
across the dashboard.

The map-frame pose is ``map -> <base_frame>``, composed by tf2 from AMCL's
``map -> odom`` and DiffDrive's ``odom -> base_link``.  That is the same frame
Nav2 plans in, so what the dashboard draws is what the navigation stack sees.
"""

import math

import rclpy
from rclpy.node import Node
from fleet_msgs.msg import Heartbeat, RobotState
from nav_msgs.msg import Odometry
from tf2_ros import Buffer, TransformListener, LookupException, ConnectivityException, ExtrapolationException

# Gazebo model frame that backs each fleet robot id.
DEFAULT_BASE_FRAMES = {
    'amr_a': 'amr_blue/base_link',
    'amr_b': 'amr_green/base_link',
    'amr_c': 'amr_orange/base_link',
}

# Telemetry rate. Odometry arrives at 20 Hz; publishing state at 2 Hz was the
# stale-telemetry bottleneck behind the choppy dashboard motion.
STATE_PUBLISH_HZ = 20.0
HEARTBEAT_PUBLISH_HZ = 2.0


def _yaw_from_quaternion(x, y, z, w):
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class FleetAgentNode(Node):
    def __init__(self):
        super().__init__('fleet_agent_node')
        self.declare_parameter('robot_id', 'amr_a')
        self.robot_id = self.get_parameter('robot_id').value.strip('/')
        self.namespace = f'/{self.robot_id}'

        self.declare_parameter('map_frame_id', 'map')
        self.declare_parameter('base_frame_id', DEFAULT_BASE_FRAMES.get(self.robot_id, 'base_link'))
        self.map_frame_id = self.get_parameter('map_frame_id').value
        self.base_frame_id = self.get_parameter('base_frame_id').value

        self.state_publisher = self.create_publisher(RobotState, f'{self.namespace}/state', 10)
        self.heartbeat_publisher = self.create_publisher(Heartbeat, f'{self.namespace}/heartbeat', 10)

        # Internal state
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.current_lin_vel = 0.0
        self.current_ang_vel = 0.0
        self.pose_frame = 'odom'          # which frame current_x/y are actually in
        self._warned_no_tf = False

        # Odom supplies body-frame velocities; it must not supply position.
        self.create_subscription(Odometry, f'{self.namespace}/odom', self.odom_callback, 10)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.create_timer(1.0 / STATE_PUBLISH_HZ, self.publish_state)
        self.create_timer(1.0 / HEARTBEAT_PUBLISH_HZ, self.publish_heartbeat)

        self.get_logger().info(
            f'Fleet agent for {self.robot_id}: publishing {self.map_frame_id}-frame pose of '
            f'{self.base_frame_id} at {STATE_PUBLISH_HZ:.0f} Hz.'
        )

    def odom_callback(self, msg):
        """Velocities only. See the module docstring for why position is ignored here."""
        self.current_lin_vel = msg.twist.twist.linear.x
        self.current_ang_vel = msg.twist.twist.angular.z

        # Fallback pose, used only until the map -> base_link chain is available.
        if self.pose_frame == 'odom':
            self.current_x = msg.pose.pose.position.x
            self.current_y = msg.pose.pose.position.y
            q = msg.pose.pose.orientation
            self.current_theta = _yaw_from_quaternion(q.x, q.y, q.z, q.w)

    def _update_pose_from_tf(self):
        """Refresh the map-frame pose from tf2. Returns True when it succeeded."""
        try:
            tf = self.tf_buffer.lookup_transform(
                self.map_frame_id, self.base_frame_id, rclpy.time.Time()
            )
        except (LookupException, ConnectivityException, ExtrapolationException) as exc:
            if not self._warned_no_tf:
                self.get_logger().warning(
                    f'No {self.map_frame_id} -> {self.base_frame_id} transform yet ({exc}); '
                    f'reporting odom-frame pose until AMCL and the Gazebo TF bridge are up.'
                )
                self._warned_no_tf = True
            return False

        t = tf.transform.translation
        q = tf.transform.rotation
        self.current_x = t.x
        self.current_y = t.y
        self.current_theta = _yaw_from_quaternion(q.x, q.y, q.z, q.w)

        if self.pose_frame != self.map_frame_id:
            self.pose_frame = self.map_frame_id
            self._warned_no_tf = False
            self.get_logger().info(
                f'{self.map_frame_id} -> {self.base_frame_id} transform acquired; '
                f'RobotState now carries the map-frame pose.'
            )
        return True

    def publish_state(self):
        if not self._update_pose_from_tf():
            self.pose_frame = 'odom'

        msg = RobotState()
        msg.robot_id = self.robot_id
        msg.timestamp = self.get_clock().now().nanoseconds / 1e9
        msg.x = float(self.current_x)
        msg.y = float(self.current_y)
        msg.theta = float(self.current_theta)
        msg.linear_velocity = float(self.current_lin_vel)
        msg.angular_velocity = float(self.current_ang_vel)
        msg.battery_percent = 95.0
        msg.current_task_id = ''

        # Reported from measured motion. The task allocator owns task-level state.
        if abs(self.current_lin_vel) > 0.01 or abs(self.current_ang_vel) > 0.01:
            msg.status = 'NAVIGATING'
        else:
            msg.status = 'IDLE'

        self.state_publisher.publish(msg)

    def publish_heartbeat(self):
        msg = Heartbeat()
        msg.robot_id = self.robot_id
        msg.timestamp = self.get_clock().now().nanoseconds / 1e9
        self.heartbeat_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FleetAgentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
