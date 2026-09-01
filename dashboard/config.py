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


# ── Warehouse map (Gazebo world coordinates, metres) ────────────────────────

MAP_MIN_X = -10.0
MAP_MAX_X = 10.0
MAP_MIN_Y = -10.0
MAP_MAX_Y = 10.0
MAP_WIDTH = 20.0    # metres (-10.0 to +10.0)
MAP_HEIGHT = 20.0   # metres (-10.0 to +10.0)

# Named stations (Pickup / Dropoff / Charging locations from Gazebo warehouse)
STATIONS = {
    "P1": (-7.2, 0.0),    # Pickup Station 1 (West Central Aisle)
    "P2": (-7.2, -7.5),   # Pickup Station 2 (South-West)
    "D1": (6.8, 0.0),     # Drop Station 1 (East Central Aisle)
    "CHG": (6.0, 6.0),    # Charging Bay (North-East with dock & lightning terminal)
}

# Shared intersections / chokepoints with bollards
INTERSECTIONS = {
    "I1": (-4.3, 0.0),    # Intersection 1 (West-Central Chokepoint)
    "I2": (0.8, 0.0),     # Intersection 2 (East-Central Chokepoint)
}

# 8 Industrial Shelving Racks (S1 - S8 arranged vertically per simulation world)
RACKS = {
    "S1": (-6.5, -5.5),   # Bottom-Left
    "S2": (-6.5, 5.5),    # Top-Left
    "S3": (-2.1, -5.5),   # Bottom-Mid-West
    "S4": (-2.1, 5.5),    # Top-Mid-West
    "S5": (-0.7, -5.5),   # Bottom-Mid-East
    "S6": (-0.7, 5.5),    # Top-Mid-East
    "S7": (3.2, -5.5),    # Bottom-Right
    "S8": (3.2, 5.5),     # Top-Right
}

# Static Obstacles & Pallets (from Gazebo simulation world)
OBSTACLES = {
    "OBS_AISLE": (-1.5, 0.0),    # Orange Blocked Aisle Container (Center)
    "DUMPSTER": (6.2, -2.5),     # Green Waste Container (East)
    "PALLET_SE": (6.2, -5.5),    # Pallet Stack (South-East zone)
    "PALLET_NW": (-8.2, 5.5),    # Pallet Stack (North-West by S2)
    "PALLET_SW": (-3.7, -7.8),   # Pallet Stack (South by S3)
}

# Robot home / spawn positions (from Gazebo warehouse world)
ROBOT_HOMES = {
    "A": (-7.5, 0.8),    # AMR Blue (Spawns West by Pickup)
    "B": (-4.3, -3.2),   # AMR Green (Spawns South Aisle)
    "C": (5.0, 3.5),     # AMR Orange (Spawns North-East by Charging Bay)
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
