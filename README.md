# SYNERGY — Decentralized Multi-AMR Warehouse Fleet Coordination & Operations Platform

> **Decentralized Autonomous Mobile Robot (AMR) Orchestration, Logistics Simulation & Live Operations Dashboard**
>
> SYNERGY is a competition-ready industrial multi-robot logistics coordination platform featuring pure‑Python decentralized coordination algorithms, high-fidelity Gazebo Sim (SDF 1.9), ROS 2 integration, and a dedicated operations dashboard.

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
├── fleet_coordination/             # Decentralized Coordination Algorithm Sub-Package
│   ├── config/                     # Tunable parameters, weights, timeouts
│   ├── models/                     # Pure dataclasses (shared vocabulary)
│   ├── algorithm/                  # Core algorithms (WorldModel, Conflict, Priority, Reservations, Auctions) — zero ROS imports
│   ├── ros_interface/              # ROS 2 adapter layer (rclpy node, serialization)
│   ├── tests/                      # 13 test suites (323 automated unit & integration tests)
│   ├── PROJECT.md                  # Comprehensive algorithmic technical documentation
│   └── ALGORITHM_HANDOFF.md        # ROS 2 integration contracts & developer handoff guide

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

### 1. Launch Multi-Robot Gazebo Simulation

Launch the complete multi-robot simulation environment with a single command:

#### 🍎 macOS / 🐧 Linux
```bash
./gazebo/scripts/launch_sim.sh
```
*Or using Python:*
```bash
python3 gazebo/scripts/launch_sim.py
```

#### 🪟 Windows
```cmd
gazebo\scripts\launch_sim.bat
```
*Or via PowerShell:*
```powershell
.\gazebo\scripts\launch_sim.ps1
```

### 2. Run Algorithmic Unit Test Suite
```bash
# Run complete test suite (323 tests in < 1.0s)
pytest -q
```

---

## 🤖 Active AMR Fleet (Gazebo Simulation)

The simulation includes **3 color-coded AMRs** operating under isolated namespaces with differential drive kinematics, 2D planar LiDAR, 6-axis IMU, and 4-point dynamic caster stability:

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

### Running Unit Tests

```bash
# Run fleet coordination tests (323 tests in <1.0s)
python -m pytest fleet_coordination/tests -q

# Run dashboard tests (79 tests)
python -m pytest dashboard/tests -q
```

### Domain Models (`fleet_coordination/models/`)


| Model | Purpose |
|---|---|
| `Pose2D` | 2D position $(x, y)$ and heading $(\theta)$ in global frame |
| `RobotState` | Physical and operational telemetry broadcast by an AMR |
| `RobotIntent` | Declared future resource usage, waypoints, and validity deadline |
| `Reservation` | Authoritative mutual-exclusion claim on a shared resource |
| `Task` | Unit of warehouse logistics work |
| `ConflictReport` | Detected spatial/temporal contention between competing robots |
| `PriorityDecision` | Deterministic winner and scoring breakdown from `PriorityEngine` |
| `ReservationDecision` | Lifecycle outcome from `ReservationManager` (accepted, rejected, reason) |
| `TaskBid` | Individual AMR task bid score and eligibility factors |
| `AssignmentDecision` | Winner and bidding breakdown from `TaskAllocator` |
| `PeerHealthAssessment` | Individual peer health classification (`HEALTHY`, `SUSPECT`, `FAILED`) |
| `FleetHealthReport` | Fleet-wide heartbeat health assessment |
| `Obstacle` | Static or dynamic spatial obstruction impacting corridor resources |
| `RerouteDecision` | Alternative path evaluation from `RerouteEvaluator` |
| `LinkMetrics` | Communication link latency, packet loss, and telemetry freshness |
| `NetworkStatusReport` | Local communication mode (`CONNECTED`, `DEGRADED`, `DISCONNECTED`, `RECOVERY`) |
| `ReconciliationReport` | Convergence statistics following network partition healing |
| `TaskMetrics` / `RobotMetrics` / `PerformanceMetrics` | Observational benchmark and telemetry structures |

---

## 🧪 Testing & Verification

All 13 algorithmic test suites run in **$< 1.0$ second** with zero external simulation or middleware dependencies:

```bash
# Run complete test suite (323 tests)
python -m pytest -q

# Run verbose tests on specific modules
python -m pytest fleet_coordination/tests/test_reservation_manager.py -v
python -m pytest fleet_coordination/tests/test_benchmark.py -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 323 items

fleet_coordination/tests/test_models.py .............................    (29 tests)
fleet_coordination/tests/test_world_model.py ........................... (35 tests)
fleet_coordination/tests/test_conflict_detector.py ..................... (38 tests)
fleet_coordination/tests/test_priority_engine.py ....................... (37 tests)
fleet_coordination/tests/test_reservation_manager.py ................... (45 tests)
fleet_coordination/tests/test_task_allocator.py ........................ (36 tests)
fleet_coordination/tests/test_serialization.py ......................... (20 tests)
fleet_coordination/tests/test_fleet_node.py .........                    (9 tests)
fleet_coordination/tests/test_failure_detector.py ...................   (19 tests)
fleet_coordination/tests/test_obstacle_policy.py .....................  (21 tests)
fleet_coordination/tests/test_network_manager.py ...................... (22 tests)
fleet_coordination/tests/test_metrics.py .......                        (7 tests)
fleet_coordination/tests/test_benchmark.py .....                        (5 tests)

============================= 323 passed in 0.80s =============================
```

---

## 🔗 Integration Boundaries

### ROS 2 Interface Boundary
- Located strictly in `fleet_coordination/ros_interface/`.
- `fleet_node.py` provides `FleetCoordinationCore` and `FleetCoordinationNode` (rclpy wrapper).
- `serialization.py` handles deterministic JSON ↔ Dataclass encoding/decoding.

### Nav2 & Gazebo Boundaries
- **Nav2** manages continuous trajectory generation, local collision avoidance, and motor control.
- **Fleet Coordination** arbitrates discrete resource access, task assignment, and yield decisions.
- **Gazebo** simulates physics, sensors (LiDAR/Odometry), and robot hardware.

---

## 📚 Technical Documentation & Module Guides

- 👉 **[Gazebo Simulation Module Documentation (`gazebo/README.md`)](./gazebo/README.md)**: Full installation guides, SDF world topologies, Gazebo-to-ROS 2 bridges, and sensor catalogs.
- 👉 **[Algorithmic Technical Documentation (`fleet_coordination/PROJECT.md`)](./fleet_coordination/PROJECT.md)**: Mathematical formulations, invariants, and detailed state machines.
- 👉 **[Developer Handoff Guide (`fleet_coordination/ALGORITHM_HANDOFF.md`)](./fleet_coordination/ALGORITHM_HANDOFF.md)**: ROS 2 integration contracts, topic schemas, and developer workflows.

* **Operations Dashboard Guide:** [`dashboard/README.md`](dashboard/README.md)
* **Fleet Coordination Subsystem:** [`fleet_coordination/PROJECT.md`](fleet_coordination/PROJECT.md)
* **Gazebo Simulation Manual:** [`gazebo/README.md`](gazebo/README.md)
