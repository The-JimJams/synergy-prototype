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
from datetime import datetime, timezone
import math
import threading
import time
from typing import Optional

from models import RobotState, Event, Task, Reservation
from data_store import DataStore

logger = logging.getLogger("synergy.adapters.rosbridge")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

TASK_ANNOUNCE_TOPIC = "/tasks/announcements"

# Map from ROS robot namespace -> dashboard robot_id
ROBOT_MAP = {
    "amr_a": "A",
    "amr_b": "B",
    "amr_c": "C",
}


def _quat_to_yaw(ox: float, oy: float, oz: float, ow: float) -> float:
    """Extract yaw from a quaternion."""
    return math.atan2(2.0 * (ow * oz + ox * oy), 1.0 - 2.0 * (oy * oy + oz * oz))


class RosbridgeLiveAdapter:
    """Connects to rosbridge WebSocket on the host and feeds live telemetry into DataStore."""

    def __init__(self, data_store: DataStore, url: str = "ws://localhost:9090"):
        self.data_store = data_store
        self.url = url
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._ws = None
        self._connected = threading.Event()
        self._announce_advertised = False

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
        """True while the adapter's reconnect thread is running.

        This stays True when rosbridge is unreachable, because the thread keeps
        retrying. Use is_connected() to tell whether data is actually arriving.
        """
        return self._thread is not None and self._thread.is_alive()

    def is_connected(self) -> bool:
        """True only while the rosbridge WebSocket is actually open."""
        return self._connected.is_set()

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
        self._connected.set()
        # Advertise the task announcement topic so an operator can inject a task.
        # Publishing an announcement is a task *source*; the robots still run the
        # bidding and pick the winner themselves.
        ws.send(json.dumps({
            "op": "advertise",
            "topic": TASK_ANNOUNCE_TOPIC,
            "type": "fleet_msgs/TaskAnnouncement",
        }))
        self._announce_advertised = True
        # Subscribe to all active robot namespaces
        for ns in ROBOT_MAP:
            # /state carries the map-frame pose (see _handle_fleet_state).
            # /odom is deliberately NOT subscribed: it is an odom-frame pose that
            # starts at zero regardless of where the robot spawned.
            self._subscribe(ws, f"/{ns}/state", "fleet_msgs/RobotState", throttle=50)
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
        self._connected.clear()
        self._announce_advertised = False
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

        if topic.endswith("/state"):
            self._handle_fleet_state(dashboard_id, msg)

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
        """fleet_msgs/TaskAnnouncement -> a task row plus a TASK_ANNOUNCED event.

        The Task model has no priority field, so priority is carried in the event
        message rather than silently dropped.
        """
        try:
            task_id = str(msg.get("task_id", ""))
            if not task_id:
                return
            pickup = str(msg.get("pickup", ""))
            dropoff = str(msg.get("dropoff", ""))
            priority = int(msg.get("priority", 1))

            self.data_store.update_task(Task(
                task_id=task_id,
                pickup=pickup,
                dropoff=dropoff,
                assigned_robot=None,      # the fleet decides this, not the dashboard
                status="ANNOUNCED",
            ))
            self.data_store.add_event(Event(
                event_type="TASK_ANNOUNCED",
                robot_id="FLEET",
                task_id=task_id,
                message=f"Task {task_id}: {pickup} -> {dropoff} (priority {priority})",
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(f"Malformed TaskAnnouncement dropped: {exc} ({msg!r})")

    def _handle_task_bid(self, msg: dict) -> None:
        """fleet_msgs/TaskBid -> a BID_SUBMITTED event in the coordination feed."""
        try:
            robot_ns = str(msg.get("robot_id", ""))
            task_id = str(msg.get("task_id", ""))
            est_time = float(msg.get("estimated_time", 0.0))
            distance = float(msg.get("distance", 0.0))

            self.data_store.add_event(Event(
                event_type="BID_SUBMITTED",
                robot_id=ROBOT_MAP.get(robot_ns, robot_ns.upper()),
                task_id=task_id,
                message=f"Bid on {task_id}: est_time={est_time:.2f}s, dist={distance:.2f}m",
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(f"Malformed TaskBid dropped: {exc} ({msg!r})")

    def _handle_reservation(self, msg: dict) -> None:
        """fleet_msgs/ResourceClaim -> a reservation row plus an event.

        Recording the row as well as the event is what lets the reservations table
        show live intersection claims; previously only the event was produced and
        the table stayed empty in live mode.
        """
        try:
            resource = str(msg.get("resource", ""))
            if not resource:
                return
            robot_ns = str(msg.get("robot_id", ""))
            robot_id = ROBOT_MAP.get(robot_ns, robot_ns.upper())
            status = str(msg.get("status", "CLAIMED")).upper()

            # A claim whose resource names a task the fleet announced is the
            # winner declaring the assignment it computed for itself. Reflect it
            # on the task so the queue stops showing every live task as
            # ANNOUNCED with no owner -- the dashboard reports the fleet's
            # decision here, it never makes one.
            known_task = self.data_store.get_task(resource)
            if known_task is not None:
                if status in ("COMPLETED",):
                    task_status = "COMPLETED"
                elif status in ("RELEASED", "FREE"):
                    # A release after a failed Nav2 leg is not the same thing as
                    # a fresh announcement. Flipping the row back to ANNOUNCED
                    # made a task that had visibly started look like it had never
                    # been picked up, and it then sat there with no owner and no
                    # explanation. Show it as FAILED and keep the robot that was
                    # working it, so the queue says what actually happened.
                    already = str(known_task.get("status", "")).upper()
                    task_status = "COMPLETED" if already == "COMPLETED" else "FAILED"
                else:
                    task_status = "ASSIGNED"
                self.data_store.update_task(Task(
                    task_id=resource,
                    pickup=known_task.get("pickup", ""),
                    dropoff=known_task.get("dropoff", ""),
                    assigned_robot=robot_id,
                    status=task_status,
                    created_at=known_task.get("created_at") or _now_iso(),
                    completed_at=_now_iso() if task_status == "COMPLETED" else None,
                ))

            if status in ("RELEASED", "FREE", "COMPLETED"):
                self.data_store.release_reservation(resource)
            elif known_task is None:
                # Only physical resources (intersections, aisles) belong in the
                # reservations table; task claims are shown on the task queue.
                self.data_store.update_reservation(Reservation(
                    resource_id=resource,
                    robot_id=robot_id,
                    status=status,
                ))

            self.data_store.add_event(Event(
                event_type="RESERVATION",
                robot_id=robot_id,
                resource_id=resource,
                message=f"Resource {resource} {status} by {robot_id}",
            ))
        except (KeyError, TypeError, ValueError) as exc:
            logger.warning(f"Malformed ResourceClaim dropped: {exc} ({msg!r})")

    # ── Task injection (the only thing this adapter writes to ROS) ───────────

    def announce_task(self, task_id: str, pickup: str, dropoff: str,
                      priority: int = 3, deadline_sec: float = 90.0) -> tuple[bool, str]:
        """Publish one TaskAnnouncement onto the live fleet topic.

        Returns ``(ok, detail)``.  This does not assign the task, choose a winner,
        or command any robot -- those decisions stay with the robots' own
        allocators.  It is the operator equivalent of a new order arriving.
        """
        if not self._connected.is_set() or self._ws is None:
            return False, "Not connected to rosbridge; is rosbridge_server running on :9090?"
        if not self._announce_advertised:
            return False, "Task announcement topic has not been advertised yet."

        payload = {
            "op": "publish",
            "topic": TASK_ANNOUNCE_TOPIC,
            "msg": {
                "task_id": str(task_id),
                "pickup": str(pickup),
                "dropoff": str(dropoff),
                "deadline": time.time() + float(deadline_sec),
                "priority": int(priority),
                "capability_requirements": ["delivery", "navigation"],
            },
        }
        try:
            self._ws.send(json.dumps(payload))
        except Exception as exc:  # noqa: BLE001 - surface the reason to the caller
            return False, f"Failed to publish task announcement: {exc}"

        logger.info(f"Announced task {task_id} ({pickup} -> {dropoff}) to the live fleet.")
        return True, "announced"
