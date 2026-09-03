#!/usr/bin/env python3
"""
Runtime verification: every solid warehouse object must be visible to the 2D LiDAR.

Root cause this guards against
------------------------------
Gazebo's ``gpu_lidar`` is a rendering sensor: it returns hits against *visual*
geometry, while the physics engine blocks against *collision* geometry.  When a
model has a solid collision box but no visual geometry at the scan plane
(z = 0.26 m for these AMRs), Nav2's costmap sees free space where the physics
engine has a wall.  The planner then routes straight through the object and the
robot drives into an obstacle it never saw.  That is exactly what the shelf
racks used to do: their only geometry at 0.26 m was six 80 mm uprights.

What this script does
---------------------
Teleports ``amr_blue`` to a probe pose in front of each solid object, reads one
real ``/amr_blue/scan`` message, and checks that the rays aimed into the
object's footprint actually stop at its near face.  Nothing is hardcoded into
the navigation stack -- this only *reads* live sensor data and reports.

Usage
-----
    # terminal 1
    cd gazebo && export GZ_SIM_RESOURCE_PATH="$PWD/simulation/models"
    gz sim -s -r simulation/worlds/warehouse.sdf

    # terminal 2
    python3 gazebo/scripts/verify_lidar_obstacles.py

Exit code 0 = every object is detected, 1 = at least one is transparent.
"""

import json
import math
import os
import subprocess
import sys
import time

MODEL = "amr_blue"
WORLD = "warehouse"
SCAN_TOPIC = f"/{MODEL}/scan"

# LiDAR offset from base_link, from models/amr_blue/model.sdf
LIDAR_DX = 0.14

# Minimum fraction of rays aimed into an object that must actually stop on it.
DETECTION_THRESHOLD = 0.90

# Solid objects that the LiDAR must see, with their world footprints.
#   name:   (centre_x, centre_y, size_x, size_y, probe_x, probe_y)
# The probe pose is a clear spot in front of the object's -Y face.
OBJECTS = [
    ("shelf_rack_NW1",          -4.8,  7.5, 5.0, 1.0, -4.8,  5.4),
    ("shelf_rack_SW1",          -4.8, -3.0, 5.0, 1.0, -4.8, -5.0),
    ("shelf_rack_NE2",           4.8,  3.0, 5.0, 1.0,  4.8,  0.9),
    ("pallet_tower_3",          -8.0, 5.25, 1.4, 1.2, -8.0,  3.4),
    ("pallet_tower_1",          -5.2, -7.3, 1.4, 1.2, -5.2, -9.2),
    ("green_dumpster_container", -2.8, -7.3, 1.2, 0.8, -2.8, -9.0),
    ("blocked_aisle_obstacle",  -0.2, 0.75, 0.8, 1.2, -0.2, -1.4),
    ("north_wall",               0.0, 10.0, 20.0, 0.15, 0.0,  8.6),
]


def gz(*args, **kw):
    env = dict(os.environ, GZ_IP=os.environ.get("GZ_IP", "127.0.0.1"))
    return subprocess.run(["gz", *args], capture_output=True, text=True, env=env, **kw)


def teleport(x, y, yaw=0.0):
    """Move the robot with Gazebo's own set_pose service (simulation control, not navigation)."""
    req = (
        f'name: "{MODEL}", position: {{x: {x}, y: {y}, z: 0.05}}, '
        f"orientation: {{x: 0, y: 0, z: {math.sin(yaw / 2)}, w: {math.cos(yaw / 2)}}}"
    )
    return gz(
        "service", "-s", f"/world/{WORLD}/set_pose",
        "--reqtype", "gz.msgs.Pose", "--reptype", "gz.msgs.Boolean",
        "--timeout", "3000", "--req", req,
    )


def read_scan():
    res = gz("topic", "-e", "-t", SCAN_TOPIC, "-n", "1", "--json-output", timeout=30)
    if not res.stdout.strip():
        raise RuntimeError(f"no message on {SCAN_TOPIC}; is the Gazebo server running?")
    d = json.loads(res.stdout)
    return [float(v) for v in d["ranges"]], d["angleMin"], d["angleStep"]


def check(name, cx, cy, sx, sy, px, py):
    """Return (rays_aimed_at_object, rays_that_stopped_on_it)."""
    teleport(px, py)
    time.sleep(2.0)          # let the sensor re-render from the new pose
    ranges, amin, astep = read_scan()

    lx, ly = px + LIDAR_DX, py
    near_y = cy - sy / 2.0   # the face pointing at the probe pose
    x_lo, x_hi = cx - sx / 2.0, cx + sx / 2.0

    aimed = blocked = 0
    for i, rng in enumerate(ranges):
        a = amin + i * astep
        dx, dy = math.cos(a), math.sin(a)
        if dy <= 1e-6:
            continue
        t = (near_y - ly) / dy               # range at which the ray reaches the face
        if t <= 0:
            continue
        if not (x_lo <= lx + dx * t <= x_hi):
            continue                          # ray misses the footprint entirely
        aimed += 1
        if math.isfinite(rng) and rng <= t + 0.15:
            blocked += 1
    return aimed, blocked


def main():
    print(f"Probing {len(OBJECTS)} warehouse objects against live {SCAN_TOPIC} data\n")
    failures = []
    for name, cx, cy, sx, sy, px, py in OBJECTS:
        try:
            aimed, blocked = check(name, cx, cy, sx, sy, px, py)
        except Exception as exc:                      # noqa: BLE001 - report and continue
            print(f"  {name:28s} ERROR: {exc}")
            failures.append(name)
            continue
        if aimed == 0:
            print(f"  {name:28s} SKIP  (probe pose sees no part of the footprint)")
            continue
        frac = blocked / aimed
        ok = frac >= DETECTION_THRESHOLD
        print(f"  {name:28s} {'PASS' if ok else 'FAIL'}  "
              f"{blocked:4d}/{aimed:4d} rays stopped on the object ({frac * 100:5.1f}%)")
        if not ok:
            failures.append(name)

    print()
    if failures:
        print(f"FAIL: {len(failures)} object(s) are transparent to the LiDAR: {', '.join(failures)}")
        print("These will be missing from the Nav2 costmap while still blocking physically.")
        return 1
    print("PASS: every solid object is visible to the LiDAR at the scan plane.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
