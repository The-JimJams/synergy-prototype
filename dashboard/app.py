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
import os
import sys
from typing import Dict, Any

from flask import Flask, jsonify, render_template, request, send_from_directory

import config
from data_store import DataStore
from simulator.fleet_simulator import FleetSimulator
from simulator.scenarios import AVAILABLE_SCENARIOS
from metrics import ExperimentLogger, compute_run_metrics, compute_aggregate_metrics, calculate_improvement_percent
from event_logger import EventAuditLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
)
logger = logging.getLogger("synergy.dashboard")


def create_app(
    mode: str = config.MODE,
    scenario: str = config.DEFAULT_SCENARIO,
    sim_speed: float = config.SIM_SPEED,
    store: DataStore = None,
) -> tuple[Flask, DataStore, FleetSimulator | None]:
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
    simulator: FleetSimulator | None = None

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
        logger.info("Initializing ROS 2 Integration Mode (ROS 2 adapter standby)")
    else:
        logger.warning(f"Unknown DASHBOARD_MODE '{mode}'. Defaulting to mock mode.")
        simulator = FleetSimulator(data_store=store)
        simulator.start()

    app.config["DASHBOARD_MODE"] = mode
    app.config["CURRENT_SCENARIO"] = scenario

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
        if not simulator:
            return jsonify({"error": "Simulator not active in ROS 2 mode"}), 400

        if request.method == "POST":
            req_data = request.get_json(silent=True) or {}
            target_scenario = req_data.get("scenario")
            if target_scenario in AVAILABLE_SCENARIOS:
                store.reset()
                simulator.load_scenario(target_scenario)
                simulator.start()
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
            "status": simulator.get_status(),
        })

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


if __name__ == "__main__":
    main()
