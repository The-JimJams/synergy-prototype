#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from geometry_msgs.msg import TransformStamped

from rclpy.parameter import Parameter

class DynamicTfPublisher(Node):
    def __init__(self):
        super().__init__('dynamic_lidar_tf_publisher',
                         parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.01, self.publish_tf) # 100 Hz
        
    def publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'amr_blue/base_link'
        t.child_frame_id = 'amr_blue/lidar_link/lidar_2d'
        
        t.transform.translation.x = 0.14
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.11
        
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        
        self.br.sendTransform(t)

def main():
    rclpy.init()
    node = DynamicTfPublisher()
    node.set_parameters([rclpy.parameter.Parameter('use_sim_time', rclpy.Parameter.Type.BOOL, True)])
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
