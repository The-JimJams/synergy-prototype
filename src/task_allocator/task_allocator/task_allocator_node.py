#!/usr/bin/env python3
"""
Task Allocator Node — integration/ros2-nav2 + P5 integration.

Changes from previous version:
- P5 TaskManager used for capability-based eligibility check before executing won tasks.
- P5 HeartbeatMonitor + FailureDetector watch /amr_a/heartbeat.
- P5 TaskRecoveryManager re-queues tasks if a robot is detected as FAILED.
- All existing ROS 2 announcement/bidding/Nav2 pipelines are UNCHANGED.
"""

import sys
import os
import time
from datetime import datetime, timezone

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

from fleet_msgs.msg import RobotState, TaskAnnouncement, TaskBid, Heartbeat

# ---------------------------------------------------------------------------
# P5 imports — try multiple candidate paths so this works both locally
# and inside the Docker container at /workspace/synergy-prototype
# ---------------------------------------------------------------------------
_P5_CANDIDATES = [
    # Docker container path
    '/workspace/synergy-prototype/p5_task_failure',
    # Local host path (relative from installed package location)
    os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'p5_task_failure')),
]
for _p5_path in _P5_CANDIDATES:
    if os.path.isdir(_p5_path) and _p5_path not in sys.path:
        sys.path.insert(0, _p5_path)

try:
    from p5.models.robot import Robot, RobotStatus
    from p5.models.task import Task, TaskStatus
    from p5.manager.task_manager import TaskManager
    from p5.failure.heartbeat import HeartbeatMonitor
    from p5.failure.detector import FailureDetector
    from p5.recovery.task_recovery import TaskRecoveryManager
    from p5.models.heartbeat import Heartbeat as P5Heartbeat, HeartbeatStatus
    P5_AVAILABLE = True
except ImportError as e:
    P5_AVAILABLE = False
    # Define stubs so type hints don't cause NameErrors at runtime
    Robot = None
    RobotStatus = None
    Task = None
    TaskStatus = None

# Warehouse coordinate map: task pickup locations (strings → (x, y))
PICKUP_COORDS = {
    'dock_a':  (-3.5, 5.25),
    'dock_b':  (0.0,  8.0),
    'default': (-3.5, 5.25),
}
DROPOFF_COORDS = {
    'zone_b':  (0.0, -8.1),
    'zone_a':  (0.0,  8.0),
    'default': (0.0, -8.1),
}

# Failure timeout: if no heartbeat seen for this many seconds, robot is FAILED
HEARTBEAT_TIMEOUT_SEC = 10.0


class TaskAllocatorNode(Node):
    def __init__(self):
        super().__init__('task_allocator_node')

        self.declare_parameter('robot_id', 'amr_a')
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

        # Track active P5 Task objects so we can recover them on failure
        self._p5_active_tasks: dict[str, 'Task'] = {}  # task_id -> P5 Task
        self._p5_robot: 'Robot | None' = None

        # ---- ROS 2 pub/sub ----
        self.announcement_publisher = self.create_publisher(TaskAnnouncement, '/tasks/announcements', 10)
        self.bid_publisher = self.create_publisher(TaskBid, '/tasks/bids', 10)

        self.create_subscription(TaskAnnouncement, '/tasks/announcements', self.handle_task_announcement, 10)
        self.create_subscription(TaskBid, '/tasks/bids', self.handle_task_bid, 10)

        for topic in ['/amr_a/state', '/amr_b/state', '/amr_c/state']:
            self.create_subscription(RobotState, topic, self.handle_robot_state, 10)

        # Subscribe to heartbeat topics to feed P5 HeartbeatMonitor
        for topic in ['/amr_a/heartbeat', '/amr_b/heartbeat', '/amr_c/heartbeat']:
            self.create_subscription(
                Heartbeat, topic,
                lambda msg, t=topic: self._on_heartbeat(msg, t),
                10
            )

        # Nav2 Action Client
        self.nav_client = ActionClient(self, NavigateToPose, f'/{self.robot_id}/navigate_to_pose')

        # ---- P5 components ----
        if P5_AVAILABLE:
            self._p5_task_manager = TaskManager()
            self._p5_heartbeat_monitor = HeartbeatMonitor()
            self._p5_failure_detector = FailureDetector(timeout_seconds=HEARTBEAT_TIMEOUT_SEC)
            self._p5_recovery_manager = TaskRecoveryManager()
            # Periodic failure check every 5 seconds
            self.create_timer(5.0, self._check_for_failures)
            self.get_logger().info('P5 integration ACTIVE: TaskManager, FailureDetector, TaskRecoveryManager ready.')
        else:
            self.get_logger().warning(f'P5 not available — running without failure detection.')

        if self.is_announcer:
            self.publish_test_task_announcement()

    # ------------------------------------------------------------------
    # ROS 2 state / heartbeat callbacks
    # ------------------------------------------------------------------

    def handle_robot_state(self, msg):
        """Keep a lightweight state cache for bid scoring."""
        if msg.robot_id == self.robot_id:
            self.local_robot_state = {
                'robot_id': msg.robot_id,
                'position': [msg.x, msg.y],
                'battery': float(msg.battery_percent),
                'status': msg.status,
            }

    def _on_heartbeat(self, ros_msg: Heartbeat, topic: str):
        """Feed ROS 2 heartbeat into P5 HeartbeatMonitor."""
        if not P5_AVAILABLE:
            return
        p5_hb = P5Heartbeat(
            robot_id=ros_msg.robot_id,
            timestamp=datetime.fromtimestamp(ros_msg.timestamp, tz=timezone.utc),
            status=HeartbeatStatus.ALIVE,
        )
        self._p5_heartbeat_monitor.register(p5_hb)

    # ------------------------------------------------------------------
    # Task announcement / bidding (UNCHANGED)
    # ------------------------------------------------------------------

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
        robot_position = self.local_robot_state.get('position', [0.0, 0.0])
        battery = self.local_robot_state.get('battery', 100.0)

        if isinstance(robot_position, (list, tuple)) and len(robot_position) >= 2:
            distance = max(1.0, abs(robot_position[0]) + abs(robot_position[1]) + 5.0)
        else:
            distance = 12.0 + task_msg.priority * 3.0

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
            self.execute_task(task_id)
        else:
            self.get_logger().info(f'TASK LOST: {task_id} to {winner.robot_id}')

    # ------------------------------------------------------------------
    # Task execution — P5 capability check then Nav2 goal
    # ------------------------------------------------------------------

    def execute_task(self, task_id):
        """Validate eligibility via P5, then send a Nav2 NavigateToPose goal."""
        announcement = self.task_announcements.get(task_id)

        # Build P5 Robot from current state
        p5_robot = self._build_p5_robot()
        self._p5_robot = p5_robot

        # Build P5 Task from announcement
        p5_task = self._build_p5_task(task_id, announcement)

        # P5 capability check
        if P5_AVAILABLE:
            result = self._p5_task_manager.capability_checker.check(p5_robot, p5_task)
            if not result.eligible:
                self.get_logger().warning(
                    f'P5 capability check FAILED for {task_id}: {result.reasons} — task not executed.'
                )
                return
            self.get_logger().info(f'P5 capability check PASSED for {task_id}')

            # Mark task as ASSIGNED in P5
            p5_task.status = TaskStatus.ASSIGNED
            p5_task.assigned_robot = self.robot_id
            self._p5_active_tasks[task_id] = p5_task
            p5_robot.status = RobotStatus.BUSY
            p5_robot.current_task = task_id

        self.get_logger().info(f'Executing task {task_id} via Nav2')
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Nav2 Action Server not available!')
            return

        # Resolve destination coordinates
        pickup_key = announcement.pickup if announcement else 'default'
        dropoff_key = announcement.dropoff if announcement else 'default'
        goal_x, goal_y = DROPOFF_COORDS.get(dropoff_key, DROPOFF_COORDS['default'])

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = goal_x
        goal_msg.pose.pose.position.y = goal_y
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Sending Nav2 goal to x: {goal_x}, y: {goal_y}')
        self._send_goal_future = self.nav_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(
            lambda f, tid=task_id: self.goal_response_callback(f, tid)
        )

    def goal_response_callback(self, future, task_id):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Nav2 goal rejected')
            return

        self.get_logger().info('Nav2 goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(
            lambda f, tid=task_id: self.get_result_callback(f, tid)
        )

    def get_result_callback(self, future, task_id):
        status = future.result().status
        self.get_logger().info(f'Nav2 goal finished with status: {status}')

        # status == 4 means SUCCEEDED in ROS 2 action status
        if P5_AVAILABLE and task_id in self._p5_active_tasks:
            p5_task = self._p5_active_tasks[task_id]
            if status == 4:
                p5_task.status = TaskStatus.COMPLETED
                self.get_logger().info(f'P5: task {task_id} marked COMPLETED')
                if self._p5_robot:
                    self._p5_robot.status = RobotStatus.AVAILABLE
                    self._p5_robot.current_task = None
            else:
                p5_task.status = TaskStatus.FAILED
                self.get_logger().warning(f'P5: task {task_id} marked FAILED (Nav2 status={status})')

    # ------------------------------------------------------------------
    # P5 Failure Detection & Recovery
    # ------------------------------------------------------------------

    def _check_for_failures(self):
        """Periodic check: detect robot failures and recover active tasks."""
        if not P5_AVAILABLE or self._p5_robot is None:
            return

        latest_hb = self._p5_heartbeat_monitor.get_latest(self.robot_id)
        now = datetime.now(timezone.utc)

        failed = self._p5_failure_detector.detect(self._p5_robot, latest_hb, now)

        if failed:
            self.get_logger().warning(f'P5: FAILURE DETECTED for {self.robot_id}')
            # Recover all active tasks assigned to this robot
            for task_id, p5_task in list(self._p5_active_tasks.items()):
                if p5_task.assigned_robot == self.robot_id:
                    self.get_logger().warning(f'P5: recovering task {task_id}')
                    self._p5_recovery_manager.recover(p5_task, self._p5_robot)
                    # Re-announce the recovered task so another robot can bid
                    self._reannounce_task(task_id, p5_task)

    def _reannounce_task(self, task_id: str, p5_task: 'Task'):
        """Re-publish a recovered task as a new ROS 2 announcement."""
        original = self.task_announcements.get(task_id)
        if original is None:
            self.get_logger().warning(f'Cannot re-announce {task_id}: original announcement not found')
            return

        recovered_id = f'{task_id}_recovery_{int(time.time())}'
        msg = TaskAnnouncement()
        msg.task_id = recovered_id
        msg.pickup = original.pickup
        msg.dropoff = original.dropoff
        msg.deadline = time.time() + 90.0
        msg.priority = original.priority + 1  # bump priority for recovered tasks
        msg.capability_requirements = list(original.capability_requirements)

        self.announcement_publisher.publish(msg)
        self.get_logger().info(
            f'P5 RECOVERY: re-announced task as {recovered_id} (original: {task_id})'
        )

        p5_task.status = TaskStatus.ANNOUNCED
        # Remove from active tracking so it can be re-assigned
        self._p5_active_tasks.pop(task_id, None)

    # ------------------------------------------------------------------
    # P5 helpers — build internal models from ROS state
    # ------------------------------------------------------------------

    def _build_p5_robot(self) -> 'Robot':
        pos = self.local_robot_state.get('position', [0.0, 0.0])
        battery = self.local_robot_state.get('battery', 100.0)
        ros_status = self.local_robot_state.get('status', 'IDLE').upper()

        # Map ROS status strings to P5 RobotStatus
        status_map = {
            'IDLE': RobotStatus.AVAILABLE,
            'NAVIGATING': RobotStatus.BUSY,
            'CHARGING': RobotStatus.CHARGING,
            'FAILED': RobotStatus.FAILED,
        }
        p5_status = status_map.get(ros_status, RobotStatus.AVAILABLE)

        return Robot(
            robot_id=self.robot_id,
            position=(float(pos[0]), float(pos[1])),
            battery=float(battery),
            payload_capacity=500.0,
            current_task=None,
            workload=0,
            status=p5_status,
            capabilities=('CARRY', 'navigation', 'delivery'),
        )

    def _build_p5_task(self, task_id: str, announcement) -> 'Task':
        if announcement is not None:
            pickup_key = announcement.pickup
            dropoff_key = announcement.dropoff
            priority = int(announcement.priority)
            required_caps = tuple(announcement.capability_requirements)
        else:
            pickup_key = 'default'
            dropoff_key = 'default'
            priority = 3
            required_caps = ('delivery', 'navigation')

        pickup_xy = PICKUP_COORDS.get(pickup_key, PICKUP_COORDS['default'])
        dropoff_xy = DROPOFF_COORDS.get(dropoff_key, DROPOFF_COORDS['default'])

        return Task(
            task_id=task_id,
            pickup_location=pickup_xy,
            dropoff_location=dropoff_xy,
            priority=priority,
            deadline=time.time() + 90.0,
            required_payload=50.0,
            status=TaskStatus.ASSIGNED,
            assigned_robot=None,
            required_capabilities=required_caps,
        )


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
