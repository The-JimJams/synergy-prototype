"""
SYNERGY Dashboard — ROS 2 Telemetry Adapter
=============================================

Connects the dashboard to a real ROS 2 fleet system when ROS 2 (rclpy) is present.

ISOLATION & SAFETY GUARANTEES
------------------------------
1. Does NOT import rclpy at module level. Importing this file will NEVER crash
   the dashboard if ROS 2 is not installed.
2. Read-only: creates ONLY Subscribers. NEVER publishes control commands, goal poses,
   or reservation decisions.
3. Maps raw ROS message dictionaries / objects to normalized internal models
   (RobotState, RobotIntent, Reservation, Event, NetworkStatus) before writing to DataStore.
"""

import logging
from typing import Dict, Any, Optional

import config
from data_store import DataStore
from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Event,
    NetworkStatus,
    Task,
)

logger = logging.getLogger("synergy.adapters.ros2")

# Check rclpy availability at runtime
HAS_ROS2 = False
try:
    import rclpy
    from rclpy.node import Node
    HAS_ROS2 = True
except ImportError:
    Node = object  # Fallback base class when ROS 2 is absent


# ── ISOLATED ROS CONVERSION HELPERS ──────────────────────────────────────────

def robot_state_from_ros(msg: Any, robot_id: str = "A") -> RobotState:
    """Convert raw ROS message object or dict to normalized RobotState."""
    data = msg if isinstance(msg, dict) else getattr(msg, "__dict__", {})
    return RobotState(
        robot_id=str(data.get("robot_id", robot_id)),
        x=float(data.get("x", data.get("position_x", 0.0))),
        y=float(data.get("y", data.get("position_y", 0.0))),
        yaw=float(data.get("yaw", data.get("heading", 0.0))),
        velocity=float(data.get("velocity", data.get("speed", 0.0))),
        battery=float(data.get("battery", data.get("battery_percentage", 100.0))),
        status=str(data.get("status", data.get("state", "UNKNOWN"))),
        task_id=data.get("task_id"),
    )


def robot_intent_from_ros(msg: Any, robot_id: str = "A") -> RobotIntent:
    """Convert raw ROS message object or dict to normalized RobotIntent."""
    data = msg if isinstance(msg, dict) else getattr(msg, "__dict__", {})
    return RobotIntent(
        robot_id=str(data.get("robot_id", robot_id)),
        resource_id=str(data.get("resource_id", data.get("target_intersection", "UNKNOWN"))),
        eta=float(data.get("eta")) if data.get("eta") is not None else None,
    )


def reservation_from_ros(msg: Any) -> Reservation:
    """Convert raw ROS message object or dict to normalized Reservation."""
    data = msg if isinstance(msg, dict) else getattr(msg, "__dict__", {})
    return Reservation(
        resource_id=str(data.get("resource_id", "UNKNOWN")),
        robot_id=data.get("robot_id"),
        status=str(data.get("status", "FREE")),
    )


def event_from_ros(msg: Any) -> Event:
    """Convert raw ROS message object or dict to normalized Event."""
    data = msg if isinstance(msg, dict) else getattr(msg, "__dict__", {})
    return Event(
        event_type=str(data.get("event_type", "INFO")),
        robot_id=data.get("robot_id"),
        related_robot_id=data.get("related_robot_id"),
        resource_id=data.get("resource_id"),
        task_id=data.get("task_id"),
        message=str(data.get("message", "")),
    )


def network_from_ros(msg: Any) -> NetworkStatus:
    """Convert raw ROS message object or dict to normalized NetworkStatus."""
    data = msg if isinstance(msg, dict) else getattr(msg, "__dict__", {})
    return NetworkStatus(
        status=str(data.get("status", "NORMAL")),
        latency_ms=float(data["latency_ms"]) if "latency_ms" in data else None,
        packet_loss_percent=float(data["packet_loss_percent"]) if "packet_loss_percent" in data else None,
        active_peers=int(data["active_peers"]) if "active_peers" in data else None,
    )


# ── ROS 2 NODE ADAPTER CLASS ──────────────────────────────────────────────────

class ROS2Adapter:
    """ROS 2 telemetry adapter node."""

    def __init__(self, data_store: DataStore, topic_config: Optional[Dict[str, str]] = None):
        self.data_store = data_store
        self.topics = topic_config or config.ROS2_TOPICS
        self.node = None
        self._is_active = False

        if not HAS_ROS2:
            logger.warning("ROS 2 (rclpy) is NOT available on this system. ROS2Adapter standing by.")
            return

    def start(self) -> None:
        """Initialize ROS 2 node and subscribers if rclpy is available."""
        if not HAS_ROS2:
            logger.error("Cannot start ROS2Adapter: rclpy module unavailable.")
            return

        try:
            if not rclpy.ok():
                rclpy.init()

            self.node = rclpy.create_node("synergy_dashboard_adapter")
            logger.info("ROS 2 node 'synergy_dashboard_adapter' initialized.")
            self._is_active = True
        except Exception as e:
            logger.exception(f"Failed to start ROS 2 node: {e}")
            self._is_active = False

    def stop(self) -> None:
        """Shutdown ROS 2 node safely."""
        if self.node and HAS_ROS2:
            try:
                self.node.destroy_node()
                logger.info("ROS 2 adapter node destroyed.")
            except Exception as e:
                logger.warning(f"Error destroying ROS 2 node: {e}")
        self._is_active = False

    def is_active(self) -> bool:
        return self._is_active
