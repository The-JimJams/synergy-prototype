"""Integration tests for RosbridgeLiveAdapter against a stub rosbridge server.

These exercise the real WebSocket path -- handshake, subscribe, publish, dispatch --
without needing ROS 2 installed, using a minimal stdlib WebSocket server.

They cover the three defects that made live mode look broken:

1. ``_handle_task_announcement`` / ``_handle_task_bid`` / ``_handle_reservation``
   imported ``dashboard.models`` while the package is imported as top-level
   ``models``.  The ImportError was caught by the surrounding ``except Exception``
   and logged at debug level, so every live task, bid and reservation event was
   silently dropped and the dashboard showed an empty feed.

2. Robot position was taken from ``/amr_*/odom``.  Gazebo's DiffDrive integrates
   odometry from zero at spawn, so that is an odom-frame pose, not a map-frame
   one, and it put every robot on the origin.  Position must come from
   ``/amr_*/state``.

3. There was no way to inject a task into the live fleet, so the dashboard fell
   back to simulating one itself.
"""

import base64
import hashlib
import json
import os
import socket
import struct
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_store import DataStore                              # noqa: E402
from adapters.rosbridge_live_adapter import RosbridgeLiveAdapter  # noqa: E402

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


# ── Minimal RFC 6455 server: enough for text frames in both directions ────────

def _encode_text_frame(payload: str) -> bytes:
    data = payload.encode("utf-8")
    header = bytearray([0x81])            # FIN + text opcode
    n = len(data)
    if n < 126:
        header.append(n)
    elif n < (1 << 16):
        header.append(126)
        header += struct.pack(">H", n)
    else:
        header.append(127)
        header += struct.pack(">Q", n)
    return bytes(header) + data           # server frames are never masked


def _read_exactly(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed")
        buf += chunk
    return buf


def _read_frame(sock):
    """Return the payload of one client text frame, or None for close/ping."""
    b0, b1 = _read_exactly(sock, 2)
    opcode = b0 & 0x0F
    masked = bool(b1 & 0x80)
    length = b1 & 0x7F
    if length == 126:
        length = struct.unpack(">H", _read_exactly(sock, 2))[0]
    elif length == 127:
        length = struct.unpack(">Q", _read_exactly(sock, 8))[0]
    mask = _read_exactly(sock, 4) if masked else b"\x00\x00\x00\x00"
    payload = _read_exactly(sock, length)
    if masked:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    if opcode in (0x8, 0x9, 0xA):         # close / ping / pong
        return None
    return payload.decode("utf-8", "replace")


class StubRosbridge:
    """Accepts one connection, records what the client sends, and can push messages."""

    def __init__(self):
        self._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv.bind(("127.0.0.1", 0))
        self._srv.listen(1)
        self.port = self._srv.getsockname()[1]

        self.received: list[dict] = []
        self._conn = None
        self._lock = threading.Lock()
        self.connected = threading.Event()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    @property
    def url(self):
        return f"ws://127.0.0.1:{self.port}"

    def _serve(self):
        try:
            conn, _ = self._srv.accept()
        except OSError:
            return

        request = b""
        while b"\r\n\r\n" not in request:
            chunk = conn.recv(4096)
            if not chunk:
                conn.close()
                return
            request += chunk

        key = ""
        for line in request.decode("latin-1").split("\r\n"):
            if line.lower().startswith("sec-websocket-key:"):
                key = line.split(":", 1)[1].strip()
        accept = base64.b64encode(
            hashlib.sha1((key + WS_GUID).encode()).digest()
        ).decode()
        conn.sendall(
            b"HTTP/1.1 101 Switching Protocols\r\n"
            b"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            b"Sec-WebSocket-Accept: " + accept.encode() + b"\r\n\r\n"
        )

        with self._lock:
            self._conn = conn
        self.connected.set()

        while not self._stop.is_set():
            try:
                raw = _read_frame(conn)
            except (ConnectionError, OSError):
                break
            if raw is None:
                continue
            try:
                self.received.append(json.loads(raw))
            except json.JSONDecodeError:
                pass

    def push(self, topic: str, msg: dict):
        """Send one rosbridge 'publish' packet to the connected client."""
        with self._lock:
            conn = self._conn
        assert conn is not None, "no client connected"
        conn.sendall(_encode_text_frame(
            json.dumps({"op": "publish", "topic": topic, "msg": msg})
        ))

    def ops(self, op: str):
        return [m for m in self.received if m.get("op") == op]

    def wait_for(self, predicate, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if predicate():
                return True
            time.sleep(0.02)
        return False

    def close(self):
        self._stop.set()
        with self._lock:
            if self._conn:
                try:
                    self._conn.close()
                except OSError:
                    pass
        try:
            self._srv.close()
        except OSError:
            pass


@pytest.fixture
def live(tmp_path):
    pytest.importorskip("websocket", reason="websocket-client is required for live mode")
    server = StubRosbridge()
    store = DataStore()
    adapter = RosbridgeLiveAdapter(store, url=server.url)
    adapter.start()
    assert server.connected.wait(timeout=5.0), "adapter never connected to stub rosbridge"
    assert server.wait_for(lambda: len(server.ops("subscribe")) >= 4), "adapter did not subscribe"
    try:
        yield adapter, store, server
    finally:
        adapter.stop()
        server.close()


# ── Tests ────────────────────────────────────────────────────────────────────

def test_subscribes_to_state_and_not_to_odom(live):
    """Position must come from the map-frame /state topic, never from /odom."""
    _, _, server = live
    topics = {m["topic"] for m in server.ops("subscribe")}

    assert "/amr_a/state" in topics
    assert "/amr_b/state" in topics
    assert "/amr_c/state" in topics
    assert not any(t.endswith("/odom") for t in topics), (
        "odom is an odom-frame pose that starts at zero at spawn; "
        "subscribing to it puts every robot on the origin"
    )


def test_state_message_sets_map_frame_pose(live):
    """A RobotState at the robot's real spawn pose must land in the store unchanged."""
    _, store, server = live
    server.push("/amr_a/state", {
        "robot_id": "amr_a", "x": -3.5, "y": 5.25, "theta": 1.2,
        "linear_velocity": 0.42, "battery_percent": 91.0,
        "status": "NAVIGATING", "current_task_id": "task_test_001",
    })
    assert server.wait_for(lambda: store.get_robot_state("A") is not None)

    robot = store.get_robot_state("A")
    assert robot["x"] == pytest.approx(-3.5)
    assert robot["y"] == pytest.approx(5.25)
    assert robot["yaw"] == pytest.approx(1.2)
    assert robot["velocity"] == pytest.approx(0.42)
    assert robot["battery"] == pytest.approx(91.0)
    assert robot["status"] == "NAVIGATING"


def test_each_robot_keeps_its_own_identity(live):
    """Three robots, three distinct poses -- no cross-talk between namespaces."""
    _, store, server = live
    poses = {"amr_a": (-3.5, 5.25), "amr_b": (0.5, 8.5), "amr_c": (3.5, -6.5)}
    for ns, (x, y) in poses.items():
        server.push(f"/{ns}/state", {
            "robot_id": ns, "x": x, "y": y, "theta": 0.0,
            "linear_velocity": 0.0, "battery_percent": 95.0, "status": "IDLE",
        })
    assert server.wait_for(lambda: len(store.get_all_robots(stale_threshold_s=60)) == 3)

    for ns, dash_id in (("amr_a", "A"), ("amr_b", "B"), ("amr_c", "C")):
        robot = store.get_robot_state(dash_id)
        assert robot["robot_id"] == dash_id
        assert (robot["x"], robot["y"]) == pytest.approx(poses[ns])


def test_task_announcement_reaches_the_store(live):
    """Regression: this was dropped by an ImportError swallowed as a debug log."""
    _, store, server = live
    server.push("/tasks/announcements", {
        "task_id": "task_test_001", "pickup": "P1", "dropoff": "D1",
        "priority": 3, "deadline": time.time() + 90,
        "capability_requirements": ["delivery", "navigation"],
    })
    assert server.wait_for(lambda: any(
        t["task_id"] == "task_test_001" for t in store.get_tasks()
    )), "live task announcement never reached the data store"

    assert any(e["event_type"] == "TASK_ANNOUNCED" for e in store.get_events(limit=50))


def test_bid_and_reservation_reach_the_event_feed(live):
    """Regression: same swallowed ImportError killed bid and reservation events."""
    _, store, server = live
    server.push("/tasks/bids", {
        "robot_id": "amr_b", "task_id": "task_test_001",
        "estimated_time": 12.5, "distance": 7.5, "battery_cost": 0.1, "confidence": 0.9,
    })
    server.push("/fleet/reservations", {
        "robot_id": "amr_a", "resource": "I1", "status": "CLAIMED",
        "claim_id": "c1", "priority": 3, "start_time": 0.0, "end_time": 5.0,
    })

    assert server.wait_for(lambda: any(
        e["event_type"] == "BID_SUBMITTED" for e in store.get_events(limit=50)
    )), "live bid never reached the event feed"
    assert server.wait_for(lambda: any(
        e["event_type"] == "RESERVATION" for e in store.get_events(limit=50)
    )), "live reservation never reached the event feed"


def test_announce_task_publishes_to_the_fleet(live):
    """Task injection publishes an announcement and assigns nobody."""
    adapter, store, server = live

    assert server.wait_for(lambda: any(
        m["topic"] == "/tasks/announcements" for m in server.ops("advertise")
    )), "announcement topic was never advertised"

    ok, detail = adapter.announce_task("T42", "P1", "D1", priority=3)
    assert ok, detail

    assert server.wait_for(lambda: any(
        m["topic"] == "/tasks/announcements" for m in server.ops("publish")
    ))
    published = [m for m in server.ops("publish") if m["topic"] == "/tasks/announcements"][-1]
    msg = published["msg"]
    assert msg["task_id"] == "T42"
    assert msg["pickup"] == "P1"
    assert msg["dropoff"] == "D1"
    assert msg["priority"] == 3
    # The dashboard announces; the robots decide. No winner is named here.
    assert "assigned_robot" not in msg
    assert "winner" not in msg


def test_announce_task_fails_cleanly_when_disconnected():
    """With no rosbridge, announcing must report an error, never fabricate a task."""
    pytest.importorskip("websocket")
    store = DataStore()
    adapter = RosbridgeLiveAdapter(store, url="ws://127.0.0.1:1")  # nothing listening
    ok, detail = adapter.announce_task("T99", "P1", "D1")
    assert ok is False
    assert "rosbridge" in detail.lower()
    assert store.get_tasks() == []
    assert store.get_all_robots() == {}
