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
import math
from datetime import datetime, timezone

try:
    import rclpy
    from rclpy.node import Node
    from rclpy.action import ActionClient
    from nav2_msgs.action import NavigateToPose
    from geometry_msgs.msg import PoseStamped
    from fleet_msgs.msg import RobotState, TaskAnnouncement, TaskBid, Heartbeat, ResourceClaim
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False
    Node = object
    ActionClient = object

    class NavigateToPose:
        class Goal:
            def __init__(self):
                class Header:
                    frame_id = 'map'
                    stamp = 0
                class PoseObj:
                    class Pos:
                        x, y, z = 0.0, 0.0, 0.0
                    class Ori:
                        w = 1.0
                    position = Pos()
                    orientation = Ori()
                self.header = Header()
                self.pose = PoseObj()

    class PoseStamped: pass
    class RobotState:
        robot_id, x, y, theta = '', 0.0, 0.0, 0.0
        linear_velocity, angular_velocity, battery_percent = 0.0, 0.0, 100.0
        status, current_task_id = 'IDLE', ''
    class TaskAnnouncement:
        task_id, pickup, dropoff = '', '', ''
        priority, deadline = 1, 0.0
        capability_requirements = []
    class TaskBid:
        robot_id, task_id = '', ''
        estimated_time, distance, battery_cost, confidence = 0.0, 0.0, 0.0, 1.0
    class Heartbeat:
        robot_id, timestamp = '', 0.0
    class ResourceClaim:
        robot_id, resource, claim_id, status = '', '', '', ''
        start_time, end_time = 0.0, 0.0
        priority = 0

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

# ---------------------------------------------------------------------------
# Warehouse waypoints — GROUND TRUTH from gazebo/simulation/worlds/warehouse.sdf
#
# These are Nav2 goal poses, so every entry must be a pose the robot can
# actually occupy, verified against src/synergy_nav2/maps/warehouse_map.pgm:
#
#   * Station entries are the station pads' own coordinates, except P2 — in the
#     world, pallet_tower_1 (-5.2, -7.3) sits on top of the P2 pad, so P2 uses
#     the clear north-west corner of the pad instead.
#   * Shelf entries S1-S8 are AISLE APPROACH poses, not rack centres.  A rack
#     centre is inside a 5.0 x 1.0 x 2.2 m solid and is not a reachable goal.
#     Racks stand at x = -4.8 / +4.8, y = 7.5 / 3.0 / 1.5 / -3.0.
#
# Every pose below has >= 0.60 m clearance to the nearest occupied cell
# (robot inscribed radius 0.26 m, circumscribed 0.405 m, inflation 0.55 m) and
# is reachable from all three spawn poses.
# ---------------------------------------------------------------------------
WAYPOINTS = {
    # Stations
    'P1': (0.0, 8.0),     'p1': (0.0, 8.0),        # pickup_P1
    'P2': (-6.4, -6.3),   'p2': (-6.4, -6.3),      # pickup_P2 pad, clear corner
    'D1': (0.0, -8.1),    'd1': (0.0, -8.1),       # drop_pack_D1
    'CHG': (5.5, -7.5),   'chg': (5.5, -7.5),      # charging_bay
    # Shared intersections (bollard-flanked chokepoints)
    'I1': (0.0, 5.2),     'i1': (0.0, 5.2),
    'I2': (0.0, -0.7),    'i2': (0.0, -0.7),
    # High-bay shelving racks S1 - S8 — aisle-side approach poses
    'S1': (-4.8, 6.0),    's1': (-4.8, 6.0),       # rack (-4.8,  7.5), aisle S
    'S2': (4.8, 6.0),     's2': (4.8, 6.0),        # rack ( 4.8,  7.5), aisle S
    'S3': (-4.8, 4.3),    's3': (-4.8, 4.3),       # rack (-4.8,  3.0), aisle N
    'S4': (4.8, 4.3),     's4': (4.8, 4.3),        # rack ( 4.8,  3.0), aisle N
    'S5': (-4.8, 0.0),    's5': (-4.8, 0.0),       # rack (-4.8,  1.5), aisle S
    'S6': (4.8, 0.0),     's6': (4.8, 0.0),        # rack ( 4.8,  1.5), aisle S
    'S7': (-4.8, -4.5),   's7': (-4.8, -4.5),      # rack (-4.8, -3.0), aisle S
    'S8': (4.8, -4.5),    's8': (4.8, -4.5),       # rack ( 4.8, -3.0), aisle S
    # Spawn docks / legacy aliases
    'dock_a': (-3.5, 5.25),   # amr_blue spawn
    'dock_b': (0.5, 8.5),     # amr_green spawn
    'dock_c': (3.5, -6.5),    # amr_orange spawn
    'zone_a': (0.0, 8.0),
    'zone_b': (0.0, -8.1),
    'default': (0.0, -8.1),
}

# Where each AMR waits when it has nothing to do. A robot that simply stops on
# the pad it just delivered to leaves its own footprint sitting on the next
# task's goal: the following delivery then fails to plan at all, because NavFn
# refuses a goal whose cell is lethal. Clearing to a dock keeps the stations and
# the corridor usable.
STANDBY_DOCKS = {
    'amr_a': (-3.5, 5.25),
    'amr_b': (0.5, 8.5),
    'amr_c': (3.5, -6.5),
}

# Failure timeout: if no heartbeat seen for this many seconds, robot is FAILED
HEARTBEAT_TIMEOUT_SEC = 10.0


class TaskAllocatorNode(Node):
    def __init__(self):
        if ROS2_AVAILABLE:
            super().__init__('task_allocator_node')
            self.declare_parameter('robot_id', 'amr_a')
            self.declare_parameter('is_announcer', False)
            self.declare_parameter('nav_enabled', True)
            self.declare_parameter('bidding_window_sec', 0.5)
            self.robot_id = self.get_parameter('robot_id').value.strip('/')
            self.is_announcer = self.get_parameter('is_announcer').value
            self.nav_enabled = bool(self.get_parameter('nav_enabled').value)
            self.bidding_window_sec = float(self.get_parameter('bidding_window_sec').value)
        else:
            self.robot_id = 'amr_a'
            self.is_announcer = False
            self.nav_enabled = True
            self.bidding_window_sec = 0.5
            class MockLogger:
                def info(self, msg): pass
                def warning(self, msg): pass
                def error(self, msg): pass
            self._logger = MockLogger()
            self.get_logger = lambda: self._logger

        self.local_robot_state = {
            'robot_id': self.robot_id,
            'position': [0.0, 0.0],
            'battery': 100.0,
            'status': 'idle',
        }

        self.task_announcements = {}
        self.task_bids = {}
        self.bid_windows = {}
        self._announcement_times = {}

        # Track active P5 Task objects so we can recover them on failure
        self._p5_active_tasks: dict[str, 'Task'] = {}  # task_id -> P5 Task
        self._p5_robot: 'Robot | None' = None
        # Base ids already released by failure recovery, so the periodic check
        # re-announces a given task once instead of once every 5 s forever.
        self._recovered_task_ids: set[str] = set()
        self._failure_announced = False

        # ---- ROS 2 pub/sub ----
        if ROS2_AVAILABLE:
            self.announcement_publisher = self.create_publisher(TaskAnnouncement, '/tasks/announcements', 10)
            self.bid_publisher = self.create_publisher(TaskBid, '/tasks/bids', 10)
            # The winner announces its own claim. Every peer already computed the
            # same winner independently; this only makes the outcome observable
            # so monitors do not have to re-derive it (and so the dashboard never
            # has to pick a winner itself to display one).
            self.claim_publisher = self.create_publisher(ResourceClaim, '/fleet/reservations', 10)

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

            # Nav2 Action Client. In the current demo only AMR A has a Nav2 stack,
            # so other robots must not win navigation tasks they cannot execute.
            if self.nav_enabled:
                self.nav_client = ActionClient(self, NavigateToPose, f'/{self.robot_id}/navigate_to_pose')
            else:
                self.nav_client = None
                self.get_logger().info(
                    f'Navigation disabled for {self.robot_id}; this allocator will observe tasks without bidding.'
                )
        else:
            class MockPub:
                def publish(self, msg): pass
            self.announcement_publisher = MockPub()
            self.bid_publisher = MockPub()
            self.claim_publisher = MockPub()
            self.nav_client = None

        # ---- P5 components ----
        if P5_AVAILABLE:
            self._p5_task_manager = TaskManager()
            self._p5_heartbeat_monitor = HeartbeatMonitor()
            self._p5_failure_detector = FailureDetector(timeout_seconds=HEARTBEAT_TIMEOUT_SEC)
            self._p5_recovery_manager = TaskRecoveryManager()
            self.demo_task_count = 1
            # Periodic failure check every 5 seconds
            if ROS2_AVAILABLE:
                self.create_timer(5.0, self._check_for_failures)
            self.get_logger().info('P5 integration ACTIVE: TaskManager, FailureDetector, TaskRecoveryManager ready.')
        else:
            self.get_logger().warning(f'P5 not available — running without failure detection.')

        if self.is_announcer and ROS2_AVAILABLE:
            self._startup_announcement_timer = self.create_timer(3.0, self._publish_startup_task_once)

    def _publish_startup_task_once(self):
        self.publish_test_task_announcement()
        self._startup_announcement_timer.cancel()

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
        """When a task is announced, start the bid collection window, verify eligibility, and publish our bid."""
        task_id = msg.task_id
        t_announce = time.time()
        self._announcement_times[task_id] = t_announce
        self.task_announcements[task_id] = msg

        if task_id not in self.bid_windows:
            self.start_collection_window(task_id)

        if not self.nav_enabled:
            self.get_logger().info(f'Observed {task_id}; skipping bid because Nav2 is disabled for {self.robot_id}.')
            return

        # A robot whose own heartbeat has stopped must not take new work --
        # including the task its own failure just released. Checked here rather
        # than only on the P5 Robot object because _build_p5_robot() rebuilds
        # that object from live ROS state on every announcement and would
        # otherwise clear the FAILED status set by _check_for_failures().
        if self._failure_announced:
            self.get_logger().warning(
                f'ELIGIBILITY: robot={self.robot_id}, task={task_id}, eligible=False, '
                f"reasons=['SELF_FAILED_HEARTBEAT_LOST'] — skipping bid."
            )
            return

        if task_id in self.task_bids and self.robot_id in self.task_bids[task_id]:
            self.get_logger().info(f'Already bid for {task_id}; skipping duplicate bid.')
            return

        # Pre-bid eligibility / capability filtering
        eligible = True
        reasons = []
        if P5_AVAILABLE:
            p5_robot = self._build_p5_robot()
            self._p5_robot = p5_robot
            p5_task = self._build_p5_task(task_id, msg)
            res = self._p5_task_manager.capability_checker.check(p5_robot, p5_task)
            eligible = res.eligible
            reasons = list(res.reasons)

        if not eligible:
            self.get_logger().info(
                f'ELIGIBILITY: robot={self.robot_id}, task={task_id}, eligible=False, reasons={reasons} — skipping bid.'
            )
            return

        self.get_logger().info(f'ELIGIBILITY: robot={self.robot_id}, task={task_id}, eligible=True')

        t_calc_start = time.perf_counter()
        bid = self.compute_bid(msg)
        calc_ms = (time.perf_counter() - t_calc_start) * 1000.0

        self.get_logger().info(
            f'BID_CALCULATION: robot={self.robot_id}, task={task_id}, eligible=True, '
            f'bid_val={bid.estimated_time:.2f}s, dist={bid.distance:.2f}m, batt={bid.battery_cost:.2f}, '
            f'calc_time_ms={calc_ms:.3f}ms'
        )
        self.publish_bid(bid)

    def compute_bid(self, task_msg):
        """Calculate bid estimate based on distance to pickup landmark and battery."""
        robot_position = self.local_robot_state.get('position', [0.0, 0.0])
        battery = self.local_robot_state.get('battery', 100.0)

        pickup_coords = WAYPOINTS.get(task_msg.pickup, WAYPOINTS.get('P1', (-7.2, 0.0)))
        if isinstance(robot_position, (list, tuple)) and len(robot_position) >= 2:
            distance = math.hypot(robot_position[0] - pickup_coords[0], robot_position[1] - pickup_coords[1])
        else:
            distance = 12.0 + task_msg.priority * 3.0

        # Physical estimation: 0.6 m/s max velocity
        estimated_time = max(1.0, distance / 0.6)
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
        if P5_AVAILABLE and self._p5_robot:
            if getattr(self._p5_robot.status, 'name', '') in ('FAILED', 'CHARGING'):
                self.get_logger().warning(f'Skipping bid for {bid.task_id} because robot status is {self._p5_robot.status.name}')
                return

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
        """Collect all bids for the window before deterministically selecting the winner."""
        def _resolve_after_window():
            self.determine_winner(task_id)
            collection_timer.cancel()
            self.bid_windows.pop(task_id, None)

        if task_id not in self.bid_windows:
            collection_timer = self.create_timer(self.bidding_window_sec, _resolve_after_window)
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

        t_winner = time.time()
        t_announced = self._announcement_times.get(task_id, t_winner)
        window_latency_s = t_winner - t_announced

        self.get_logger().info(
            f'WINNER_SELECTION: task={task_id}, winner={winner.robot_id}, winning_bid={winner.estimated_time:.2f}s, '
            f'total_bids={len(bids)}, window_latency_s={window_latency_s:.3f}s'
        )
        self.get_logger().info(f'WINNER: {winner.robot_id}')
        if winner.robot_id == self.robot_id:
            self.get_logger().info(f'TASK WON: {task_id}')
            self._publish_claim(task_id, 'CLAIMED')
            self.execute_task(task_id)
        else:
            self.get_logger().info(f'TASK LOST: {task_id} to {winner.robot_id}')

    # ------------------------------------------------------------------
    # Task execution — P5 capability check then Nav2 goal
    # ------------------------------------------------------------------

    def execute_task(self, task_id):
        """Validate eligibility via P5, then send a Nav2 NavigateToPose goal."""
        if not self.nav_enabled or self.nav_client is None:
            self.get_logger().warning(f'Cannot execute {task_id}: Nav2 is disabled for {self.robot_id}.')
            return

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
        self.get_logger().info('Waiting for Nav2 action server...')
        if not self.nav_client.wait_for_server(timeout_sec=30.0):
            self.get_logger().error('Nav2 Action Server not available after 30s!')
            # Reset robot back to AVAILABLE so it can accept the next task attempt
            if P5_AVAILABLE and self._p5_robot:
                self._p5_robot.status = RobotStatus.AVAILABLE
                self._p5_robot.current_task = None
            if task_id in self._p5_active_tasks:
                self._p5_active_tasks.pop(task_id, None)
            return

        # Resolve pickup and dropoff coordinates
        pickup_key = announcement.pickup if announcement else 'P1'
        dropoff_key = announcement.dropoff if announcement else 'D1'
        pickup_x, pickup_y = WAYPOINTS.get(pickup_key, WAYPOINTS['P1'])
        dropoff_x, dropoff_y = WAYPOINTS.get(dropoff_key, WAYPOINTS['D1'])

        self.get_logger().info(f'PICKUP_GOAL: {pickup_key} ({pickup_x}, {pickup_y})')
        self._send_nav2_goal(
            pickup_x, pickup_y, task_id,
            phase='PICKUP',
            next_coords=(dropoff_x, dropoff_y, dropoff_key)
        )

    def _send_nav2_goal(self, goal_x, goal_y, task_id, phase, next_coords=None):
        """Send a single NavigateToPose goal with phase tracking."""
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(goal_x)
        goal_msg.pose.pose.position.y = float(goal_y)
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Sending Nav2 goal ({phase}) to x: {goal_x}, y: {goal_y}')
        send_future = self.nav_client.send_goal_async(goal_msg)
        send_future.add_done_callback(
            lambda f, tid=task_id, ph=phase, nc=next_coords: self.goal_response_callback(f, tid, ph, nc)
        )

    def _publish_claim(self, task_id: str, status: str) -> None:
        """Announce this robot's own claim on a task it won, or its release."""
        if not ROS2_AVAILABLE:
            return
        msg = ResourceClaim()
        msg.robot_id = self.robot_id
        msg.resource = task_id
        msg.claim_id = f'{self.robot_id}:{task_id}'
        msg.status = status
        msg.start_time = time.time()
        msg.end_time = 0.0
        ann = self.task_announcements.get(task_id)
        msg.priority = int(getattr(ann, 'priority', 0) or 0)
        self.claim_publisher.publish(msg)

    def _return_to_standby(self) -> None:
        """Clear the delivery pad after finishing, so it stays navigable."""
        dock = STANDBY_DOCKS.get(self.robot_id)
        if dock is None or not self.nav_enabled or self.nav_client is None:
            return
        self.get_logger().info(f'STANDBY: {self.robot_id} clearing the pad, returning to {dock}')
        self._send_nav2_goal(dock[0], dock[1], f'{self.robot_id}_standby', phase='STANDBY')

    def _release_task(self, task_id: str, reason: str) -> None:
        """Return this robot to the auction after a task stops making progress.

        _build_p5_robot() reports BUSY while _p5_active_tasks is non-empty, and
        the capability check refuses to bid for a BUSY robot. Only the success
        and nav-server-timeout paths used to clear the entry, so a single
        aborted or rejected Nav2 goal pinned the robot BUSY for the rest of the
        process: every later announcement was answered with
        ROBOT_UNAVAILABLE and the robot never bid again. Observed live with all
        three AMRs simultaneously unavailable and tasks stuck at ANNOUNCED.
        """
        self._p5_active_tasks.pop(task_id, None)
        self._publish_claim(task_id, 'RELEASED')
        if P5_AVAILABLE and self._p5_robot is not None:
            if getattr(self._p5_robot.status, 'name', '') != 'FAILED':
                self._p5_robot.status = RobotStatus.AVAILABLE
            self._p5_robot.current_task = None
        self.get_logger().info(
            f'TASK_RELEASED: {task_id} ({reason}); {self.robot_id} is available for bidding again.'
        )

    def goal_response_callback(self, future, task_id, phase, next_coords):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning(f'NAV2_STATUS: REJECTED ({phase} for {task_id})')
            if phase != 'STANDBY':
                self._release_task(task_id, f'Nav2 rejected the {phase} goal')
            return

        self.get_logger().info(f'NAV2_STATUS: ACCEPTED ({phase} for {task_id})')
        self.get_logger().info('ROBOT_MOVING: TRUE')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f, tid=task_id, ph=phase, nc=next_coords: self.get_result_callback(f, tid, ph, nc)
        )

    def get_result_callback(self, future, task_id, phase, next_coords):
        status = future.result().status
        self.get_logger().info(f'Nav2 goal ({phase}) finished with status: {status}')

        if phase == 'STANDBY':
            self.get_logger().info(f'STANDBY: {self.robot_id} parked (status={status})')
            return

        # status == 4 means SUCCEEDED in ROS 2 action status
        if status == 4:
            if phase == 'PICKUP':
                self.get_logger().info(f'PICKUP_REACHED: TRUE for {task_id}')
                if P5_AVAILABLE and task_id in self._p5_active_tasks:
                    self._p5_active_tasks[task_id].status = TaskStatus.IN_PROGRESS
                    self.get_logger().info(f'P5: task {task_id} marked IN_PROGRESS')

                if next_coords:
                    dropoff_x, dropoff_y, dropoff_key = next_coords
                    self.get_logger().info(f'DROPOFF_GOAL: {dropoff_key} ({dropoff_x}, {dropoff_y})')
                    self._send_nav2_goal(dropoff_x, dropoff_y, task_id, phase='DROPOFF', next_coords=None)
            else:
                self.get_logger().info(f'DROPOFF_REACHED: TRUE for {task_id}')
                self.get_logger().info(f'TASK_COMPLETED: {task_id}')
                self._publish_claim(task_id, 'COMPLETED')
                self._return_to_standby()
                if P5_AVAILABLE and task_id in self._p5_active_tasks:
                    p5_task = self._p5_active_tasks[task_id]
                    p5_task.status = TaskStatus.COMPLETED
                    self.get_logger().info(f'P5: task {task_id} marked COMPLETED')
                    if self._p5_robot:
                        self._p5_robot.status = RobotStatus.AVAILABLE
                        self._p5_robot.current_task = None

                    self._p5_active_tasks.pop(task_id, None)
        else:
            if P5_AVAILABLE and task_id in self._p5_active_tasks:
                self._p5_active_tasks[task_id].status = TaskStatus.FAILED
                self.get_logger().warning(f'P5: task {task_id} marked FAILED at phase {phase} (status={status})')
            self._release_task(task_id, f'Nav2 {phase} goal ended with status {status}')

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
        if latest_hb:
            self.get_logger().info(f'P5 Debug: now={now.timestamp()}, hb={latest_hb.timestamp.timestamp()}, diff={(now - latest_hb.timestamp).total_seconds()}s')
        else:
            self.get_logger().info('P5 Debug: NO HEARTBEAT RECEIVED YET!')

        if failed:
            # Mark the robot FAILED so publish_bid()'s existing guard stops it
            # bidding. Without this a robot whose heartbeat had stopped kept
            # bidding on -- and winning, because it is closest -- the very task
            # its own failure had just released, so recovery never handed the
            # work to a healthy peer.
            self._p5_robot.status = RobotStatus.FAILED

            if not self._failure_announced:
                self.get_logger().warning(f'P5: FAILURE DETECTED for {self.robot_id}')
                self._failure_announced = True

            # Recover all active tasks assigned to this robot
            for task_id, p5_task in list(self._p5_active_tasks.items()):
                if p5_task.assigned_robot == self.robot_id:
                    self.get_logger().warning(f'P5: recovering task {task_id}')
                    self._p5_recovery_manager.recover(p5_task, self._p5_robot)
                    # Re-announce the recovered task so another robot can bid
                    self._reannounce_task(task_id, p5_task)
        else:
            # Heartbeat is back: allow this robot to take work again.
            if self._failure_announced:
                self.get_logger().info(f'P5: {self.robot_id} heartbeat recovered; returning to service')
                self._failure_announced = False
                if getattr(self._p5_robot.status, 'name', '') == 'FAILED':
                    self._p5_robot.status = RobotStatus.AVAILABLE

    def _reannounce_task(self, task_id: str, p5_task: 'Task'):
        """Re-publish a recovered task as a new ROS 2 announcement."""
        original = self.task_announcements.get(task_id)
        if original is None:
            self.get_logger().warning(f'Cannot re-announce {task_id}: original announcement not found')
            return

        # Recover from the ORIGINAL task id, never from an already-recovered one.
        # This check runs every 5 s and a genuinely dead robot never recovers, so
        # appending to the previous id grew it without bound: observed in a live
        # run as T_NODASH_recovery_<ts>_recovery_<ts>... 40 suffixes deep and
        # still growing, one re-announcement every 5 s.
        base_id = task_id.split('_recovery_')[0]
        if base_id in self._recovered_task_ids:
            return
        self._recovered_task_ids.add(base_id)
        recovered_id = f'{base_id}_recovery_{int(time.time())}'
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
        if len(self._p5_active_tasks) > 0:
            p5_status = RobotStatus.BUSY

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

        pickup_xy = WAYPOINTS.get(pickup_key, WAYPOINTS['default'])
        dropoff_xy = WAYPOINTS.get(dropoff_key, WAYPOINTS['default'])

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


    def _announce_next_demo_task(self, prev_task_id):
        self.demo_task_count += 1
        msg = TaskAnnouncement()
        msg.task_id = f'task_demo_{self.demo_task_count:03d}'

        prev_ann = self.task_announcements.get(prev_task_id)
        if prev_ann and 'zone_b' in prev_ann.dropoff:
            msg.pickup = 'zone_b'
            msg.dropoff = 'dock_a'
        else:
            msg.pickup = 'dock_a'
            msg.dropoff = 'zone_b'

        import time
        msg.deadline = time.time() + 90.0
        msg.priority = 3
        msg.capability_requirements = ['delivery', 'navigation']
        self.announcement_publisher.publish(msg)
        self.get_logger().info(f'Published NEXT demo task announcement: {msg.task_id} to {msg.dropoff}')

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
