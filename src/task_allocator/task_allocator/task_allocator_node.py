#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node

from fleet_msgs.msg import RobotState, TaskAnnouncement, TaskBid


class TaskAllocatorNode(Node):
    def __init__(self):
        super().__init__('task_allocator_node')

        self.declare_parameter('robot_id', 'robot_a')
        self.declare_parameter('is_announcer', False)
        self.robot_id = self.get_parameter('robot_id').value.strip('/')
        self.is_announcer = self.get_parameter('is_announcer').value

        self.local_robot_state = {
            'robot_id': self.robot_id,
            'position': [0.0, 0.0],
            'battery': 100.0,
            'status': 'idle',
        }

        self.task_announcements = {}
        self.task_bids = {}
        self.bid_windows = {}

        self.announcement_publisher = self.create_publisher(TaskAnnouncement, '/tasks/announcements', 10)
        self.bid_publisher = self.create_publisher(TaskBid, '/tasks/bids', 10)

        self.create_subscription(TaskAnnouncement, '/tasks/announcements', self.handle_task_announcement, 10)
        self.create_subscription(TaskBid, '/tasks/bids', self.handle_task_bid, 10)

        for topic in ['/robot_a/state', '/robot_b/state', '/robot_c/state']:
            self.create_subscription(RobotState, topic, self.handle_robot_state, 10)

        if self.is_announcer:
            self.publish_test_task_announcement()

    def handle_robot_state(self, msg):
        """Keep a lightweight state cache for bid scoring."""
        if msg.robot_id == self.robot_id:
            self.local_robot_state = {
                'robot_id': msg.robot_id,
                'position': list(msg.position),
                'battery': float(msg.battery),
                'status': msg.status,
            }

    def publish_test_task_announcement(self):
        """Emit one hardcoded task announcement at startup for testing."""
        msg = TaskAnnouncement()
        msg.task_id = 'task_test_001'
        msg.pickup = 'dock_a'
        msg.dropoff = 'zone_b'
        msg.deadline = time.time() + 90.0
        msg.priority = 3
        msg.capability_requirements = ['delivery', 'navigation']
        self.announcement_publisher.publish(msg)
        self.get_logger().info(
            f'Published test task announcement: task_id={msg.task_id}, pickup={msg.pickup}, dropoff={msg.dropoff}'
        )

    def handle_task_announcement(self, msg):
        """When a task is announced, start the bid collection window and publish our bid."""
        task_id = msg.task_id
        self.task_announcements[task_id] = msg

        if task_id not in self.bid_windows:
            self.start_collection_window(task_id)

        if task_id in self.task_bids and self.robot_id in self.task_bids[task_id]:
            self.get_logger().info(f'Already bid for {task_id}; skipping duplicate bid.')
            return

        bid = self.compute_bid(msg)
        self.publish_bid(bid)

    def compute_bid(self, task_msg):
        """Simple placeholder bid estimate based on distance and battery."""
        estimated_time = 8.0 + task_msg.priority * 2.0
        distance = 12.0 + task_msg.priority * 3.0

        robot_position = self.local_robot_state.get('position', [0.0, 0.0])
        battery = self.local_robot_state.get('battery', 100.0)

        if isinstance(robot_position, (list, tuple)) and len(robot_position) >= 2:
            distance = max(1.0, abs(robot_position[0]) + abs(robot_position[1]) + 5.0)

        estimated_time = max(1.0, distance / 4.5)
        battery_cost = max(0.0, (100.0 - battery) / 40.0)
        confidence = 0.75 + (task_msg.priority / 10.0)

        bid = TaskBid()
        bid.robot_id = self.robot_id
        bid.task_id = task_msg.task_id
        bid.estimated_time = float(estimated_time)
        bid.distance = float(distance)
        bid.battery_cost = float(battery_cost)
        bid.confidence = float(min(0.99, confidence))
        return bid

    def publish_bid(self, bid):
        """Publish a computed bid for a task."""
        self.bid_publisher.publish(bid)
        self.task_bids.setdefault(bid.task_id, {})[self.robot_id] = bid
        self.get_logger().info(
            f'Published bid: robot_id={bid.robot_id}, task_id={bid.task_id}, '
            f'estimated_time={bid.estimated_time:.2f}, distance={bid.distance:.2f}, '
            f'battery_cost={bid.battery_cost:.2f}, confidence={bid.confidence:.2f}'
        )

    def handle_task_bid(self, msg):
        """Store incoming bids; the collection window is already anchored to the announcement."""
        task_id = msg.task_id
        self.task_bids.setdefault(task_id, {})[msg.robot_id] = msg

    def start_collection_window(self, task_id):
        """Collect all bids for a short collection window before determining the winner."""

        def _resolve_after_window():
            self.determine_winner(task_id)
            collection_timer.cancel()
            self.bid_windows.pop(task_id, None)

        if task_id not in self.bid_windows:
            collection_timer = self.create_timer(2.0, _resolve_after_window)
            self.bid_windows[task_id] = collection_timer

    def determine_winner(self, task_id):
        """Every robot independently chooses the lowest-time winner, tie-break by robot_id."""
        bids = self.task_bids.get(task_id, {})
        if not bids:
            return

        winner = min(
            bids.values(),
            key=lambda bid: (bid.estimated_time, bid.robot_id),
        )

        if winner.robot_id == self.robot_id:
            self.get_logger().info(f'TASK WON: {task_id}')
        else:
            self.get_logger().info(f'TASK LOST: {task_id} to {winner.robot_id}')


def main(args=None):
    rclpy.init(args=args)
    node = TaskAllocatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
