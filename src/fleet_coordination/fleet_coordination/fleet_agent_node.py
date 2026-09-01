#!/usr/bin/env python3
"""ROS 2 fleet agent node for state, heartbeat, intent, and reservation conflict handling."""

import random

import rclpy
from rclpy.node import Node

from fleet_msgs.msg import Heartbeat, ResourceClaim, RobotIntent, RobotState


class FleetAgentNode(Node):
    """Publish local state periodically and maintain a local world model."""

    def __init__(self):
        super().__init__('fleet_agent_node')

        self.declare_parameter('robot_id', 'amr_a')
        robot_id = self.get_parameter('robot_id').value.strip('/')
        self.robot_id = robot_id
        self.namespace = f'/{robot_id}'

        self.world_model = {}
        self.active_claims = {}

        self.state_publisher = self.create_publisher(RobotState, f'{self.namespace}/state', 10)
        self.heartbeat_publisher = self.create_publisher(Heartbeat, f'{self.namespace}/heartbeat', 10)
        self.intent_publisher = self.create_publisher(RobotIntent, f'{self.namespace}/intent', 10)
        self.claim_publisher = self.create_publisher(ResourceClaim, '/fleet/reservations', 10)

        self._tick = 0
        self.intent_counter = 0
        self.create_timer(1.0, self.publish_state)
        self.create_timer(0.5, self.publish_heartbeat)
        self.create_timer(2.0, self.publish_intent)
        self.create_timer(0.3, self.check_for_conflicts_tick)
        self.create_timer(2.0, self.print_world_model)

        for topic in ['/amr_a/state', '/amr_b/state', '/amr_c/state']:
            self.create_subscription(
                RobotState,
                topic,
                lambda msg, topic=topic: self.log_peer_state(topic, msg),
                10,
            )

        for topic in ['/amr_a/heartbeat', '/amr_b/heartbeat', '/amr_c/heartbeat']:
            self.create_subscription(
                Heartbeat,
                topic,
                lambda msg, topic=topic: self.log_peer_heartbeat(topic, msg),
                10,
            )

        for topic in ['/amr_a/intent', '/amr_b/intent', '/amr_c/intent']:
            self.create_subscription(
                RobotIntent,
                topic,
                lambda msg, topic=topic: self.log_peer_intent(topic, msg),
                10,
            )

        self.create_subscription(
            ResourceClaim,
            '/fleet/reservations',
            self.log_reservation,
            10,
        )

    def publish_state(self):
        """Publish changing placeholder state values and update world model."""
        self._tick += 1

        msg = RobotState()
        msg.robot_id = self.robot_id
        msg.timestamp = self.get_clock().now().nanoseconds / 1e9
        msg.x = 1.0 + self._tick * 0.05
        msg.y = 2.0 + self._tick * 0.03
        msg.theta = 0.0
        msg.linear_velocity = 0.4 + self._tick * 0.03
        msg.angular_velocity = 0.0
        msg.battery_percent = max(0.0, 100.0 - self._tick * 0.8)
        msg.current_task_id = 'move_to_next_waypoint'
        msg.status = 'NAVIGATING' if self._tick % 2 == 0 else 'IDLE'

        self.state_publisher.publish(msg)

        self.world_model[self.robot_id] = {
            'last_state': msg,
            'last_heartbeat_time': self.world_model.get(self.robot_id, {}).get('last_heartbeat_time'),
            'last_updated': self.get_clock().now(),
            'position': [msg.x, msg.y],
            'battery': msg.battery_percent,
            'status': msg.status,
            'target_intersection': self.world_model.get(self.robot_id, {}).get('target_intersection', 'I1'),
            'eta': self.world_model.get(self.robot_id, {}).get('eta', 0.0),
            'priority': self.world_model.get(self.robot_id, {}).get('priority', 0.0),
        }

        self.get_logger().info(
            f'Published state on {self.namespace}/state: '
            f'robot_id={msg.robot_id}, position=[{msg.x:.2f}, {msg.y:.2f}], battery={msg.battery_percent:.1f}%, status={msg.status}'
        )

    def publish_heartbeat(self):
        """Publish a heartbeat with a timestamp."""
        msg = Heartbeat()
        msg.robot_id = self.robot_id
        msg.timestamp = self.get_clock().now().nanoseconds / 1e9

        self.heartbeat_publisher.publish(msg)

        if self.robot_id not in self.world_model:
            self.world_model[self.robot_id] = {}

        self.world_model[self.robot_id]['last_heartbeat_time'] = self.get_clock().now()
        self.world_model[self.robot_id]['last_updated'] = self.get_clock().now()
        self.world_model[self.robot_id]['position'] = self.world_model.get(self.robot_id, {}).get('position', [0.0, 0.0])
        self.world_model[self.robot_id]['battery'] = self.world_model.get(self.robot_id, {}).get('battery', 0.0)
        self.world_model[self.robot_id]['status'] = self.world_model.get(self.robot_id, {}).get('status', 'unknown')

        self.get_logger().info(f'Published heartbeat on {self.namespace}/heartbeat for {self.robot_id}')

    def publish_intent(self):
        """Publish a placeholder intent message without immediate conflict resolution."""
        self.intent_counter += 1

        intersections = ['I1', 'I2', 'I3']
        index = (self.intent_counter - 1) % len(intersections)
        target_intersection = intersections[index]

        priority_map = {
            'amr_a': 1,
            'amr_b': 2,
            'amr_c': 3,
        }
        priority = int(priority_map.get(self.robot_id, 0))

        now_sec = self.get_clock().now().nanoseconds / 1e9
        eta = now_sec + 5.0 + float(priority)
        valid_until = eta + 10.0

        msg = RobotIntent()
        msg.robot_id = self.robot_id
        msg.timestamp = now_sec
        msg.task_id = f"task_{self.robot_id}_{self.intent_counter}"
        msg.target_resource_id = target_intersection
        msg.eta = eta
        msg.priority = float(priority)
        msg.valid_until = valid_until
        msg.planned_path = ["start", "checkpoint", target_intersection]

        delay = random.uniform(0.1, 0.4)
        self.get_logger().info(f'Intent jitter for {self.robot_id}: delaying {delay:.3f}s before publish')
        self.create_timer(delay, lambda: self.intent_publisher.publish(msg))

        self.world_model[self.robot_id] = {
            **self.world_model.get(self.robot_id, {}),
            'target_intersection': target_intersection,
            'eta': msg.eta,
            'priority': priority,
            'last_updated': self.get_clock().now(),
        }

        self.get_logger().info(
            f'Published intent on {self.namespace}/intent: '
            f'robot_id={msg.robot_id}, target={msg.target_resource_id}, eta={msg.eta}, priority={msg.priority}'
        )

    def check_for_conflicts_tick(self):
        """Re-evaluate this robot's current intent after peer intents arrive."""
        local_state = self.world_model.get(self.robot_id, {})
        if not local_state:
            return

        target_intersection = local_state.get('target_intersection')
        if target_intersection is None:
            return

        self.check_for_conflicts(target_intersection, local_state.get('eta', 0.0), local_state.get('priority', 0))

    def _should_skip_reclaim(self, target_intersection):
        """Avoid duplicate claims or stale waiting retries for the same intersection."""
        local_entry = self.world_model.get(self.robot_id, {})
        if not local_entry:
            return False

        current_target = local_entry.get('target_intersection')
        if current_target != target_intersection:
            return False

        claim_state = local_entry.get('claim_state', 'CLEAR')
        existing_claim = self.active_claims.get(target_intersection)

        if claim_state == 'CLAIMED' and existing_claim is not None and existing_claim.robot_id == self.robot_id:
            return True

        if claim_state == 'WAITING' and existing_claim is not None and existing_claim.robot_id != self.robot_id:
            return True

        return False

    def check_for_conflicts(self, target_intersection, eta, priority):
        """Check for conflicting intents and publish or defer reservations."""
        local_entry = self.world_model.get(self.robot_id, {})
        if not local_entry:
            return

        if self._should_skip_reclaim(target_intersection):
            self.get_logger().info(
                f'Skipping duplicate claim for {target_intersection} while robot_id={self.robot_id} already holds or waits on it.'
            )
            return

        now = self.get_clock().now()
        competing = []

        for other_robot_id, entry in self.world_model.items():
            if other_robot_id == self.robot_id:
                continue

            other_target = entry.get('target_intersection')
            other_eta = entry.get('eta', 0.0)
            other_priority = entry.get('priority', 0)
            if other_target != target_intersection:
                continue

            if abs(float(other_eta) - float(eta)) <= 3.0:
                competing.append((other_robot_id, other_priority, float(other_eta)))

        if not competing:
            existing_claim = self.active_claims.get(target_intersection)
            if existing_claim is not None and existing_claim.robot_id == self.robot_id:
                self.world_model[self.robot_id]['claim_state'] = 'CLAIMED'
                return

            claim = ResourceClaim()
            claim.robot_id = self.robot_id
            claim.resource = target_intersection
            claim.start_time = now.nanoseconds / 1e9
            claim.end_time = (now + rclpy.time.Duration(seconds=5.0)).nanoseconds / 1e9
            claim.priority = int(priority)
            claim.claim_id = f"{self.robot_id}_{target_intersection}_{self._tick}"
            self.claim_publisher.publish(claim)
            self.active_claims[target_intersection] = claim
            self.world_model[self.robot_id]['claim_state'] = 'CLAIMED'
            self.get_logger().info(f'CLAIMED {target_intersection} for {self.robot_id}')
            return

        winner_id = self.robot_id
        winner_priority = priority
        winner_eta = eta
        for peer_id, peer_priority, peer_eta in competing:
            if peer_priority > winner_priority:
                winner_id = peer_id
                winner_priority = peer_priority
                winner_eta = peer_eta
            elif peer_priority == winner_priority and peer_id < winner_id:
                winner_id = peer_id
                winner_eta = peer_eta

        if winner_id == self.robot_id:
            existing_claim = self.active_claims.get(target_intersection)
            if existing_claim is not None and existing_claim.robot_id == self.robot_id:
                self.world_model[self.robot_id]['claim_state'] = 'CLAIMED'
                return

            claim = ResourceClaim()
            claim.robot_id = self.robot_id
            claim.resource = target_intersection
            claim.start_time = now.nanoseconds / 1e9
            claim.end_time = (now + rclpy.time.Duration(seconds=5.0)).nanoseconds / 1e9
            claim.priority = int(priority)
            claim.claim_id = f"{self.robot_id}_{target_intersection}_{self._tick}"
            self.claim_publisher.publish(claim)
            self.active_claims[target_intersection] = claim
            self.world_model[self.robot_id]['claim_state'] = 'CLAIMED'
            self.get_logger().info(f'CLAIMED {target_intersection} for {self.robot_id}')
        else:
            self.world_model[self.robot_id]['claim_state'] = 'WAITING'
            self.get_logger().info(
                f'WAITING at {target_intersection}, robot_id={winner_id} has priority'
            )

    def log_peer_state(self, topic, msg):
        """Update world model from peer state messages and log them."""
        self.get_logger().info(
            f'Received on {topic}: robot_id={msg.robot_id}, '
            f'position=[{msg.x:.2f}, {msg.y:.2f}], battery={msg.battery_percent:.1f}%, status={msg.status}'
        )

        self.world_model[msg.robot_id] = {
            **self.world_model.get(msg.robot_id, {}),
            'last_state': msg,
            'last_heartbeat_time': self.world_model.get(msg.robot_id, {}).get('last_heartbeat_time'),
            'last_updated': self.get_clock().now(),
            'position': [msg.x, msg.y],
            'battery': msg.battery_percent,
            'status': msg.status,
        }

    def log_peer_heartbeat(self, topic, msg):
        """Update world model from peer heartbeat messages."""
        robot_id = msg.robot_id
        heartbeat_time = self.get_clock().now()

        if robot_id not in self.world_model:
            self.world_model[robot_id] = {
                'last_state': None,
                'last_heartbeat_time': heartbeat_time,
                'last_updated': heartbeat_time,
                'position': [0.0, 0.0],
                'battery': 0.0,
                'status': 'unknown',
                'target_intersection': 'unknown',
                'eta': 0.0,
                'priority': 0,
                'claim_state': 'CLEAR',
            }
        else:
            self.world_model[robot_id]['last_heartbeat_time'] = heartbeat_time
            self.world_model[robot_id]['last_updated'] = heartbeat_time

        self.get_logger().info(
            f'Received heartbeat on {topic}: robot_id={robot_id}, time={heartbeat_time.nanoseconds / 1e9}'
        )

    def log_peer_intent(self, topic, msg):
        """Store peer intent info in the world model and re-check for conflicts."""
        robot_id = msg.robot_id
        self.world_model[robot_id] = {
            **self.world_model.get(robot_id, {}),
            'target_intersection': msg.target_resource_id,
            'eta': msg.eta,
            'priority': msg.priority,
            'last_updated': self.get_clock().now(),
        }
        self.get_logger().info(
            f'Received intent on {topic}: robot_id={robot_id}, '
            f'target={msg.target_resource_id}, eta={msg.eta}, priority={msg.priority}'
        )
        self.check_for_conflicts_tick()

    def log_reservation(self, msg):
        """Track active reservations from the shared fleet reservation topic."""
        now = self.get_clock().now()
        claim_end = now.nanoseconds / 1e9 + 5.0
        self.active_claims[msg.resource] = msg

        if msg.robot_id == self.robot_id:
            self.world_model[self.robot_id]['claim_state'] = 'CLAIMED'
            self.get_logger().info(f'Observed my own claim on {msg.resource}: {msg.claim_id}')
        else:
            if msg.resource == self.world_model.get(self.robot_id, {}).get('target_intersection'):
                self.world_model[self.robot_id]['claim_state'] = 'WAITING'
            self.get_logger().info(
                f'Observed reservation: robot_id={msg.robot_id}, resource={msg.resource}, '
                f'claim_id={msg.claim_id}, priority={msg.priority}'
            )

    def print_world_model(self):
        """Print a readable table of the current world model."""
        if not self.world_model:
            self.get_logger().info('World model is empty.')
            return

        now = self.get_clock().now()
        header = (
            f"{'robot_id':<12} | {'position':<20} | {'battery':>8} | {'status':<10} | {'target':<12} | {'eta':>10} | {'claim':<8} | {'secs_since_hb':>14}"
        )
        self.get_logger().info('')
        self.get_logger().info(header)
        self.get_logger().info('-' * len(header))

        for robot_id, entry in self.world_model.items():
            position = entry.get('position', [0.0, 0.0])
            pos_str = f"[{position[0]:.2f}, {position[1]:.2f}]" if len(position) >= 2 else str(position)
            battery = entry.get('battery', 0.0)
            status = entry.get('status', 'unknown')
            target = entry.get('target_intersection', 'unknown')
            eta = entry.get('eta', 0.0)
            claim_state = entry.get('claim_state', 'CLEAR')
            last_hb = entry.get('last_heartbeat_time')

            if last_hb is None:
                secs_since_hb = float('nan')
            else:
                secs_since_hb = (now - last_hb).nanoseconds / 1e9

            row = (
                f"{robot_id:<12} | "
                f"{pos_str:<20} | "
                f"{battery:>8.2f} | "
                f"{status:<10} | "
                f"{target:<12} | "
                f"{eta:>10.2f} | "
                f"{claim_state:<8} | "
                f"{secs_since_hb:>14.2f}"
            )
            self.get_logger().info(row)


def main(args=None):
    """Initialize ROS 2 and spin the node."""
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
