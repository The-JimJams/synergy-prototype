"""
SYNERGY Dashboard — Configuration
===================================

Central configuration with sensible defaults.
Override via environment variables or by modifying this file.

The warehouse layout constants and ROS 2 topic names below are the REAL ones:
the layout is read from gazebo/simulation/worlds/warehouse.sdf and agrees with
src/synergy_nav2/maps/warehouse_map.pgm; the topics are the ones the nodes in
src/ actually publish on. Server/simulator settings above them are demo defaults.
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

# ── Warehouse layout — GROUND TRUTH from gazebo/simulation/worlds/warehouse.sdf
#
# Every coordinate below is the object's actual pose in the Gazebo world and
# agrees with the Nav2 occupancy grid in src/synergy_nav2/maps/warehouse_map.pgm.
# Keep these in sync with WAYPOINTS in task_allocator_node.py and with the
# layout constants in static/js/map.js — a robot drawn against a warehouse that
# does not exist is what made live AMRs look like they drove through shelving.

# Named stations. Station goal poses (what a robot navigates to) are in
# WAYPOINTS; these are where the station pads are drawn.
STATIONS = {
    "P1": (0.0, 8.0),      # pickup_P1  — north bay
    "P2": (-5.5, -7.0),    # pickup_P2  — south-west bay
    "D1": (0.0, -8.1),     # drop_pack_D1 — south bay
    "CHG": (5.5, -7.5),    # charging_bay — south-east
}

# Shared intersections / chokepoints, each flanked by a pair of bollards
# at x = +/- 0.75 in the central corridor.
INTERSECTIONS = {
    "I1": (0.0, 5.2),      # north chokepoint
    "I2": (0.0, -0.7),     # central chokepoint
}

# 8 high-bay shelving racks. Each rack is 5.0 m (X) x 1.0 m (Y) x 2.2 m,
# standing in two columns at x = -4.8 and x = +4.8.
RACKS = {
    "S1": (-4.8, 7.5),
    "S2": (4.8, 7.5),
    "S3": (-4.8, 3.0),
    "S4": (4.8, 3.0),
    "S5": (-4.8, 1.5),
    "S6": (4.8, 1.5),
    "S7": (-4.8, -3.0),
    "S8": (4.8, -3.0),
}

# Rack footprint in metres (same for every rack), used for drawing.
RACK_SIZE = (5.0, 1.0)

# Where a robot actually stops to service each rack.
#
# RACKS above holds rack CENTRES, which is what the map draws -- but a centre is
# inside a 5.0 x 1.0 x 2.2 m solid and is not a pose any robot can occupy.  These
# aisle-side approach poses mirror task_allocator_node.WAYPOINTS, so a task to
# "S1" resolves to the same destination in mock mode as it does on the live fleet.
RACK_APPROACHES = {
    "S1": (-4.8, 6.0),     # rack (-4.8,  7.5), approached from the south aisle
    "S2": (4.8, 6.0),      # rack ( 4.8,  7.5)
    "S3": (-4.8, 4.3),     # rack (-4.8,  3.0), approached from the north aisle
    "S4": (4.8, 4.3),      # rack ( 4.8,  3.0)
    "S5": (-4.8, 0.0),     # rack (-4.8,  1.5)
    "S6": (4.8, 0.0),      # rack ( 4.8,  1.5)
    "S7": (-4.8, -4.5),    # rack (-4.8, -3.0)
    "S8": (4.8, -4.5),     # rack ( 4.8, -3.0)
}

# Static obstacles and props.
OBSTACLES = {
    "OBS_AISLE": (-0.2, 0.75),   # blocked_aisle_obstacle (movable, 0.8 x 1.2)
    "DUMPSTER": (-2.8, -7.3),    # green_dumpster_container (1.2 x 0.8)
    "PALLET_SW": (-5.2, -7.3),   # pallet_tower_1
    "PALLET_NE": (5.2, 8.75),    # pallet_tower_2
    "PALLET_NW": (-8.0, 5.25),   # pallet_tower_3
}

# Robot spawn poses, straight from the world file's <include> blocks.
ROBOT_HOMES = {
    "A": (-3.5, 5.25),     # amr_blue
    "B": (0.5, 8.5),       # amr_green
    "C": (3.5, -6.5),      # amr_orange
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


# ── ROS 2 live topics ──────────────────────────────────────────────────────
# The names the fleet actually publishes on. Verified against the publishers in
# src/: fleet_agent_node.py (state, heartbeat), task_allocator_node.py
# (announcements, bids) and dashboard_bridge_node.py (telemetry, reservations).
#
# The default live path is adapters/rosbridge_live_adapter.py, which subscribes
# to these over rosbridge on :9090. adapters/ros2_adapter.py is the direct-rclpy
# alternative and reads this table.
#
# {robot_id} is the ROS namespace (amr_a / amr_b / amr_c), NOT the dashboard's
# single-letter id (A / B / C).

ROS2_TOPICS = {
    "robot_state":  "/{robot_id}/state",
    "heartbeat":    "/{robot_id}/heartbeat",
    "odom":         "/{robot_id}/odom",
    "scan":         "/{robot_id}/scan",
    "task_announce": "/tasks/announcements",
    "task_bid":     "/tasks/bids",
    "reservation":  "/fleet/reservations",
    "telemetry":    "/fleet/telemetry",
}
