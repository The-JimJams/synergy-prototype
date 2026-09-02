"""
SYNERGY Dashboard — Rosbridge Live Adapter
==========================================

Runs on the Mac host. Connects to rosbridge at ws://localhost:9090 and
subscribes to live ROS 2 topics, pushing data into the DataStore so the
warehouse map displays real robot positions.

Topics consumed (read-only):
  /amr_a/odom         → nav_msgs/Odometry  → position (x, y, yaw), velocity
  /amr_a/state        → fleet_msgs/RobotState → status, task_id, battery

Usage:
    adapter = RosbridgeLiveAdapter(data_store)
    adapter.start()   # launches a background thread
    ...
    adapter.stop()
"""

import json
import logging
import math
import threading
import time
from typing import Optional

from models import RobotState, Event
from data_store import DataStore

logger = logging.getLogger("synergy.adapters.rosbridge")

# Map from ROS robot namespace → dashboard robot_id
ROBOT_MAP = {
    "amr_a": "A",
    "amr_b": "B",
    "amr_c": "C",
}


def _quat_to_yaw(ox: float, oy: float, oz: float, ow: float) -> float:
    """Extract yaw from quaternion."""
    return math.atan2(2.0 * (ow * oz + ox * oy), 1.0 - 2.0 * (oy * oy + oz * oz))


class RosbridgeLiveAdapter:
    """Connects to rosbridge WebSocket on the host and feeds live telemetry into DataStore."""

    def __init__(self, data_store: DataStore, url: str = "ws://localhost:9090"):
        self.data_store = data_store
        self.url = url
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._ws = None

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="rosbridge-adapter")
        self._thread.start()
        logger.info(f"Rosbridge live adapter started → {self.url}")

    def stop(self) -> None:
        self._stop_event.set()
        if self._ws:
            try:
                self._ws.close()
            except Exception:
                pass
        logger.info("Rosbridge live adapter stopped.")

    def is_active(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    # ── Internal ─────────────────────────────────────────────────────────────

    def _run(self) -> None:
        """Background thread: connect → subscribe → receive loop with auto-reconnect."""
        try:
            import websocket  # pip install websocket-client
        except ImportError:
            logger.error("websocket-client not installed. Run: pip install websocket-client")
            return

        while not self._stop_event.is_set():
            try:
                self._ws = websocket.WebSocketApp(
                    self.url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self._ws.run_forever(ping_interval=10, ping_timeout=5)
            except Exception as exc:
                logger.warning(f"Rosbridge connection error: {exc}")

            if not self._stop_event.is_set():
                logger.info("Rosbridge disconnected, retrying in 3s…")
                time.sleep(3)

    def _subscribe(self, ws, topic: str, msg_type: str, throttle: int = 50) -> None:
        msg = {
            "op": "subscribe",
            "topic": topic,
            "type": msg_type,
            "throttle_rate": throttle,
            "queue_length": 1,
        }
        ws.send(json.dumps(msg))

    def _on_open(self, ws) -> None:
        logger.info("Connected to rosbridge.")
        # Subscribe to all active robot namespaces
        for ns in ROBOT_MAP:
            self._subscribe(ws, f"/{ns}/odom", "nav_msgs/Odometry", throttle=50)
            self._subscribe(ws, f"/{ns}/state", "fleet_msgs/RobotState", throttle=100)
        # Subscribe to global fleet channels
        self._subscribe(ws, "/tasks/announcements", "fleet_msgs/TaskAnnouncement", throttle=0)
        self._subscribe(ws, "/tasks/bids", "fleet_msgs/TaskBid", throttle=0)
        self._subscribe(ws, "/fleet/reservations", "fleet_msgs/ResourceClaim", throttle=0)
        logger.info("Subscribed to odom, state, task, and reservation topics for live fleet.")

    def _on_message(self, ws, raw: str) -> None:
        try:
            pkt = json.loads(raw)
            if pkt.get("op") != "publish":
                return
            topic: str = pkt.get("topic", "")
            msg = pkt.get("msg", {})
            self._dispatch(topic, msg)
        except Exception as exc:
            logger.debug(f"Message parse error: {exc}")

    def _on_error(self, ws, error) -> None:
        logger.warning(f"Rosbridge WS error: {error}")

    def _on_close(self, ws, code, reason) -> None:
        logger.info(f"Rosbridge WS closed (code={code}).")

    def _dispatch(self, topic: str, msg: dict) -> None:
        """Route incoming ROS messages to the correct DataStore update."""
        if topic == "/tasks/announcements":
            self._handle_task_announcement(msg)
            return
        elif topic == "/tasks/bids":
            self._handle_task_bid(msg)
            return
        elif topic == "/fleet/reservations":
            self._handle_reservation(msg)
            return

        # Determine which robot this message belongs to
        robot_ns = None
        for ns in ROBOT_MAP:
            if topic.startswith(f"/{ns}/"):
                robot_ns = ns
                break
        if robot_ns is None:
            return

        dashboard_id = ROBOT_MAP[robot_ns]

        if topic.endswith("/odom"):
            self._handle_odom(dashboard_id, msg)
        elif topic.endswith("/state"):
            self._handle_fleet_state(dashboard_id, msg)

    def _handle_odom(self, robot_id: str, msg: dict) -> None:
        """Parse nav_msgs/Odometry and update DataStore robot position."""
        try:
            pose = msg["pose"]["pose"]
            twist = msg["twist"]["twist"]
            pos = pose["position"]
            ori = pose["orientation"]

            x = float(pos.get("x", 0.0))
            y = float(pos.get("y", 0.0))
            yaw = _quat_to_yaw(
                float(ori.get("x", 0.0)),
                float(ori.get("y", 0.0)),
                float(ori.get("z", 0.0)),
                float(ori.get("w", 1.0)),
            )
            vx = float(twist.get("linear", {}).get("x", 0.0))
            vy = float(twist.get("linear", {}).get("y", 0.0))
            velocity = math.hypot(vx, vy)

            # Merge with existing state dict
            existing_obj = self.data_store.get_robot_state(robot_id)
            existing = existing_obj if isinstance(existing_obj, dict) else (existing_obj.__dict__ if existing_obj else {})
            state = RobotState(
                robot_id=robot_id,
                x=x,
                y=y,
                yaw=yaw,
                velocity=velocity,
                battery=float(existing.get("battery", 100.0)),
                status=existing.get("status", "MOVING" if velocity > 0.05 else "IDLE"),
                task_id=existing.get("task_id"),
            )
            self.data_store.update_robot(state)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            logger.debug(f"Odom parse error for {robot_id}: {exc}")

    def _handle_fleet_state(self, robot_id: str, msg: dict) -> None:
        """Parse fleet_msgs/RobotState and update status / battery / task."""
        try:
            existing_obj = self.data_store.get_robot_state(robot_id)
            existing = existing_obj if isinstance(existing_obj, dict) else (existing_obj.__dict__ if existing_obj else {})
            status_raw = msg.get("status", "").upper()
            status = status_raw if status_raw else existing.get("status", "IDLE")

            x = float(msg.get("x", existing.get("x", 0.0)))
            y = float(msg.get("y", existing.get("y", 0.0)))

            state = RobotState(
                robot_id=robot_id,
                x=x,
                y=y,
                yaw=float(msg.get("theta", existing.get("yaw", 0.0))),
                velocity=float(msg.get("linear_velocity", existing.get("velocity", 0.0))),
                battery=float(msg.get("battery_percent", existing.get("battery", 100.0))),
                status=status,
                task_id=msg.get("current_task_id") or existing.get("task_id"),
            )
            self.data_store.update_robot(state)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            logger.debug(f"FleetState parse error for {robot_id}: {exc}")

    def _handle_task_announcement(self, msg: dict) -> None:
        try:
            from dashboard.models import Task, Event
            task_id = msg.get("task_id", "")
            pickup = msg.get("pickup", "")
            dropoff = msg.get("dropoff", "")
            priority = int(msg.get("priority", 1))
            task = Task(
                task_id=task_id,
                pickup=pickup,
                dropoff=dropoff,
                priority=priority,
                status="ANNOUNCED",
            )
            self.data_store.add_task(task)
            self.data_store.add_event(Event(
                event_type="TASK_ANNOUNCED",
                robot_id="FLEET",
                task_id=task_id,
                details=f"Task {task_id}: {pickup} -> {dropoff} (priority {priority})",
            ))
        except Exception as exc:
            logger.debug(f"Task announcement parse error: {exc}")

    def _handle_task_bid(self, msg: dict) -> None:
        try:
            from dashboard.models import Event
            robot_id = msg.get("robot_id", "")
            task_id = msg.get("task_id", "")
            est_time = float(msg.get("estimated_time", 0.0))
            self.data_store.add_event(Event(
                event_type="BID_SUBMITTED",
                robot_id=robot_id.upper(),
                task_id=task_id,
                details=f"Bid on {task_id}: est_time={est_time:.2f}s",
            ))
        except Exception as exc:
            logger.debug(f"Task bid parse error: {exc}")

    def _handle_reservation(self, msg: dict) -> None:
        try:
            from dashboard.models import Event
            resource = msg.get("resource", "")
            robot_id = msg.get("robot_id", "")
            status = msg.get("status", "CLAIMED")
            self.data_store.add_event(Event(
                event_type="RESERVATION",
                robot_id=robot_id.upper(),
                details=f"Resource {resource} {status} by {robot_id}",
            ))
        except Exception as exc:
            logger.debug(f"Reservation parse error: {exc}")
