"""
SYNERGY Dashboard — Warehouse Path Planner (mock mode)
======================================================

Plans routes for MOCK mode over the SAME occupancy grid Nav2 uses in live mode
(src/synergy_nav2/maps/warehouse_map.pgm), so a mock run follows the same aisles
the real fleet drives.

Why this exists
---------------
Mock scenarios used to set an absolute pose every 1.5-2.5 s. The robot teleported
2-4 m per step and the map joined those poses with a straight line, which cut
through racking and read as the AMR jumping across the warehouse. Planning a real
route and walking it at a real speed removes the teleporting, gives the map an
actual path to draw, and keeps mock and live visually consistent.

Nothing here runs in live mode: live routes come from Nav2.
"""

from __future__ import annotations

import heapq
import math
import os
from collections import deque
from typing import Dict, List, Optional, Sequence, Tuple

Point = Tuple[float, float]

# Robot geometry, matching the Nav2 footprint in nav2_params_amr_*.yaml
INSCRIBED_RADIUS = 0.26
CIRCUMSCRIBED_RADIUS = math.hypot(0.31, 0.26)
# Keep planned routes at least this far from anything solid. Above the
# circumscribed radius so the drawn path stays visibly clear of the racking.
MIN_CLEARANCE_M = 0.55

_DEFAULT_MAP = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "src", "synergy_nav2", "maps", "warehouse_map.pgm",
    )
)


class WarehouseGrid:
    """Occupancy grid + clearance transform + A* over free space."""

    def __init__(self, pgm_path: str = _DEFAULT_MAP, resolution: float = 0.05,
                 origin: Point = (-10.0, -10.0)):
        self.resolution = resolution
        self.origin_x, self.origin_y = origin
        self.width = 0
        self.height = 0
        self._clearance: List[float] = []
        self.available = False
        try:
            self._load(pgm_path)
            self.available = True
        except Exception:
            # Without the map, callers fall back to straight segments.
            self.available = False

    # ── loading ──────────────────────────────────────────────────────────────

    def _load(self, path: str) -> None:
        data = open(path, "rb").read()
        i, tokens = 0, []
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
        self.width, self.height = int(tokens[1]), int(tokens[2])
        pixels = data[i:]
        occupied = [pixels[r * self.width + c] < 90
                    for r in range(self.height) for c in range(self.width)]
        self._clearance = self._distance_transform(occupied)

    def _distance_transform(self, occupied: Sequence[bool]) -> List[float]:
        """Two-pass chamfer 5-7 distance to the nearest occupied cell, in metres."""
        w, h, near, diag = self.width, self.height, 5, 7
        big = 10 ** 9
        dist = [0 if occupied[k] else big for k in range(w * h)]
        for r in range(h):
            for c in range(w):
                k = r * w + c
                if dist[k] == 0:
                    continue
                best = dist[k]
                for dr, dc, cost in ((-1, 0, near), (0, -1, near), (-1, -1, diag), (-1, 1, diag)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < h and 0 <= cc < w:
                        best = min(best, dist[rr * w + cc] + cost)
                dist[k] = best
        for r in range(h - 1, -1, -1):
            for c in range(w - 1, -1, -1):
                k = r * w + c
                if dist[k] == 0:
                    continue
                best = dist[k]
                for dr, dc, cost in ((1, 0, near), (0, 1, near), (1, 1, diag), (1, -1, diag)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < h and 0 <= cc < w:
                        best = min(best, dist[rr * w + cc] + cost)
                dist[k] = best
        return [d / 5.0 * self.resolution for d in dist]

    # ── coordinate helpers ───────────────────────────────────────────────────

    def to_cell(self, x: float, y: float) -> Tuple[int, int]:
        col = int((x - self.origin_x) / self.resolution)
        row = self.height - 1 - int((y - self.origin_y) / self.resolution)
        return row, col

    def to_world(self, row: int, col: int) -> Point:
        x = col * self.resolution + self.origin_x + self.resolution / 2.0
        y = (self.height - 1 - row) * self.resolution + self.origin_y + self.resolution / 2.0
        return round(x, 3), round(y, 3)

    def clearance(self, x: float, y: float) -> float:
        row, col = self.to_cell(x, y)
        if not (0 <= row < self.height and 0 <= col < self.width):
            return -1.0
        return self._clearance[row * self.width + col]

    def _passable(self, row: int, col: int, limit: float) -> bool:
        return (0 <= row < self.height and 0 <= col < self.width
                and self._clearance[row * self.width + col] >= limit)

    def nearest_free(self, x: float, y: float, limit: float = MIN_CLEARANCE_M,
                     max_radius_m: float = 4.0) -> Optional[Point]:
        """Closest pose with at least `limit` clearance (the point itself if already clear)."""
        row0, col0 = self.to_cell(x, y)
        if self._passable(row0, col0, limit):
            return x, y
        seen = {(row0, col0)}
        queue = deque([(row0, col0)])
        max_cells = max_radius_m / self.resolution
        while queue:
            row, col = queue.popleft()
            if self._passable(row, col, limit):
                return self.to_world(row, col)
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                rr, cc = row + dr, col + dc
                if (rr, cc) in seen:
                    continue
                if math.hypot(cc - col0, rr - row0) > max_cells:
                    continue
                if 0 <= rr < self.height and 0 <= cc < self.width:
                    seen.add((rr, cc))
                    queue.append((rr, cc))
        return None

    # ── planning ─────────────────────────────────────────────────────────────

    def plan(self, start: Point, goal: Point,
             limit: float = MIN_CLEARANCE_M) -> List[Point]:
        """A* through free space. Returns [] if the map is unusable."""
        if not self.available:
            return []
        s = self.nearest_free(*start, limit=limit)
        g = self.nearest_free(*goal, limit=limit)
        if s is None or g is None:
            return []
        r0, c0 = self.to_cell(*s)
        r1, c1 = self.to_cell(*g)
        if (r0, c0) == (r1, c1):
            return [s]

        def heuristic(r: int, c: int) -> float:
            return math.hypot(r - r1, c - c1)

        open_set = [(heuristic(r0, c0), 0.0, (r0, c0))]
        came: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {(r0, c0): None}
        cost = {(r0, c0): 0.0}
        found = False
        while open_set:
            _, g_cost, (r, c) = heapq.heappop(open_set)
            if (r, c) == (r1, c1):
                found = True
                break
            if g_cost > cost.get((r, c), math.inf):
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                rr, cc = r + dr, c + dc
                if not self._passable(rr, cc, limit):
                    continue
                step = g_cost + math.hypot(dr, dc)
                if step < cost.get((rr, cc), math.inf):
                    cost[(rr, cc)] = step
                    came[(rr, cc)] = (r, c)
                    heapq.heappush(open_set, (step + heuristic(rr, cc), step, (rr, cc)))
        if not found:
            return []

        cells: List[Tuple[int, int]] = []
        node: Optional[Tuple[int, int]] = (r1, c1)
        while node is not None:
            cells.append(node)
            node = came[node]
        cells.reverse()
        return self._smooth([self.to_world(r, c) for r in [n[0] for n in cells][:0] for c in []] or
                            [self.to_world(r, c) for r, c in cells], limit)

    def _visible(self, a: Point, b: Point, limit: float) -> bool:
        """True when the straight segment a-b stays clear of obstacles."""
        dist = math.dist(a, b)
        steps = max(2, int(dist / (self.resolution * 0.7)))
        for i in range(steps + 1):
            t = i / steps
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            row, col = self.to_cell(x, y)
            if not self._passable(row, col, limit):
                return False
        return True

    def _smooth(self, pts: List[Point], limit: float) -> List[Point]:
        """String-pulling: drop intermediate points the robot can cut across."""
        if len(pts) < 3:
            return pts
        out = [pts[0]]
        i = 0
        while i < len(pts) - 1:
            j = len(pts) - 1
            while j > i + 1 and not self._visible(pts[i], pts[j], limit):
                j -= 1
            out.append(pts[j])
            i = j
        return out


def densify(waypoints: Sequence[Point], spacing: float = 0.10) -> List[Point]:
    """Resample a polyline to evenly spaced points for smooth playback."""
    if len(waypoints) < 2:
        return list(waypoints)
    out: List[Point] = [tuple(waypoints[0])]
    for a, b in zip(waypoints, waypoints[1:]):
        seg = math.dist(a, b)
        if seg <= 1e-9:
            continue
        n = max(1, int(math.ceil(seg / spacing)))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def path_length(pts: Sequence[Point]) -> float:
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


_GRID: Optional[WarehouseGrid] = None
# Planning a 15 m route costs ~50 ms, and it runs on the scenario thread, so an
# uncached goto visibly stalled playback. Demo legs repeat every loop, so a small
# cache keyed on rounded endpoints makes every repeat instant.
_ROUTE_CACHE: Dict[Tuple[int, int, int, int, int], List[Point]] = {}
_ROUTE_CACHE_LIMIT = 256


def warm_cache(routes) -> None:
    """Pre-plan a set of (start, goal) legs so first playback is not stalled."""
    for start, goal in routes:
        try:
            plan_route(start, goal)
        except Exception:
            pass


def get_grid() -> WarehouseGrid:
    """Process-wide grid; the distance transform is built once."""
    global _GRID
    if _GRID is None:
        _GRID = WarehouseGrid()
    return _GRID


def plan_route(start: Point, goal: Point, spacing: float = 0.10) -> List[Point]:
    """Dense, obstacle-free route from start to goal in warehouse coordinates.

    Falls back to a straight segment only when the map is unavailable, so a
    missing map degrades to the old behaviour instead of breaking the demo.
    """
    key = (int(round(start[0] * 10)), int(round(start[1] * 10)),
           int(round(goal[0] * 10)), int(round(goal[1] * 10)),
           int(round(spacing * 100)))
    cached = _ROUTE_CACHE.get(key)
    if cached is not None:
        return list(cached)

    grid = get_grid()
    route = grid.plan(start, goal)
    dense = densify([start, goal], spacing) if not route else densify(route, spacing)
    if len(_ROUTE_CACHE) >= _ROUTE_CACHE_LIMIT:
        _ROUTE_CACHE.clear()
    _ROUTE_CACHE[key] = dense
    return list(dense)
