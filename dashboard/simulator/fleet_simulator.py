"""
SYNERGY Dashboard — Fleet Simulator
====================================

The FleetSimulator runs scenario steps in a background thread and pushes
normalized telemetry objects into the central DataStore.

Key features:
1. Thread-safe execution using a background worker thread.
2. Configurable playback speed multiplier (`speed_multiplier`).
3. Optional looping mode (`loop=True`).
4. Dispatches action dictionaries to DataStore methods cleanly.
5. Injects fresh ISO-8601 timestamps into created models.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Union, List, Dict, Any

from data_store import DataStore
from models import (
    RobotState,
    RobotIntent,
    Reservation,
    Task,
    Event,
    NetworkStatus,
    ExperimentMetrics,
)
from simulator.scenarios import get_scenario
from simulator.pathfinder import plan_route, path_length, warm_cache

logger = logging.getLogger(__name__)

# Motion model for MOCK playback.
# Scenario steps used to set an absolute pose every 1.5-2.5 s, so a robot
# teleported several metres per step and the map joined those poses with a
# straight line through the racking. A "goto" instead plans a route over the
# real occupancy grid and walks it here at a real speed, publishing at
# MOTION_TICK_HZ, so mock motion is continuous and follows the same aisles the
# live fleet uses.
MOTION_TICK_HZ = 20.0
DEFAULT_CRUISE_SPEED = 0.55        # m/s, just under Nav2's max_vel_x of 0.6
MAX_YAW_RATE = 2.2                 # rad/s, in-place turn before setting off
ARRIVAL_EPS = 0.02


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FleetSimulator:
    """Replays mock telemetry scenarios into a DataStore instance."""

    def __init__(
        self,
        data_store: DataStore,
        speed_multiplier: float = 1.0,
        loop: bool = True,
    ):
        self.data_store = data_store
        self.speed_multiplier = max(0.1, speed_multiplier)
        self.loop = loop

        self._scenario_name: str = "full_demo"
        self._steps: List[Dict[str, Any]] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_step_index: int = 0
        self._is_running: bool = False

        # robot_id -> live motion state for the goto motion model
        self._motion: Dict[str, Dict[str, Any]] = {}
        self._motion_lock = threading.Lock()
        self._motion_thread: Optional[threading.Thread] = None

        # Pre-load default scenario
        self.load_scenario(self._scenario_name)

    def load_scenario(self, scenario_input: Union[str, List[Dict[str, Any]]]) -> None:
        """Load a scenario by name or by passing a step list directly."""
        if self._is_running:
            self.stop()

        if isinstance(scenario_input, str):
            self._scenario_name = scenario_input
            self._steps = get_scenario(scenario_input)
        else:
            self._scenario_name = "custom"
            self._steps = scenario_input

        self._current_step_index = 0
        self._prewarm_routes()

    def _prewarm_routes(self) -> None:
        """Plan this scenario's legs up front so playback never stalls on the planner."""
        legs, last = [], {}
        for step in self._steps:
            for action in step.get("actions", []):
                data = action.get("data", {})
                rid = data.get("robot_id")
                if not rid:
                    continue
                if action.get("type") in ("goto", "update_robot"):
                    goal = (float(data.get("x", 0.0)), float(data.get("y", 0.0)))
                    if action.get("type") == "goto" and rid in last:
                        legs.append((last[rid], goal))
                    last[rid] = goal
        threading.Thread(target=warm_cache, args=(legs,), daemon=True,
                         name="RouteWarmup").start()

    def start(self) -> None:
        """Start background simulation thread."""
        if self._is_running:
            return

        self._stop_event.clear()
        self._is_running = True
        self._thread = threading.Thread(
            target=self._run_loop, name="FleetSimulatorThread", daemon=True
        )
        self._thread.start()
        self._motion_thread = threading.Thread(
            target=self._motion_loop, name="FleetMotionThread", daemon=True
        )
        self._motion_thread.start()
        logger.info(f"FleetSimulator started scenario '{self._scenario_name}'")

    def stop(self) -> None:
        """Signal simulator thread to stop and wait for termination."""
        if not self._is_running:
            return

        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        if self._motion_thread and self._motion_thread.is_alive():
            self._motion_thread.join(timeout=2.0)
        with self._motion_lock:
            self._motion.clear()
        self._is_running = False
        logger.info("FleetSimulator stopped")

    def is_running(self) -> bool:
        return self._is_running

    def get_status(self) -> Dict[str, Any]:
        """Return status information for telemetry inspection."""
        return {
            "running": self._is_running,
            "scenario": self._scenario_name,
            "current_step": self._current_step_index,
            "total_steps": len(self._steps),
            "speed_multiplier": self.speed_multiplier,
            "loop": self.loop,
        }

    def _run_loop(self) -> None:
        """Main loop executed in background thread."""
        try:
            while not self._stop_event.is_set():
                for idx, step in enumerate(self._steps):
                    if self._stop_event.is_set():
                        break

                    self._current_step_index = idx
                    delay = step.get("delay", 0.0)

                    if delay > 0:
                        scaled_delay = delay / self.speed_multiplier
                        # Sleep in small increments so stop() is responsive, but
                        # never overshoot the requested delay: the previous
                        # version always burned a whole 50 ms chunk per step, so
                        # a step could not run faster than 50 ms no matter what
                        # speed_multiplier said and fast playback was capped at
                        # ~20 steps/second.
                        deadline = time.monotonic() + scaled_delay
                        while not self._stop_event.is_set():
                            remaining = deadline - time.monotonic()
                            if remaining <= 0:
                                break
                            time.sleep(min(0.05, remaining))

                    if self._stop_event.is_set():
                        break

                    # Dispatch step actions
                    actions = step.get("actions", [])
                    for action in actions:
                        self._dispatch_action(action)

                if not self.loop or self._stop_event.is_set():
                    break

        except Exception as e:
            logger.exception(f"Unhandled error in FleetSimulator loop: {e}")
        finally:
            self._is_running = False

    # ── Motion model (mock only) ─────────────────────────────────────────────

    def _motion_loop(self) -> None:
        """Advance every moving robot along its planned route at MOTION_TICK_HZ."""
        dt = 1.0 / MOTION_TICK_HZ
        while not self._stop_event.is_set():
            try:
                self._tick_motion(dt * self.speed_multiplier)
            except Exception as exc:            # never kill the demo on one bad tick
                logger.debug(f"motion tick error: {exc}")
            time.sleep(dt)

    def _tick_motion(self, dt: float) -> None:
        with self._motion_lock:
            active = [(rid, m) for rid, m in self._motion.items() if not m.get("done")]
        for rid, m in active:
            self._advance(rid, m, dt)

    def _advance(self, rid: str, m: Dict[str, Any], dt: float) -> None:
        path = m["path"]
        idx = m["idx"]
        if idx >= len(path):
            self._finish_leg(rid, m)
            return

        # Turn toward the next point before driving, so the heading the map
        # draws matches the direction of travel instead of snapping on arrival.
        tx, ty = path[idx]
        heading = math.atan2(ty - m["y"], tx - m["x"])
        yaw_err = (heading - m["yaw"] + math.pi) % (2 * math.pi) - math.pi
        max_turn = MAX_YAW_RATE * dt
        if abs(yaw_err) > max_turn:
            m["yaw"] += max_turn * (1 if yaw_err > 0 else -1)
            # Creep while turning sharply rather than pivoting on the spot.
            travel = m["speed"] * dt * 0.15
        else:
            m["yaw"] = heading
            travel = m["speed"] * dt

        # Walk the polyline, consuming waypoints until this tick's budget is spent.
        while travel > ARRIVAL_EPS and m["idx"] < len(path):
            tx, ty = path[m["idx"]]
            gap = math.hypot(tx - m["x"], ty - m["y"])
            if gap <= travel:
                m["x"], m["y"] = tx, ty
                m["idx"] += 1
                travel -= gap
            else:
                m["x"] += (tx - m["x"]) * (travel / gap)
                m["y"] += (ty - m["y"]) * (travel / gap)
                travel = 0.0

        m["battery"] = max(5.0, m["battery"] - 0.02 * dt)
        remaining = path[m["idx"]:]
        arrived = m["idx"] >= len(path)

        self.data_store.update_robot(RobotState(
            robot_id=rid,
            x=round(m["x"], 3),
            y=round(m["y"], 3),
            yaw=round(m["yaw"], 4),
            velocity=0.0 if arrived else round(m["speed"], 2),
            battery=round(m["battery"], 1),
            status=m.get("arrive_status", "IDLE") if arrived else m.get("status", "MOVING"),
            task_id=m.get("task_id"),
            timestamp=_now_iso(),
        ))
        # Shrink the drawn route as the robot consumes it: the line always shows
        # what is still ahead, not the whole leg.
        self.data_store.update_path(rid, remaining if not arrived else [])
        if arrived:
            self._finish_leg(rid, m)

    def _finish_leg(self, rid: str, m: Dict[str, Any]) -> None:
        m["done"] = True
        self.data_store.clear_path(rid)
        for action in m.get("on_arrive") or []:
            try:
                self._dispatch_action(action)
            except Exception as exc:
                logger.debug(f"on_arrive dispatch failed: {exc}")

    def _start_goto(self, data: Dict[str, Any]) -> None:
        """Plan a route and begin driving. Replaces any leg already in flight."""
        rid = data.get("robot_id")
        if not rid:
            return
        goal = (float(data.get("x", 0.0)), float(data.get("y", 0.0)))

        existing = self.data_store.get_robot_state(rid)
        if isinstance(existing, dict) and existing:
            sx, sy = float(existing.get("x", 0.0)), float(existing.get("y", 0.0))
            yaw = float(existing.get("yaw", 0.0))
            battery = float(existing.get("battery", 100.0))
        else:
            sx, sy, yaw, battery = goal[0], goal[1], 0.0, 100.0

        # Planning runs here on the scenario thread only for the first, cheap
        # check; a cache miss costs ~50 ms, which visibly stalls playback and
        # made fast-forward timing non-deterministic. Hand the plan to the
        # motion thread and start from a placeholder it replaces on its first
        # tick, so scenario pacing never depends on planner cost.
        route = plan_route((sx, sy), goal)
        with self._motion_lock:
            self._motion[rid] = {
                "path": route,
                "idx": 0,
                "x": sx, "y": sy, "yaw": yaw,
                "battery": float(data.get("battery", battery)),
                "speed": float(data.get("speed", DEFAULT_CRUISE_SPEED)),
                "status": data.get("status", "MOVING"),
                "arrive_status": data.get("arrive_status", "IDLE"),
                "task_id": data.get("task_id"),
                "on_arrive": data.get("on_arrive") or [],
                "done": False,
            }
        self.data_store.update_path(rid, route)

    def _stop_robot(self, rid: str) -> None:
        with self._motion_lock:
            m = self._motion.get(rid)
            if m:
                m["done"] = True
        self.data_store.clear_path(rid)

    def _dispatch_action(self, action: Dict[str, Any]) -> None:
        """Dispatch a single action to the DataStore."""
        atype = action.get("type")
        data = dict(action.get("data", {}))

        if atype == "goto":
            self._start_goto(data)
            return

        if atype == "stop_robot":
            rid = data.get("robot_id")
            if rid:
                self._stop_robot(rid)
            return

        if atype == "update_robot":
            rid = data.get("robot_id")
            # An explicit pose placement cancels any leg in flight, otherwise the
            # motion thread would immediately drag the robot back onto its route.
            if rid:
                self._stop_robot(rid)
            # If robot is actively executing an assigned task, do not overwrite with static scenario positions
            active_tasks = self.data_store.get_tasks()
            if any(t.get("assigned_robot") == rid and t.get("status") == "IN_PROGRESS" for t in active_tasks):
                return

            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_robot(RobotState.from_dict(data))

        elif atype == "update_intent":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_intent(RobotIntent.from_dict(data))

        elif atype == "clear_intent":
            rid = data.get("robot_id")
            if rid:
                self.data_store.clear_intent(rid)

        elif atype == "update_reservation":
            if "start_time" not in data and data.get("status") == "ACTIVE":
                data["start_time"] = _now_iso()
            self.data_store.update_reservation(Reservation.from_dict(data))

        elif atype == "release_reservation":
            resource_id = data.get("resource_id")
            if resource_id:
                self.data_store.release_reservation(resource_id)

        elif atype == "update_task":
            if "created_at" not in data:
                data["created_at"] = _now_iso()
            if data.get("status") == "COMPLETED" and "completed_at" not in data:
                data["completed_at"] = _now_iso()
            self.data_store.update_task(Task.from_dict(data))

        elif atype == "add_event":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.add_event(Event.from_dict(data))

        elif atype == "update_network":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_network(NetworkStatus.from_dict(data))

        elif atype == "update_metrics":
            if "timestamp" not in data:
                data["timestamp"] = _now_iso()
            self.data_store.update_metrics(ExperimentMetrics.from_dict(data))

        else:
            logger.warning(f"Unknown simulator action type: '{atype}'")
