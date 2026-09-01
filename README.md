# SYNERGY — Decentralized Multi-AMR Warehouse Fleet Coordination & Operations Platform

> **Decentralized Autonomous Mobile Robot (AMR) Orchestration, Logistics Simulation & Live Operations Dashboard**

SYNERGY is a competition-ready, industrial multi-robot logistics coordination platform featuring pure-Python decentralized coordination algorithms, high-fidelity Gazebo Sim physics simulation, ROS 2 integration, and a dedicated industrial operations dashboard.

---

## 📁 Repository Architecture

```
synergy-prototype/
├── dashboard/                      # Live Industrial AMR Fleet Operations Dashboard
│   ├── app.py                      # Flask REST API backend & static server
│   ├── config.py                   # 20m × 20m warehouse coordinates & configuration
│   ├── data_store.py               # In-memory thread-safe telemetry store
│   ├── simulator/                  # Standalone mock telemetry engine (6 scenarios)
│   ├── static/                     # Light industrial theme CSS & 60fps Canvas 2D engine
│   ├── templates/                  # Operations command center HTML template
│   └── tests/                      # 79 pytest unit & integration tests
├── fleet_coordination/             # Fleet Coordination Algorithmic Subsystem
│   ├── config/                     # Tunable parameters (no magic numbers)
│   ├── models/                     # Pure dataclasses (shared domain vocabulary)
│   ├── algorithm/                  # Core algorithms (ZERO ROS / Gazebo imports)
│   ├── ros_interface/              # ROS 2 adapter layer (rclpy node, serialization)
│   └── tests/                      # 13 test suites (323 pytest unit & integration tests)
├── gazebo/                         # Gazebo Simulation Environment Sub-Package
│   ├── scripts/                    # Universal cross-platform simulation launchers
│   └── simulation/
│       ├── models/                 # Modular SDF models (AMRs, Shelves, Stations)
│       └── worlds/
│           ├── warehouse.sdf       # Master 20m × 20m multi-robot warehouse world
│           └── amr_test.sdf        # Isolated single-robot testing environment
├── p5_task_failure/                # Task failure & recovery test scenarios
├── Dockerfile                      # Containerized environment build
└── README.md                       # Master project documentation
```

---

## 🖥️ Live AMR Operations Dashboard (`dashboard/`)

A light-theme industrial control dashboard for real-time fleet telemetry, 2D floor plan visualization, intersection claim monitoring, and benchmark evaluation.

### Running the Dashboard

```bash
# Standalone Mock Mode (runs anywhere without ROS 2 or Gazebo)
python dashboard/run_dashboard.py --mode mock --scenario full_demo --port 5055

# Or via ROS 2 mode (subscribes to live ROS 2 / Nav2 telemetry topics)
python dashboard/run_dashboard.py --mode ros2 --port 5055
```

Open your browser at: `http://localhost:5055`

### Key Dashboard Features

* **Architectural 20×20m Warehouse Map:** 1:1 scale matching Gazebo `warehouse.sdf` with 8 vertical shelving racks ($S1$–$S8$), Pickup ($P$), Dropoff ($D$), Charging Bay with rapid recharge ($CHG$ ⚡), and chokepoint intersections ($I1$, $I2$).
* **60 FPS Smooth AMR Movement:** Interpolation engine with linear position lerp and shortest-arc orientation delta handling across $\pm\pi$.
* **Inspector & Fleet Cards:** Interactive AMR selection, operating pose, speed, battery gauge, and assigned task.
* **Operations Deck:** Warehouse task queue, intersection reservations, mesh network diagnostics, filtered event feed, and empirical benchmark evaluation.
* **Testing:** 79 automated pytest tests (`python -m pytest dashboard/tests -v`).

---

## ⚡ Quick Start (Gazebo Simulation)

Launch the complete multi-robot simulation environment with a single command:

### 🍎 macOS / 🐧 Linux
```bash
./gazebo/scripts/launch_sim.sh
```
*Or using Python:*
```bash
python3 gazebo/scripts/launch_sim.py
```

### 🪟 Windows
```cmd
gazebo\scripts\launch_sim.bat
```
*Or via PowerShell:*
```powershell
.\gazebo\scripts\launch_sim.ps1
```

---

## 🤖 Active AMR Fleet

The environment includes **3 color-coded AMRs** operating under isolated namespaces with differential drive kinematics, 2D planar LiDAR, 6-axis IMU, and 4-point dynamic caster stability:

| Robot | Color Theme | Initial Spawn `(X, Y)` | Velocity Topic (Pub) | Odometry Topic (Sub) | 2D LiDAR Topic (Sub) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AMR Blue (A)** | 🔵 Sapphire Blue | `(-7.5, 0.8)` | `/amr_blue/cmd_vel` | `/amr_blue/odom` | `/amr_blue/scan` |
| **AMR Green (B)** | 🟢 Emerald Green | `(-4.3, -3.2)` | `/amr_green/cmd_vel` | `/amr_green/odom` | `/amr_green/scan` |
| **AMR Orange (C)**| 🟠 Safety Orange | `(5.0, 3.5)` | `/amr_orange/cmd_vel` | `/amr_orange/odom` | `/amr_orange/scan` |

---

## 🧠 Fleet Coordination Algorithm (`fleet_coordination/`)

Pure Python decentralized fleet coordination algorithms with zero external simulation dependencies.

### Key Principle

> **There is no central fleet decision-maker.**
>
> Every robot runs an identical instance of the coordination logic, maintains its own local `WorldModel`, and makes independent decisions. Coordination emerges from peer-to-peer telemetry exchange and deterministic arbitration rules.

### Subsystem Components

```
Fleet Coordination Agent (one per robot)
    │
    ├── WorldModel            — Local private state store (working memory)
    ├── ConflictDetector      — Spatial & temporal conflict detection over shared resources
    ├── PriorityEngine        — Deterministic multi-factor priority arbitration
    ├── ReservationManager    — Mutual-exclusion resource claiming & lifecycle management
    ├── TaskAllocator         — Decentralized auction & eligibility bidding
    ├── FailureDetector       — Heartbeat-based peer health monitoring & task reclaim
    ├── ObstaclePolicy        — Dynamic obstacle detection & corridor blockage classification
    ├── RerouteEvaluator      — Deterministic alternative route evaluation
    ├── NetworkManager        — Communication quality tracking (CONNECTED/DEGRADED/DISCONNECTED/RECOVERY)
    ├── ReconciliationManager — Post-partition state convergence & deterministic conflict resolution
    ├── MetricsLogger         — Observational event historian & counter tracker
    └── BenchmarkEvaluator    — Deterministic comparison against STOP-AND-WAIT baseline
```

### Running Unit Tests

```bash
# Run fleet coordination tests (323 tests in <1.0s)
python -m pytest fleet_coordination/tests -q

# Run dashboard tests (79 tests)
python -m pytest dashboard/tests -q
```

---

## 📚 Detailed Documentation

* **Operations Dashboard Guide:** [`dashboard/README.md`](dashboard/README.md)
* **Fleet Coordination Subsystem:** [`fleet_coordination/PROJECT.md`](fleet_coordination/PROJECT.md)
* **Gazebo Simulation Manual:** [`gazebo/README.md`](gazebo/README.md)
