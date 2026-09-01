"""
SYNERGY Dashboard — Flask Backend
==================================

Provides read-only JSON endpoints for the web frontend and serves the static HTML/JS/CSS.

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
        # ROS 2 adapter will be initialized separately in Phase 16
    else:
        logger.warning(f"Unknown DASHBOARD_MODE '{mode}'. Defaulting to mock mode.")
        simulator = FleetSimulator(data_store=store)
        simulator.start()

    # Store mode on app config for endpoints
    app.config["DASHBOARD_MODE"] = mode
    app.config["CURRENT_SCENARIO"] = scenario

    # ── READ-ONLY ROUTES ───────────────────────────────────────────────────

    @app.route("/")
    def index():
        """Serve main single-page monitoring dashboard."""
        if os.path.exists(os.path.join(app.template_folder, "index.html")):
            return render_template(
                "index.html",
                mode=mode,
                scenario=scenario,
                poll_interval=config.POLL_INTERVAL_MS,
            )
        return """
        <!DOCTYPE html>
        <html>
        <head><title>SYNERGY Fleet Dashboard</title></head>
        <body style="font-family: sans-serif; padding: 20px; background: #0f172a; color: #f8fafc;">
            <h1>SYNERGY AMR Fleet Dashboard Backend</h1>
            <p>Status: <strong>ONLINE</strong> (Mode: <code>""" + mode + """</code>)</p>
            <p>API endpoints available at <code>/api/state</code>, <code>/api/events</code>, etc.</p>
        </body>
        </html>
        """

    @app.route("/api/health", methods=["GET"])
    def api_health():
        """Backend health & runtime status."""
        summary = store.get_summary()
        summary["mode"] = mode
        if simulator:
            summary["simulator"] = simulator.get_status()
        return jsonify(summary)

    @app.route("/api/state", methods=["GET"])
    def api_state():
        """Current normalized state of all robots."""
        robots = store.get_all_robots()
        return jsonify({
            "timestamp": store.get_summary()["last_update"],
            "robots": robots,
        })

    @app.route("/api/robots", methods=["GET"])
    def api_robots():
        """Detailed information per robot."""
        return jsonify({"robots": store.get_all_robots()})

    @app.route("/api/intents", methods=["GET"])
    def api_intents():
        """Current declared robot intents."""
        return jsonify({"intents": store.get_intents()})

    @app.route("/api/reservations", methods=["GET"])
    def api_reservations():
        """Active and free resource / intersection reservations."""
        return jsonify({"reservations": store.get_reservations()})

    @app.route("/api/tasks", methods=["GET"])
    def api_tasks():
        """Current tracked warehouse tasks."""
        return jsonify({"tasks": store.get_tasks()})

    @app.route("/api/events", methods=["GET"])
    def api_events():
        """Chronological event feed with optional filtering."""
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
        """Inter-robot network health status."""
        return jsonify(store.get_network())

    @app.route("/api/metrics", methods=["GET"])
    def api_metrics():
        """Current experiment evaluation metrics."""
        metrics = store.get_metrics()
        if metrics is None:
            return jsonify({
                "mode": "proposed",
                "total_task_time": 0.0,
                "average_wait_time": 0.0,
                "tasks_completed": 0,
                "collision_count": 0,
            })
        return jsonify(metrics)

    @app.route("/api/experiments", methods=["GET"])
    def api_experiments():
        """Historical experiment runs."""
        return jsonify({"experiments": store.get_experiment_runs()})

    # ── MOCK DEMO CONTROLLER (Read/Switch scenario for demo testing) ───────

    @app.route("/api/simulator/scenario", methods=["GET", "POST"])
    def api_simulator_scenario():
        """Query or switch mock scenario (only active in mock mode)."""
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
    parser.add_argument(
        "--mode",
        choices=["mock", "ros2"],
        default=config.MODE,
        help="Dashboard mode (mock or ros2)",
    )
    parser.add_argument(
        "--scenario",
        choices=AVAILABLE_SCENARIOS,
        default=config.DEFAULT_SCENARIO,
        help="Mock demo scenario to run",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=config.SIM_SPEED,
        help="Simulator playback speed multiplier",
    )
    parser.add_argument(
        "--host", default=config.HOST, help="Host IP to bind Flask app"
    )
    parser.add_argument(
        "--port", type=int, default=config.PORT, help="Port to bind Flask app"
    )

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
