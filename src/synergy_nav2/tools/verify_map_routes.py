#!/usr/bin/env python3
"""
Offline check that the warehouse map + Nav2 costmap configuration admit real
warehouse routes -- aisles, turns and intersections -- rather than straight lines.

It reads the same files Nav2 reads at runtime:

  * ``maps/warehouse_map.yaml`` / ``.pgm``  -- the static layer
  * ``config/nav2_params_amr_a.yaml``       -- footprint, inflation_radius,
                                               cost_scaling_factor, planner plugin

and reproduces what ``nav2_costmap_2d`` builds from them:

  * inscribed / circumscribed radii derived from the footprint polygon
  * an inflation layer, with everything inside the inscribed radius lethal
  * NavFn's planning rule -- cost >= 253 is not traversable

then runs the same search NavFn runs (Dijkstra, since ``use_astar: false``)
between the waypoints the task allocator actually dispatches to.

For each route it reports the planned length against the straight-line distance
and how many turns the route contains, and flags any straight line that would cut
through occupied space.  A route whose plan is materially longer than the straight
line, with several turns, is a route through the aisles.

    python3 src/synergy_nav2/tools/verify_map_routes.py

Exit code 0 = every route plans and none of them is a straight line through a rack.
"""

import heapq
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
MAP_YAML = os.path.join(PKG, "maps", "warehouse_map.yaml")
PARAMS = os.path.join(PKG, "config", "nav2_params_amr_a.yaml")

SRC = os.path.dirname(PKG)          # <workspace>/src
ALLOCATOR = os.path.join(SRC, "task_allocator", "task_allocator", "task_allocator_node.py")


def load_waypoints():
    """Read WAYPOINTS straight out of the task allocator -- one source of truth.

    Parsed rather than imported so this runs without ROS 2 on the path.
    """
    import ast
    with open(ALLOCATOR) as fh:
        tree = ast.parse(fh.read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "WAYPOINTS" for t in node.targets
        ):
            raw = ast.literal_eval(node.value)
            # Keep the canonical upper-case keys; the lower-case ones are aliases.
            return {k: tuple(map(float, v)) for k, v in raw.items()}
    raise RuntimeError(f"WAYPOINTS not found in {ALLOCATOR}")


WAYPOINTS = load_waypoints()

# Routes exercised by the demo, expressed in allocator waypoint names.
ROUTES = [
    ("dock_a", "zone_b"),   # the startup demo task
    ("P1", "D1"),           # pickup -> dropoff, the length of the warehouse
    ("P2", "CHG"),          # south-west pickup -> charging bay
    ("S1", "S8"),           # opposite corners of the rack field
    ("S3", "S6"),           # across the central aisles
    ("I1", "I2"),           # between the two shared intersections
    ("dock_b", "D1"),       # AMR B spawn -> dropoff
    ("dock_c", "P1"),       # AMR C spawn -> pickup
]

# NavFn treats anything at or above INSCRIBED_INFLATED_OBSTACLE as untraversable.
LETHAL_COST = 253


# ── Loading the real configuration ───────────────────────────────────────────

def load_map():
    with open(MAP_YAML) as fh:
        text = fh.read()

    def field(name, default=None):
        m = re.search(rf"^{name}:\s*(.+)$", text, re.M)
        return m.group(1).strip() if m else default

    image = field("image")
    resolution = float(field("resolution"))
    origin = [float(v) for v in field("origin").strip("[]").split(",")]
    occupied_thresh = float(field("occupied_thresh", "0.65"))
    negate = int(field("negate", "0"))

    path = os.path.join(os.path.dirname(MAP_YAML), image)
    with open(path, "rb") as fh:
        data = fh.read()

    # Minimal binary PGM (P5) reader
    tokens, i = [], 0
    while len(tokens) < 4:
        while data[i:i + 1].isspace():
            i += 1
        if data[i:i + 1] == b"#":
            while data[i:i + 1] not in (b"\n", b""):
                i += 1
            continue
        start = i
        while not data[i:i + 1].isspace():
            i += 1
        tokens.append(data[start:i])
    i += 1
    assert tokens[0] == b"P5", "expected a binary PGM"
    width, height, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    pixels = data[i:i + width * height]

    # ROS map_server: occupancy = (maxval - value) / maxval, unless negate.
    #
    # Row order matters. PGM row 0 is the TOP of the image, i.e. maximum Y, while
    # the occupancy grid's row 0 is minimum Y -- map_server writes image row j to
    # grid row (height - 1 - j). Reading the raster straight through mirrors the
    # map about y = origin_y + height/2, which is invisible in a vertically
    # symmetric warehouse except at the few asymmetric spots.
    occupied = bytearray(width * height)
    for row in range(height):
        src = row * width
        dst = (height - 1 - row) * width
        for col in range(width):
            value = pixels[src + col]
            p = value / maxval if negate else (maxval - value) / maxval
            occupied[dst + col] = 1 if p > occupied_thresh else 0

    return {
        "w": width, "h": height, "res": resolution,
        "origin": origin, "occ": occupied, "image": image,
    }


def load_params():
    with open(PARAMS) as fh:
        text = fh.read()

    footprint_txt = re.search(r"footprint:\s*\"(\[\[.*?\]\])\"", text).group(1)
    points = [tuple(float(v) for v in pair.split(","))
              for pair in re.findall(r"\[(-?[\d.]+,\s*-?[\d.]+)\]", footprint_txt)]

    gc = text.index("global_costmap:")
    tail = text[gc:]
    inflation_radius = float(re.search(r"inflation_radius:\s*([\d.]+)", tail).group(1))
    cost_scaling = float(re.search(r"cost_scaling_factor:\s*([\d.]+)", tail).group(1))
    resolution = float(re.search(r"resolution:\s*([\d.]+)", tail).group(1))
    use_astar = re.search(r"use_astar:\s*(\w+)", text).group(1).lower() == "true"

    inscribed = min(
        _point_to_segment(0.0, 0.0, *points[i], *points[(i + 1) % len(points)])
        for i in range(len(points))
    )
    circumscribed = max(math.hypot(px, py) for px, py in points)
    return {
        "footprint": points, "inscribed": inscribed, "circumscribed": circumscribed,
        "inflation_radius": inflation_radius, "cost_scaling": cost_scaling,
        "resolution": resolution, "use_astar": use_astar,
    }


def _point_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    denom = dx * dx + dy * dy
    t = 0.0 if denom == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


# ── Costmap construction (mirrors nav2_costmap_2d's inflation layer) ─────────

def build_costmap(grid, params):
    """Return (cost[], distance_in_cells[]) using a brushfire distance transform."""
    w, h, res = grid["w"], grid["h"], grid["res"]
    occ = grid["occ"]
    inflation_cells = int(math.ceil(params["inflation_radius"] / res))

    INF = float("inf")
    dist = [INF] * (w * h)
    queue = []
    for idx, is_occ in enumerate(occ):
        if is_occ:
            dist[idx] = 0.0
            queue.append((0.0, idx))
    heapq.heapify(queue)

    max_dist = inflation_cells + 1
    while queue:
        d, idx = heapq.heappop(queue)
        if d > dist[idx]:
            continue
        if d > max_dist:
            continue
        cx, cy = idx % w, idx // w
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                nd = d + (1.0 if dx == 0 or dy == 0 else math.sqrt(2.0))
                nidx = ny * w + nx
                if nd < dist[nidx]:
                    dist[nidx] = nd
                    heapq.heappush(queue, (nd, nidx))

    inscribed = params["inscribed"]
    scaling = params["cost_scaling"]
    cost = bytearray(w * h)
    for idx in range(w * h):
        d_m = dist[idx] * res
        if occ[idx]:
            cost[idx] = 254
        elif d_m <= inscribed:
            cost[idx] = 253
        elif d_m <= params["inflation_radius"]:
            factor = math.exp(-scaling * (d_m - inscribed))
            cost[idx] = int((253 - 1) * factor)
        else:
            cost[idx] = 0
    return cost, dist


# ── Planning ─────────────────────────────────────────────────────────────────

def world_to_cell(grid, x, y):
    cx = int((x - grid["origin"][0]) / grid["res"])
    cy = int((y - grid["origin"][1]) / grid["res"])
    return cx, cy


def cell_to_world(grid, cx, cy):
    return (grid["origin"][0] + (cx + 0.5) * grid["res"],
            grid["origin"][1] + (cy + 0.5) * grid["res"])


def plan(grid, cost, start, goal):
    """Dijkstra over traversable cells, weighted by inflation cost like NavFn."""
    w, h = grid["w"], grid["h"]
    sx, sy = world_to_cell(grid, *start)
    gx, gy = world_to_cell(grid, *goal)
    s_idx, g_idx = sy * w + sx, gy * w + gx

    if cost[s_idx] >= LETHAL_COST:
        return None, f"start {start} is in lethal space (cost={cost[s_idx]})"
    if cost[g_idx] >= LETHAL_COST:
        return None, f"goal {goal} is in lethal space (cost={cost[g_idx]})"

    INF = float("inf")
    dist = {s_idx: 0.0}
    prev = {}
    pq = [(0.0, s_idx)]
    seen = set()
    while pq:
        d, idx = heapq.heappop(pq)
        if idx in seen:
            continue
        seen.add(idx)
        if idx == g_idx:
            break
        cx, cy = idx % w, idx // w
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                nidx = ny * w + nx
                if cost[nidx] >= LETHAL_COST:
                    continue
                step = 1.0 if dx == 0 or dy == 0 else math.sqrt(2.0)
                # NavFn biases away from inflated cells rather than ignoring them.
                nd = d + step * (1.0 + cost[nidx] / 100.0)
                if nd < dist.get(nidx, INF):
                    dist[nidx] = nd
                    prev[nidx] = idx
                    heapq.heappush(pq, (nd, nidx))

    if g_idx not in dist:
        return None, "no traversable route exists"

    path, idx = [], g_idx
    while idx != s_idx:
        path.append(cell_to_world(grid, idx % w, idx // w))
        idx = prev[idx]
    path.append(cell_to_world(grid, sx, sy))
    path.reverse()
    return path, None


def path_length(path):
    return sum(math.dist(path[i], path[i + 1]) for i in range(len(path) - 1))


def count_turns(path, step=12, threshold_deg=25.0):
    """Heading changes above the threshold, sampled every `step` points."""
    pts = path[::step]
    if len(pts) < 3:
        return 0
    turns, last = 0, None
    for i in range(len(pts) - 1):
        heading = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
        if last is not None:
            delta = abs(math.degrees(math.atan2(math.sin(heading - last),
                                                math.cos(heading - last))))
            if delta > threshold_deg:
                turns += 1
        last = heading
    return turns


def straight_line_blocked(grid, cost, a, b):
    """Would a straight line from a to b pass through lethal space?"""
    steps = max(2, int(math.dist(a, b) / (grid["res"] / 2)))
    for i in range(steps + 1):
        t = i / steps
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t
        cx, cy = world_to_cell(grid, x, y)
        if not (0 <= cx < grid["w"] and 0 <= cy < grid["h"]):
            return True
        if cost[cy * grid["w"] + cx] >= LETHAL_COST:
            return True
    return False


def main():
    grid = load_map()
    params = load_params()

    span_x = grid["w"] * grid["res"]
    span_y = grid["h"] * grid["res"]
    print("MAP")
    print(f"  image           {grid['image']}  {grid['w']} x {grid['h']} px @ {grid['res']} m/px")
    print(f"  world extent    {span_x:.1f} m x {span_y:.1f} m  "
          f"(x {grid['origin'][0]:.1f}..{grid['origin'][0] + span_x:.1f}, "
          f"y {grid['origin'][1]:.1f}..{grid['origin'][1] + span_y:.1f})")
    occupied = sum(grid["occ"])
    print(f"  occupied        {occupied} cells = {occupied * grid['res'] ** 2:.1f} m^2 "
          f"({100 * occupied / (grid['w'] * grid['h']):.1f}% of the floor)")

    print("\nCOSTMAP (from nav2_params_amr_a.yaml)")
    print(f"  footprint       {params['footprint']}")
    print(f"  inscribed r     {params['inscribed']:.3f} m   circumscribed r {params['circumscribed']:.3f} m")
    print(f"  inflation r     {params['inflation_radius']:.2f} m   cost_scaling {params['cost_scaling']}")
    print(f"  planner         NavFn ({'A*' if params['use_astar'] else 'Dijkstra'})")

    cost, _ = build_costmap(grid, params)
    free = sum(1 for c in cost if c < LETHAL_COST)
    print(f"  traversable     {free} cells = {free * grid['res'] ** 2:.1f} m^2 "
          f"({100 * free / len(cost):.1f}% of the floor)")

    print("\nWAYPOINT CLEARANCE (every Nav2 goal must be a pose the robot can occupy)")
    _, dist_cells = build_costmap(grid, params)
    bad_waypoints = []
    for name in sorted({k.upper() for k in WAYPOINTS}):
        key = name if name in WAYPOINTS else name.lower()
        if key not in WAYPOINTS:
            continue
        x, y = WAYPOINTS[key]
        cx, cy = world_to_cell(grid, x, y)
        idx = cy * grid["w"] + cx
        # The brushfire stops expanding past the inflation radius, so anything it
        # never reached is simply further away than that.
        raw = dist_cells[idx]
        c = cost[idx]
        ok = c < LETHAL_COST
        if not ok:
            bad_waypoints.append(f"{name} ({x}, {y})")
        if math.isinf(raw):
            clearance = f'> {params["inflation_radius"]:.2f} m'
        else:
            clearance = f'{raw * grid["res"]:.2f} m'
        flag = "OK  " if ok else "BAD "
        print(f"  {flag}{name:<8} ({x:6.2f},{y:6.2f})  clearance {clearance:>9}  cost {c:3d}")

    if bad_waypoints:
        print(f"\n  {len(bad_waypoints)} waypoint(s) sit in lethal space: {', '.join(bad_waypoints)}")

    print("\nROUTES")
    header = f"  {'route':<18}{'straight':>10}{'planned':>10}{'ratio':>8}{'turns':>7}  note"
    print(header)
    print("  " + "-" * (len(header) - 2))

    failures, straight_routes = [], []
    for a_name, b_name in ROUTES:
        a, b = WAYPOINTS[a_name], WAYPOINTS[b_name]
        path, err = plan(grid, cost, a, b)
        label = f"{a_name} -> {b_name}"
        if path is None:
            print(f"  {label:<18}{'':>10}{'FAIL':>10}{'':>8}{'':>7}  {err}")
            failures.append(label)
            continue

        straight = math.dist(a, b)
        planned = path_length(path)
        turns = count_turns(path)
        blocked = straight_line_blocked(grid, cost, a, b)
        note = "straight line crosses obstacles" if blocked else "straight line is clear"
        print(f"  {label:<18}{straight:>9.2f}m{planned:>9.2f}m"
              f"{planned / straight:>8.2f}{turns:>7}  {note}")

        # A route that must detour but plans as a straight line is the failure mode.
        if blocked and planned / straight < 1.02:
            straight_routes.append(label)

    print()
    if bad_waypoints:
        print(f"FAIL: {len(bad_waypoints)} waypoint(s) are not valid Nav2 goals.")
        return 1
    if failures:
        print(f"FAIL: {len(failures)} route(s) could not be planned: {', '.join(failures)}")
        return 1
    if straight_routes:
        print(f"FAIL: {len(straight_routes)} route(s) planned straight through obstacles.")
        return 1
    print("PASS: every route plans through free space; routes that need to detour do detour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
