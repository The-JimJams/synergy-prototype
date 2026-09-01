"""
SYNERGY Dashboard — Configuration
===================================

Central configuration with sensible defaults.
Override via environment variables or by modifying this file.

Nothing here is a confirmed ROS 2 topic name or real system parameter.
All values are defaults for the standalone mock/demo mode.
"""

import os


# ── Dashboard server ────────────────────────────────────────────────────────

HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.getenv("DASHBOARD_PORT", "5000"))
DEBUG = os.getenv("DASHBOARD_DEBUG", "true").lower() in ("true", "1", "yes")

# "mock" or "ros2"
MODE = os.getenv("DASHBOARD_MODE", "mock")


# ── Simulator ───────────────────────────────────────────────────────────────

# Default scenario when none is specified on the command line
DEFAULT_SCENARIO = os.getenv("DASHBOARD_SCENARIO", "full_demo")

# Simulation speed multiplier (1.0 = real-time, 2.0 = double speed, etc.)
SIM_SPEED = float(os.getenv("DASHBOARD_SIM_SPEED", "1.0"))

# Whether the simulator loops its scenario continuously
SIM_LOOP = os.getenv("DASHBOARD_SIM_LOOP", "true").lower() in ("true", "1", "yes")


# ── Robot IDs ───────────────────────────────────────────────────────────────

ROBOT_IDS = ["A", "B", "C"]


# ── Warehouse map (mock layout, metres) ─────────────────────────────────────

MAP_WIDTH = 12.0    # metres
MAP_HEIGHT = 8.0    # metres

# Named stations (pickup / dropoff locations)
STATIONS = {
    "S1": (2.0, 1.5),
    "S2": (2.0, 6.5),
    "S3": (10.0, 1.5),
    "S4": (10.0, 6.5),
}

# Shared intersections / resources
INTERSECTIONS = {
    "I1": (5.0, 4.0),
    "I2": (8.0, 4.0),
}

# Robot home / starting positions
ROBOT_HOMES = {
    "A": (2.0, 4.0),
    "B": (6.0, 1.5),
    "C": (10.0, 4.0),
}


# ── Data store ──────────────────────────────────────────────────────────────

MAX_EVENTS = int(os.getenv("DASHBOARD_MAX_EVENTS", "1000"))
MAX_EXPERIMENT_RUNS = int(os.getenv("DASHBOARD_MAX_EXPERIMENT_RUNS", "200"))


# ── Frontend polling ────────────────────────────────────────────────────────

POLL_INTERVAL_MS = int(os.getenv("DASHBOARD_POLL_INTERVAL_MS", "500"))


# ── Experiment data output ──────────────────────────────────────────────────

DATA_DIR = os.getenv(
    "DASHBOARD_DATA_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
)
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")
EVENTS_DIR = os.path.join(DATA_DIR, "events")


# ── ROS 2 (placeholder — only used when MODE == "ros2") ────────────────────
# These are NOT confirmed real topic names.  They are placeholders that the
# ros2_adapter will read when integration mode is activated.

ROS2_TOPICS = {
    "robot_state":  "/synergy/{robot_id}/state",
    "robot_intent": "/synergy/{robot_id}/intent",
    "reservation":  "/synergy/reservations",
    "event":        "/synergy/events",
    "task":         "/synergy/tasks",
    "network":      "/synergy/network_status",
}
