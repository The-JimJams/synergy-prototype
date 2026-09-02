#!/usr/bin/env python3
"""ROS 2 read-only bridge that aggregates fleet telemetry into JSON."""

import json
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from fleet_msgs.msg import Heartbeat, ResourceClaim, RobotIntent, RobotState


class DashboardBridgeNode(Node):
    """Subscribe to each robot's state, intent, heartbeat, and reservation topic."""

    ROBOT_IDS = ['amr_a', 'amr_b', 'amr_c']

    def __init__(self):
        super().__init__('dashboard_bridge_node')

        self.state_cache = {}
        self.intent_cache = {}
        self.heartbeat_cache = {}
        self.reservation_cache = {}

        self.telemetry_publisher = self.create_publisher(String, '/fleet/telemetry', 10)

        for robot_id in self.ROBOT_IDS:
            namespace = f'/{robot_id}'
            self.create_subscription(
                RobotState,
                f'{namespace}/state',
                lambda msg, rid=robot_id: self.handle_state(rid, msg),
                10,
            )
            self.create_subscription(
                RobotIntent,
                f'{namespace}/intent',
                lambda msg, rid=robot_id: self.handle_intent(rid, msg),
                10,
            )
            self.create_subscription(
                Heartbeat,
                f'{namespace}/heartbeat',
                lambda msg, rid=robot_id: self.handle_heartbeat(rid, msg),
                10,
            )

        self.create_subscription(
            ResourceClaim,
            '/fleet/reservations',
            self.handle_reservation,
            10,
        )

        self.create_timer(1.0, self.publish_telemetry)
        self.get_logger().info('Dashboard bridge started; publishing merged telemetry to /fleet/telemetry once per second.')

    def handle_state(self, robot_id, msg):
        self.state_cache[robot_id] = {
            'robot_id': msg.robot_id,
            'timestamp': float(msg.timestamp),
            'position': [float(msg.x), float(msg.y)],
            'x': float(msg.x),
            'y': float(msg.y),
            'theta': float(msg.theta),
            'velocity': float(msg.linear_velocity),
            'linear_velocity': float(msg.linear_velocity),
            'angular_velocity': float(msg.angular_velocity),
            'battery': float(msg.battery_percent),
            'battery_percent': float(msg.battery_percent),
            'current_task': msg.current_task_id,
            'current_task_id': msg.current_task_id,
            'status': msg.status,
        }

    def handle_intent(self, robot_id, msg):
        self.intent_cache[robot_id] = {
            'robot_id': msg.robot_id,
            'planned_path': list(msg.planned_path),
            'target_intersection': msg.target_intersection,
            'eta': float(msg.eta),
            'priority': int(msg.priority),
            'task_id': msg.task_id,
        }

    def handle_heartbeat(self, robot_id, msg):
        self.heartbeat_cache[robot_id] = {
            'robot_id': msg.robot_id,
            'timestamp': float(msg.timestamp),
        }

    def handle_reservation(self, msg):
        resource = msg.resource
        self.reservation_cache[resource] = {
            'robot_id': msg.robot_id,
            'resource': msg.resource,
            'start_time': float(msg.start_time),
            'end_time': float(msg.end_time),
            'priority': int(msg.priority),
            'claim_id': msg.claim_id,
            'status': msg.status,
        }

    def _robot_entry(self, robot_id):
        state = self.state_cache.get(robot_id, {})
        intent = self.intent_cache.get(robot_id, {})
        heartbeat = self.heartbeat_cache.get(robot_id, {})

        reservations = []
        for reservation in self.reservation_cache.values():
            if reservation.get('robot_id') == robot_id:
                reservations.append({
                    'resource': reservation.get('resource'),
                    'claim_id': reservation.get('claim_id'),
                    'status': reservation.get('status'),
                    'priority': reservation.get('priority'),
                    'start_time': reservation.get('start_time'),
                    'end_time': reservation.get('end_time'),
                })

        return {
            'state': {
                'robot_id': state.get('robot_id', robot_id),
                'timestamp': state.get('timestamp'),
                'position': state.get('position', []),
                'x': state.get('x'),
                'y': state.get('y'),
                'theta': state.get('theta'),
                'velocity': state.get('velocity'),
                'linear_velocity': state.get('linear_velocity'),
                'angular_velocity': state.get('angular_velocity'),
                'battery': state.get('battery'),
                'battery_percent': state.get('battery_percent'),
                'current_task': state.get('current_task'),
                'current_task_id': state.get('current_task_id'),
                'status': state.get('status', 'unknown'),
            },
            'intent': {
                'robot_id': intent.get('robot_id', robot_id),
                'planned_path': intent.get('planned_path', []),
                'target_intersection': intent.get('target_intersection'),
                'eta': intent.get('eta'),
                'priority': intent.get('priority'),
                'task_id': intent.get('task_id'),
            },
            'heartbeat': {
                'robot_id': heartbeat.get('robot_id', robot_id),
                'timestamp': heartbeat.get('timestamp'),
            },
            'reservations': reservations,
            'active_task': state.get('current_task') or intent.get('task_id'),
        }

    def publish_telemetry(self):
        payload = {
            'timestamp': time.time(),
            'robots': {},
            'reservations': [],
        }

        for robot_id in self.ROBOT_IDS:
            payload['robots'][robot_id] = self._robot_entry(robot_id)

        for reservation in sorted(self.reservation_cache.values(), key=lambda item: item.get('resource', '')):
            payload['reservations'].append({
                'robot_id': reservation.get('robot_id'),
                'resource': reservation.get('resource'),
                'claim_id': reservation.get('claim_id'),
                'status': reservation.get('status'),
                'priority': reservation.get('priority'),
                'start_time': reservation.get('start_time'),
                'end_time': reservation.get('end_time'),
            })

        telemetry = String()
        telemetry.data = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        self.telemetry_publisher.publish(telemetry)


def main(args=None):
    rclpy.init(args=args)
    node = DashboardBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
