# SYNERGY Dashboard — Monitoring & Evaluation Module

[![Tests](https://img.shields.io/badge/tests-79%20passed-brightgreen.svg)]()
[![Mode](https://img.shields.io/badge/mode-Standalone%20Mock%20%7C%20ROS%202-blue.svg)]()
[![Read--Only](https://img.shields.io/badge/architecture-Read--Only%20Observer-orange.svg)]()

A **read-only** monitoring dashboard and performance evaluation module for the SYNERGY decentralized Autonomous Mobile Robot (AMR) warehouse prototype.

Visualizes fleet telemetry, intersection reservations, coordination events, network status, and experiment benchmark evaluations — without ever controlling the robots.

---

## Key Architecture & Independence Strategy

```
                          SYNERGY Fleet System
                        (Gazebo / ROS 2 / Mock)
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │       TELEMETRY ADAPTER       │
                   │ (mock_adapter / ros2_adapter) │
                   └───────────────────────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │    NORMALIZED DATA MODELS     │
                   │ (RobotState, Reservation,...) │
                   └───────────────────────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │      CENTRAL DATA STORE       │
                   │   (Thread-Safe In-Memory)     │
                   └───────────────────────────────┘
                                 /   \
                                v     v
                          Flask API   Metrics Engine / CSV Log
                                │
                                v
                     HTML5 / CSS3 / Vanilla JS
                     HTML Canvas Map Renderer
```

### Critical Architectural Rule
> **The dashboard is MONITORING-ONLY.**
> It must NEVER become the central decision-maker or controller for the robots.
> The decentralized Fleet Coordination Agents remain responsible for state exchange, conflict detection, priority calculation, intersection reservation, waiting/proceeding decisions, task allocation, failure handling, and rerouting.
> If the dashboard process is stopped, the fleet coordination architecture remains completely independent of it.

---

## Features

1. **Standalone Demo Mode (Mode A)**:
   - Self-contained mock telemetry simulator (`FleetSimulator`).
   - 6 built-in scenarios: `full_demo`, `normal`, `conflict`, `reroute`, `failure`, `network`.
   - Runs independently without Gazebo or ROS 2 dependencies.
2. **ROS 2 Integration Mode (Mode B)**:
   - Clean telemetry adapter boundary (`ROS2Adapter`).
   - Centralized ROS topic configuration (`config.py`).
   - Isolated conversion helpers (`robot_state_from_ros`, `reservation_from_ros`, etc.).
   - Importing backend code will **never crash** if `rclpy` or ROS 2 is absent.
3. **HTML5 Canvas 2D Warehouse Map**:
   - World-to-screen coordinate transformation (metres → pixels).
   - Storage rack schematics and aisle layout.
   - Named stations (`S1`..`S4`) and intersection zones (`I1`, `I2`).
   - Robot position markers, orientation heading arrows, trajectory trails, and obstacle warning triangles.
4. **Coordination Event Feed**:
   - Real-time log of events (`CONFLICT`, `WINNER`, `RESERVATION`, `WAIT`, `RELEASE`, `REROUTE`, `OBSTACLE`, `FAILURE`, `REASSIGNMENT`, `TASK_COMPLETED`, `HEARTBEAT_TIMEOUT`, `NETWORK_DEGRADED`, `NETWORK_RECOVERED`).
   - Dual filtering by **Event Type** and **Robot ID**.
5. **Benchmark Evaluation Engine**:
   - Calculates percentage improvement:
     $$\text{improvement\_percent} = \frac{\text{baseline\_time} - \text{proposed\_time}}{\text{baseline\_time}} \times 100$$
   - Displays measured improvement alongside target goal ($\ge 20.0\%$).
   - Logs experiment runs to [`data/experiments/experiment_results.csv`](file:///c:/Users/avani/Desktop/SYNERGY/antig/dashboard/data/experiments/) without overwriting.
   - Exports event sequences to [`data/events/`](file:///c:/Users/avani/Desktop/SYNERGY/antig/dashboard/data/events/) in JSON and JSONL format.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask, standard library |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Map Rendering** | HTML5 Canvas 2D Context |
| **Data Format** | JSON (REST API), CSV (Experiment metrics), JSONL (Event audits) |
| **Testing** | pytest |

---

## Quick Start (Standalone / Mock Mode)

### 1. Installation
```bash
cd dashboard
pip install -r requirements.txt
```

### 2. Run Dashboard
```bash
python run_dashboard.py --mode mock --scenario full_demo
```

Open your browser at: **http://localhost:5000**

### 3. Command Line Options
```bash
python run_dashboard.py --help

Options:
  --mode {mock,ros2}     Dashboard execution mode (default: mock)
  --scenario {full_demo,normal,conflict,reroute,failure,network}
                         Mock demo scenario (default: full_demo)
  --speed SPEED          Simulator playback speed multiplier (default: 1.0)
  --host HOST            Host IP binding (default: 0.0.0.0)
  --port PORT            Port binding (default: 5000)
```

---

## API Data Contract (Read-Only Endpoints)

- `GET /` -> Dashboard Single Page Application
- `GET /api/health` -> System status, active mode, and simulator state
- `GET /api/state` -> Current normalized state of all robots
- `GET /api/robots` -> Detailed robot state cards
- `GET /api/intents` -> Current declared robot intents
- `GET /api/reservations` -> Active/free intersection reservations
- `GET /api/tasks` -> Tracked warehouse tasks
- `GET /api/events?event_type=CONFLICT&robot_id=A` -> Event log feed with filtering
- `GET /api/network` -> Inter-robot communication health
- `GET /api/metrics` -> Current run evaluation metrics
- `GET /api/experiments` -> Historical experiment runs
- `GET /api/experiments/aggregate` -> Cross-run aggregate averages & improvement
- `POST /api/experiments/log` -> Log current run to CSV & JSON
- `GET/POST /api/simulator/scenario` -> Query or switch active mock scenario

*Note: All POST command attempts to control robots (`/stop_robot`, `/assign_task`) return HTTP 404.*

---

## Testing

Run all unit tests across models, data store, simulator, Flask API, metrics, event logger, and adapters:

```bash
python -m pytest tests/ -v
```

---

## Connecting Real ROS 2 Telemetry (Mode B Setup)

When ROS 2 integration is ready:
1. Ensure your ROS 2 workspace is sourced (`source /opt/ros/humble/setup.bash`).
2. Update topic names in `config.py`:
   ```python
   ROS2_TOPICS = {
       "robot_state":  "/synergy/{robot_id}/state",
       "robot_intent": "/synergy/{robot_id}/intent",
       "reservation":  "/synergy/reservations",
       "event":        "/synergy/events",
       "task":         "/synergy/tasks",
       "network":      "/synergy/network_status",
   }
   ```
3. Run dashboard in ROS 2 mode:
   ```bash
   python run_dashboard.py --mode ros2
   ```

---

## Project Structure

```
dashboard/
├── app.py                      # Flask REST API server
├── config.py                   # Central configuration & topic names
├── data_store.py               # Thread-safe in-memory data store
├── models.py                   # Normalized Python dataclasses
├── metrics.py                  # Evaluation engine & CSV logger
├── event_logger.py             # Event audit exporter (JSON/JSONL)
├── run_dashboard.py            # Standalone launcher script
├── requirements.txt            # Dependencies
├── README.md                   # Complete documentation
├── adapters/
│   ├── __init__.py
│   ├── mock_adapter.py         # Standalone mock mode wrapper
│   └── ros2_adapter.py         # ROS 2 subscriber & conversion adapter
├── simulator/
│   ├── __init__.py
│   ├── fleet_simulator.py      # Background scenario thread runner
│   └── scenarios.py            # 6 deterministic demo scenarios
├── templates/
│   └── index.html              # Dashboard SPA HTML template
├── static/
│   ├── css/style.css           # Modern dark theme styles
│   └── js/
│       ├── dashboard.js        # Main polling controller
│       ├── map.js              # HTML5 Canvas 2D map renderer
│       └── metrics.js          # Evaluation & benchmark comparison UI
├── data/
│   ├── events/                 # Exported JSON/JSONL event logs
│   └── experiments/            # CSV experiment results
└── tests/
    ├── test_models.py
    ├── test_data_store.py
    ├── test_simulator.py
    ├── test_api.py
    ├── test_metrics.py
    └── test_adapters.py
```
