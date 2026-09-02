#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped


class DynamicTfPublisher(Node):
    def __init__(self):
        super().__init__(
            'dynamic_lidar_tf_publisher',
            parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)]
        )
        self.declare_parameter('base_frame_id', 'amr_blue/base_link')
        self.declare_parameter('child_frame_id', 'amr_blue/lidar_link/lidar_2d')

        self.base_frame_id = self.get_parameter('base_frame_id').get_parameter_value().string_value
        self.child_frame_id = self.get_parameter('child_frame_id').get_parameter_value().string_value

        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.02, self.publish_tf)  # 50 Hz

    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.base_frame_id
        t.child_frame_id = self.child_frame_id

        t.transform.translation.x = 0.14
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.11

        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicTfPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
