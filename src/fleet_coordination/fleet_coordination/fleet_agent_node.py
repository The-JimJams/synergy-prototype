#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from fleet_msgs.msg import Heartbeat, ResourceClaim, RobotIntent, RobotState
from nav_msgs.msg import Odometry

class FleetAgentNode(Node):
    def __init__(self):
        super().__init__('fleet_agent_node')
        self.declare_parameter('robot_id', 'amr_a')
        self.robot_id = self.get_parameter('robot_id').value.strip('/')
        self.namespace = f'/{self.robot_id}'
        self.state_publisher = self.create_publisher(RobotState, f'{self.namespace}/state', 10)
        self.heartbeat_publisher = self.create_publisher(Heartbeat, f'{self.namespace}/heartbeat', 10)

        # Internal state
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        self.current_lin_vel = 0.0
        self.current_ang_vel = 0.0

        self.create_subscription(Odometry, f'{self.namespace}/odom', self.odom_callback, 10)

        self.create_timer(0.5, self.publish_state)
        self.create_timer(0.5, self.publish_heartbeat)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        self.current_lin_vel = msg.twist.twist.linear.x
        self.current_ang_vel = msg.twist.twist.angular.z

    def publish_state(self):
        msg = RobotState()
        msg.robot_id = self.robot_id
        msg.timestamp = self.get_clock().now().nanoseconds / 1e9
        msg.x = self.current_x
        msg.y = self.current_y
        msg.theta = self.current_theta
        msg.linear_velocity = self.current_lin_vel
        msg.angular_velocity = self.current_ang_vel
        msg.battery_percent = 95.0
        msg.current_task_id = ''

        # Simple heuristic: if moving, it's navigating, else idle.
        # But wait, if it's idle, task_allocator will set AVAILABLE.
        # Let's just always publish IDLE from here, and let task_allocator manage P5 BUSY state internally!
        # Actually, task_allocator relies on this. We'll publish IDLE so it doesn't randomly block capability check.
        # Wait, if we publish IDLE, the dashboard will show it as IDLE.
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
