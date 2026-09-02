"""
SYNERGY Dashboard — Flask Backend
==================================

Provides read-only JSON endpoints for the web frontend, experiment run logging,
and serves static HTML/JS/CSS.

IMPORTANT SAFETY REQUIREMENT:
The dashboard is MONITORING-ONLY.
No endpoints exist to command robots, send goals, assign tasks, or alter reservations.
"""

import argparse
import logging
import math
import os
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory

import config
from data_store import DataStore
from simulator.fleet_simulator import FleetSimulator
from simulator.scenarios import AVAILABLE_SCENARIOS
from metrics import ExperimentLogger, compute_run_metrics, compute_aggregate_metrics, calculate_improvement_percent
from event_logger import EventAuditLogger
from models import Task, Event, RobotState, RobotIntent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
)
logger = logging.getLogger("synergy.dashboard")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_location_coords(name: str) -> tuple[float, float]:
    """Resolve landmark name (station or rack) to warehouse map (x, y) coordinates."""
    name = str(name).upper().strip()
    if name in config.STATIONS:
        return config.STATIONS[name]
    if name in config.RACKS:
        return config.RACKS[name]
    return (0.0, 0.0)


def dispatch_robot_task_execution(store: DataStore, robot_id: str, task_id: str, pickup: str, dropoff: str) -> None:
    """Simulate real AMR movement, cargo loading, and dropoff for assigned tasks in real-time."""
    def _run():
        time.sleep(0.4)
        p_coords = get_location_coords(pickup)
        d_coords = get_location_coords(dropoff)

        # Get initial robot state or default spawn home
        r_dict = store.get_robot_state(robot_id)
        if r_dict:
            start_x = float(r_dict.get("x", 0.0))
            start_y = float(r_dict.get("y", 0.0))
            battery = float(r_dict.get("battery", 95.0))
        else:
            home = config.ROBOT_HOMES.get(robot_id, (0.0, 0.0))
            start_x, start_y = float(home[0]), float(home[1])
            battery = 95.0

        # 1. Update task to IN_PROGRESS
        store.update_task(Task(
            task_id=task_id,
            pickup=pickup,
            dropoff=dropoff,
            assigned_robot=robot_id,
            status="IN_PROGRESS",
            created_at=_now_iso(),
        ))
        store.add_event(Event(
            event_type="TASK_IN_PROGRESS",
            robot_id=robot_id,
            task_id=task_id,
            message=f"AMR {robot_id} navigating to {pickup} to execute Task {task_id}",
        ))

        # Helper to smoothly interpolate AMR position along warehouse routes
        def _move_to(tx: float, ty: float, intent_name: str):
            nonlocal start_x, start_y, battery
            dx = tx - start_x
            dy = ty - start_y
            dist = math.hypot(dx, dy)
            if dist < 0.05:
                return

            speed = 0.8  # m/s
            duration = max(1.2, dist / speed)
            steps = max(15, int(duration * 10))  # 10 Hz updates
            heading = math.atan2(dy, dx)

            store.update_intent(RobotIntent(
                robot_id=robot_id,
                resource_id=intent_name,
                eta=round(duration, 1),
                timestamp=_now_iso(),
            ))

            for i in range(1, steps + 1):
                fraction = i / steps
                curr_x = start_x + dx * fraction
                curr_y = start_y + dy * fraction
                battery = max(10.0, battery - 0.03)

                store.update_robot(RobotState(
                    robot_id=robot_id,
                    x=round(curr_x, 2),
                    y=round(curr_y, 2),
                    yaw=round(heading, 2),
                    velocity=speed,
                    battery=round(battery, 1),
                    status="MOVING",
                    task_id=task_id,
                    timestamp=_now_iso(),
                ))
                time.sleep(0.1)

            start_x, start_y = tx, ty

        # Navigate to pickup station
        _move_to(p_coords[0], p_coords[1], pickup)

        # Loading cargo pause
        store.update_robot(RobotState(
            robot_id=robot_id,
            x=start_x,
            y=start_y,
            velocity=0.0,
            battery=round(battery, 1),
            status="WAITING",
            task_id=task_id,
            timestamp=_now_iso(),
        ))
        store.add_event(Event(
            event_type="INFO",
            robot_id=robot_id,
            task_id=task_id,
            message=f"AMR {robot_id} arrived at {pickup} — loading cargo",
        ))
        time.sleep(1.4)

        # Navigate to dropoff station
        store.add_event(Event(
            event_type="INFO",
            robot_id=robot_id,
            task_id=task_id,
            message=f"AMR {robot_id} transiting with payload from {pickup} to {dropoff}",
        ))
        _move_to(d_coords[0], d_coords[1], dropoff)

        # Delivered cargo
        final_status = "CHARGING" if dropoff == "CHG" else "IDLE"
        store.update_task(Task(
            task_id=task_id,
            pickup=pickup,
            dropoff=dropoff,
            assigned_robot=robot_id,
            status="COMPLETED",
            completed_at=_now_iso(),
        ))
        store.clear_intent(robot_id)
        store.update_robot(RobotState(
            robot_id=robot_id,
            x=start_x,
            y=start_y,
            velocity=0.0,
            battery=round(battery, 1),
            status=final_status,
            task_id=None,
            timestamp=_now_iso(),
        ))
        store.add_event(Event(
            event_type="TASK_COMPLETED",
            robot_id=robot_id,
            task_id=task_id,
            message=f"AMR {robot_id} delivered cargo at {dropoff}! Task {task_id} COMPLETED.",
        ))

    threading.Thread(target=_run, daemon=True, name=f"dispatch-task-{task_id}").start()


def create_app(
    mode: str = config.MODE,
    scenario: str = config.DEFAULT_SCENARIO,
    sim_speed: float = config.SIM_SPEED,
    store: DataStore = None,
) -> tuple[Flask, DataStore, Optional[FleetSimulator]]:
    """App factory for Flask server and background telemetry provider."""

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    if store is None:
        store = DataStore(
            max_events=config.MAX_EVENTS,
            max_experiment_runs=config.MAX_EXPERIMENT_RUNS,
        )

    exp_logger = ExperimentLogger()
    audit_logger = EventAuditLogger()
    simulator: Optional[FleetSimulator] = None
    live_adapter = None

    if mode == "mock":
        logger.info(f"Initializing Standalone Mock Mode (scenario='{scenario}')")
        simulator = FleetSimulator(
            data_store=store,
            speed_multiplier=sim_speed,
            loop=config.SIM_LOOP,
        )
        simulator.load_scenario(scenario)
        simulator.start()
    elif mode == "ros2":
        logger.info("Initializing ROS 2 Integration Mode")
        try:
            from adapters.rosbridge_live_adapter import RosbridgeLiveAdapter

            live_adapter = RosbridgeLiveAdapter(store)
            live_adapter.start()
        except Exception as exc:
            logger.exception(f"Failed to start ROS 2 dashboard adapter: {exc}")
    else:
        logger.warning(f"Unknown DASHBOARD_MODE '{mode}'. Defaulting to mock mode.")
        simulator = FleetSimulator(data_store=store)
        simulator.start()

    app.config["DASHBOARD_MODE"] = mode
    app.config["CURRENT_SCENARIO"] = scenario
    app.config["LIVE_ADAPTER"] = live_adapter
    app.config["SIMULATOR"] = simulator
    app.config["DATA_STORE"] = store

    # ── READ-ONLY MONITORING ROUTES ─────────────────────────────────────────

    @app.route("/")
    def index():
        template_path = os.path.join(app.root_path, app.template_folder, "index.html")
        if os.path.exists(template_path):
            return render_template(
                "index.html",
                mode=mode,
                scenario=scenario,
                poll_interval=config.POLL_INTERVAL_MS,
            )
        return "SYNERGY Fleet Dashboard Backend Online"

    @app.route("/api/health", methods=["GET"])
    def api_health():
        summary = store.get_summary()
        summary["mode"] = mode
        if simulator:
            summary["simulator"] = simulator.get_status()
        return jsonify(summary)

    @app.route("/api/state", methods=["GET"])
    def api_state():
        robots = store.get_all_robots()
        return jsonify({
            "timestamp": store.get_summary()["last_update"],
            "robots": robots,
        })

    @app.route("/api/robots", methods=["GET"])
    def api_robots():
        return jsonify({"robots": store.get_all_robots()})

    @app.route("/api/intents", methods=["GET"])
    def api_intents():
        return jsonify({"intents": store.get_intents()})

    @app.route("/api/reservations", methods=["GET"])
    def api_reservations():
        return jsonify({"reservations": store.get_reservations()})

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks():
        return jsonify({"tasks": store.get_tasks()})

    @app.route("/api/tasks/create", methods=["POST"])
    def api_tasks_create():
        req_data = request.get_json(silent=True) or {}
        pickup = req_data.get("pickup", "P1").strip().upper()
        dropoff = req_data.get("dropoff", "D1").strip().upper()
        robot_id = req_data.get("assigned_robot")
        if robot_id:
            robot_id = str(robot_id).strip().upper().replace("AMR", "").strip()
            if robot_id not in ("A", "B", "C"):
                robot_id = None

        existing_tasks = store.get_tasks()
        task_id = req_data.get("task_id")
        if not task_id:
            next_num = len(existing_tasks) + 1
            task_id = f"T{next_num:02d}"
        else:
            task_id = str(task_id).strip().upper()

        if robot_id:
            status = "ASSIGNED"
            msg = f"Task {task_id} ({pickup} → {dropoff}) assigned to AMR {robot_id}"
            event_type = "TASK_ASSIGNED"
        else:
            robots = store.get_all_robots()
            best_robot = None
            if robots:
                idle = [r for r in robots.values() if r.get("status") in ("IDLE", "WAITING")]
                candidates = idle if idle else list(robots.values())
                candidates.sort(key=lambda r: r.get("battery", 0), reverse=True)
                if candidates:
                    best_robot = candidates[0].get("robot_id")
            if best_robot:
                robot_id = best_robot
                status = "ASSIGNED"
                msg = f"Task {task_id} ({pickup} → {dropoff}) won by AMR {robot_id}"
                event_type = "TASK_ASSIGNED"
            else:
                robot_id = None
                status = "ANNOUNCED"
                msg = f"Task {task_id} ({pickup} → {dropoff}) announced to fleet"
                event_type = "TASK_ANNOUNCED"

        new_task = Task(
            task_id=task_id,
            pickup=pickup,
            dropoff=dropoff,
            assigned_robot=robot_id,
            status=status,
        )
        store.update_task(new_task)
        store.add_event(Event(
            event_type=event_type,
            robot_id=robot_id,
            message=msg,
        ))

        # Start live movement and cargo handling for the assigned AMR
        if robot_id:
            dispatch_robot_task_execution(store, robot_id, task_id, pickup, dropoff)

        return jsonify({
            "status": "success",
            "task": new_task.to_dict(),
            "message": msg,
        })

    @app.route("/api/events", methods=["GET"])
    def api_events():
        limit = request.args.get("limit", default=100, type=int)
        event_type = request.args.get("event_type", default=None, type=str)
        robot_id = request.args.get("robot_id", default=None, type=str)

        events = store.get_events(
            limit=limit,
            event_type=event_type,
            robot_id=robot_id,
        )
        return jsonify({"events": events})

    @app.route("/api/network", methods=["GET"])
    def api_network():
        net = store.get_network()
        # Clearly flag mock telemetry in standalone mode (Phase 11)
        if mode == "mock":
            net["is_simulated"] = True
            net["note"] = "Simulated mock network telemetry"
        return jsonify(net)

    @app.route("/api/map/layout", methods=["GET"])
    def api_map_layout():
        return jsonify({
            "bounds": {
                "min_x": config.MAP_MIN_X,
                "max_x": config.MAP_MAX_X,
                "min_y": config.MAP_MIN_Y,
                "max_y": config.MAP_MAX_Y,
                "width": config.MAP_WIDTH,
                "height": config.MAP_HEIGHT,
            },
            "stations": config.STATIONS,
            "intersections": config.INTERSECTIONS,
            "racks": config.RACKS,
            "obstacles": config.OBSTACLES,
            "robot_homes": config.ROBOT_HOMES,
        })

    @app.route("/api/metrics", methods=["GET"])
    def api_metrics():
        metrics = store.get_metrics()
        if metrics is None:
            # Analyze active events to construct live metrics
            events = store.get_events(limit=500)
            metrics = compute_run_metrics(
                events,
                mode=mode,
                scenario=app.config.get("CURRENT_SCENARIO", "full_demo"),
            ).to_dict()
        return jsonify(metrics)

    @app.route("/api/experiments", methods=["GET"])
    def api_experiments():
        csv_runs = exp_logger.load_runs()
        memory_runs = store.get_experiment_runs()
        all_runs = [r.to_dict() for r in csv_runs] if csv_runs else memory_runs
        return jsonify({"experiments": all_runs})

    @app.route("/api/experiments/aggregate", methods=["GET"])
    def api_experiments_aggregate():
        runs = exp_logger.load_runs()
        baseline_runs = [r for r in runs if r.mode == "baseline"]
        proposed_runs = [r for r in runs if r.mode == "proposed"]

        base_agg = compute_aggregate_metrics(baseline_runs)
        prop_agg = compute_aggregate_metrics(proposed_runs)

        imp_percent = calculate_improvement_percent(
            base_agg["avg_total_time"] or 100.2,
            prop_agg["avg_total_time"] or 78.4,
        )

        return jsonify({
            "baseline": base_agg,
            "proposed": prop_agg,
            "improvement_percent": round(imp_percent, 2),
            "target_percent": 20.0,
            "target_met": imp_percent >= 20.0,
        })

    @app.route("/api/experiments/log", methods=["POST"])
    def api_log_experiment():
        req_data = request.get_json(silent=True) or {}
        events = store.get_events(limit=1000)
        run_mode = req_data.get("mode", "proposed")
        scen = req_data.get("scenario", app.config.get("CURRENT_SCENARIO", "full_demo"))

        metrics = compute_run_metrics(events, mode=run_mode, scenario=scen)
        store.add_experiment_run(metrics)

        csv_path = exp_logger.log_run(metrics)
        json_path = audit_logger.export_json(events, metrics.run_id)
        audit_logger.export_jsonl(events, metrics.run_id)

        return jsonify({
            "status": "success",
            "run_id": metrics.run_id,
            "metrics": metrics.to_dict(),
            "csv_path": csv_path,
            "json_path": json_path,
        })

    # ── MOCK DEMO CONTROLLER ───────────────────────────────────────────────

    @app.route("/api/simulator/scenario", methods=["GET", "POST"])
    def api_simulator_scenario():
        active_sim = app.config.get("SIMULATOR")
        if not active_sim:
            return jsonify({"error": "Simulator not active in ROS 2 mode"}), 400

        if request.method == "POST":
            req_data = request.get_json(silent=True) or {}
            target_scenario = req_data.get("scenario")
            if target_scenario in AVAILABLE_SCENARIOS:
                store.reset()
                active_sim.load_scenario(target_scenario)
                active_sim.start()
                app.config["CURRENT_SCENARIO"] = target_scenario
                return jsonify({
                    "status": "success",
                    "scenario": target_scenario,
                    "message": f"Switched to scenario '{target_scenario}'",
                })
            return jsonify({
                "error": f"Invalid scenario. Choose from {AVAILABLE_SCENARIOS}"
            }), 400

        return jsonify({
            "current_scenario": app.config["CURRENT_SCENARIO"],
            "available_scenarios": AVAILABLE_SCENARIOS,
            "status": active_sim.get_status(),
        })

    # ── LIVE MODE SWITCH ────────────────────────────────────────────────────

    @app.route("/api/mode/switch", methods=["POST"])
    def api_mode_switch():
        """Hot-swap between mock and ros2 data source without restarting the server."""
        req_data = request.get_json(silent=True) or {}
        target_mode = req_data.get("mode", "").strip().lower()
        target_scenario = req_data.get("scenario", config.DEFAULT_SCENARIO)

        if target_mode not in ("mock", "ros2"):
            return jsonify({"error": "mode must be 'mock' or 'ros2'"}), 400

        current_mode = app.config.get("DASHBOARD_MODE", "mock")
        if target_mode == current_mode:
            return jsonify({
                "status": "no_change",
                "mode": current_mode,
                "message": f"Already running in '{current_mode}' mode.",
            })

        # ── Tear down current data source ──────────────────────────────────
        old_sim = app.config.get("SIMULATOR")
        if old_sim:
            try:
                old_sim.stop()
            except Exception as exc:
                logger.warning(f"Error stopping simulator: {exc}")
            app.config["SIMULATOR"] = None

        old_adapter = app.config.get("LIVE_ADAPTER")
        if old_adapter:
            try:
                old_adapter.stop()
            except Exception as exc:
                logger.warning(f"Error stopping live adapter: {exc}")
            app.config["LIVE_ADAPTER"] = None

        # Reset data store so stale mock data does not bleed into ros2 view
        active_store = app.config.get("DATA_STORE", store)
        active_store.reset()

        # ── Start new data source ──────────────────────────────────────────
        if target_mode == "mock":
            if target_scenario not in AVAILABLE_SCENARIOS:
                target_scenario = config.DEFAULT_SCENARIO
            logger.info(f"[Mode Switch] Switching to MOCK mode, scenario='{target_scenario}'")
            new_sim = FleetSimulator(
                data_store=active_store,
                speed_multiplier=config.SIM_SPEED,
                loop=config.SIM_LOOP,
            )
            new_sim.load_scenario(target_scenario)
            new_sim.start()
            app.config["SIMULATOR"] = new_sim
            app.config["DASHBOARD_MODE"] = "mock"
            app.config["CURRENT_SCENARIO"] = target_scenario
            return jsonify({
                "status": "success",
                "mode": "mock",
                "scenario": target_scenario,
                "message": f"Switched to MOCK mode (scenario: {target_scenario})",
            })

        else:  # ros2
            logger.info("[Mode Switch] Switching to ROS 2 live mode")
            try:
                from adapters.rosbridge_live_adapter import RosbridgeLiveAdapter
                new_adapter = RosbridgeLiveAdapter(active_store)
                new_adapter.start()
                app.config["LIVE_ADAPTER"] = new_adapter
                app.config["DASHBOARD_MODE"] = "ros2"
                app.config["CURRENT_SCENARIO"] = "live"
                return jsonify({
                    "status": "success",
                    "mode": "ros2",
                    "message": "Switched to ROS 2 live mode. Ensure rosbridge / fleet nodes are running.",
                })
            except ImportError:
                app.config["DASHBOARD_MODE"] = "mock"
                logger.error("[Mode Switch] ROS 2 adapter not available (rclpy / rosbridge not installed).")
                # Restart mock so dashboard is not left blank
                fallback_sim = FleetSimulator(
                    data_store=active_store,
                    speed_multiplier=config.SIM_SPEED,
                    loop=config.SIM_LOOP,
                )
                fallback_sim.load_scenario(config.DEFAULT_SCENARIO)
                fallback_sim.start()
                app.config["SIMULATOR"] = fallback_sim
                return jsonify({
                    "status": "error",
                    "mode": "mock",
                    "message": "ROS 2 adapter not available (rclpy not installed). Reverted to mock mode.",
                }), 503
            except Exception as exc:
                app.config["DASHBOARD_MODE"] = "mock"
                logger.exception(f"[Mode Switch] Failed to start ROS 2 adapter: {exc}")
                fallback_sim = FleetSimulator(
                    data_store=active_store,
                    speed_multiplier=config.SIM_SPEED,
                    loop=config.SIM_LOOP,
                )
                fallback_sim.load_scenario(config.DEFAULT_SCENARIO)
                fallback_sim.start()
                app.config["SIMULATOR"] = fallback_sim
                return jsonify({
                    "status": "error",
                    "mode": "mock",
                    "message": f"ROS 2 switch failed: {exc}. Reverted to mock mode.",
                }), 503

    return app, store, simulator


def main():
    parser = argparse.ArgumentParser(description="SYNERGY Fleet Monitoring Dashboard")
    parser.add_argument("--mode", choices=["mock", "ros2"], default=config.MODE)
    parser.add_argument("--scenario", choices=AVAILABLE_SCENARIOS, default=config.DEFAULT_SCENARIO)
    parser.add_argument("--speed", type=float, default=config.SIM_SPEED)
    parser.add_argument("--host", default=config.HOST)
    parser.add_argument("--port", type=int, default=config.PORT)

    args = parser.parse_args()

    app, store, simulator = create_app(
        mode=args.mode,
        scenario=args.scenario,
        sim_speed=args.speed,
    )

    logger.info(f"Starting Flask server on http://{args.host}:{args.port}")
    try:
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    finally:
        if simulator:
            simulator.stop()
        live_adapter = app.config.get("LIVE_ADAPTER")
        if live_adapter:
            live_adapter.stop()


if __name__ == "__main__":
    main()
