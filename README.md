# SYNERGY — Multi-Agent AMR Orchestration & Decentralized Fleet Coordination

> **Multi-Agent Autonomous Mobile Robot (AMR) Orchestration, Logistics Simulation & Decentralized Fleet Coordination Framework**

A high-fidelity multi-robot logistics simulation platform built on **Gazebo Sim** (SDF 1.9) and **ROS 2**, paired with a **pure Python decentralized fleet coordination algorithm suite**. Designed for benchmarking decentralized multi-agent coordination, collision avoidance, fleet routing, and SLAM navigation in an industrial warehouse environment.

---

## 📁 Repository Architecture

```
synergy-prototype/
├── gazebo/                         # Gazebo Simulation Environment Sub-Package
│   ├── README.md                   # Detailed Gazebo module manual & topic catalog
│   ├── scripts/                    # Universal cross-platform simulation launchers
│   │   ├── launch_sim.py           # Universal Python launcher (macOS, Linux, Windows)
│   │   ├── launch_sim.sh           # POSIX Bash launcher (macOS / Linux)
│   │   ├── launch_sim.bat          # Windows Command Prompt batch script
│   │   └── launch_sim.ps1          # Windows PowerShell script
│   └── simulation/
│       ├── models/                 # Modular SDF 1.9 models (AMRs, Shelves, Stations)
│       │   ├── amr/                # Base AMR template
│       │   ├── amr_blue/           # AMR Blue instance (/amr_blue)
│       │   ├── amr_green/          # AMR Green instance (/amr_green)
│       │   ├── amr_orange/         # AMR Orange instance (/amr_orange)
│       │   ├── shelf/              # 3-tier industrial shelving rack with cargo
│       │   ├── pickup_station/     # Cargo intake staging zone
│       │   ├── drop_station/       # Order discharge and packing zone
│       │   ├── charging_station/   # Wireless induction docking station
│       │   ├── pallet_stack/       # Stacked wooden logistics pallets
│       │   └── dumpster/           # Industrial waste container
│       └── worlds/
│           ├── warehouse.sdf       # Master 20m × 20m multi-robot warehouse world
│           └── amr_test.sdf        # Isolated single-robot testing environment
├── fleet_coordination/             # Decentralized Coordination Algorithm Sub-Package
│   ├── config/                     # Tunable parameters, weights, timeouts
│   ├── models/                     # 17 pure Python typed domain dataclasses
│   ├── algorithm/                  # Core algorithms (WorldModel, Conflict, Priority, Reservations, Auctions)
│   ├── ros_interface/              # ROS 2 adapter layer (rclpy node, serialization)
│   ├── tests/                      # 13 test suites (323 automated unit & integration tests)
│   ├── PROJECT.md                  # Comprehensive algorithmic technical documentation
│   └── ALGORITHM_HANDOFF.md        # ROS 2 integration contracts & developer handoff guide
└── README.md                       # Master project overview
```

---

## ⚡ Quick Start

### 1. Launch Multi-Robot Gazebo Simulation

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
| **AMR Blue** | 🔵 Sapphire Blue | `(-3.5, 5.25)` | `/amr_blue/cmd_vel` | `/amr_blue/odom` | `/amr_blue/scan` |
| **AMR Green** | 🟢 Emerald Green | `(0.5, 8.5)` | `/amr_green/cmd_vel` | `/amr_green/odom` | `/amr_green/scan` |
| **AMR Orange**| 🟠 Safety Orange | `(3.5, -6.5)` | `/amr_orange/cmd_vel` | `/amr_orange/odom` | `/amr_orange/scan` |

### Sample Velocity CLI Command
```bash
# Drive AMR Blue forward at 0.5 m/s
gz topic -t "/amr_blue/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.0}"
```

---

## 🧠 Decentralized Fleet Coordination Architecture

> **Key Principle: There is no central fleet decision-maker.**
>
> Every AMR runs an identical instance of the coordination logic, maintains its own local `WorldModel`, and makes independent decisions. Coordination emerges from peer-to-peer telemetry exchange and deterministic arbitration rules.

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
- `serialization.py` handles deterministic JSON $\leftrightarrow$ Dataclass encoding/decoding.

### Nav2 & Gazebo Boundaries
- **Nav2** manages continuous trajectory generation, local collision avoidance, and motor control.
- **Fleet Coordination** arbitrates discrete resource access, task assignment, and yield decisions.
- **Gazebo** simulates physics, sensors (LiDAR/Odometry), and robot hardware.

---

## 📚 Technical Documentation & Module Guides

- 👉 **[Gazebo Simulation Module Documentation (`gazebo/README.md`)](./gazebo/README.md)**: Full installation guides, SDF world topologies, Gazebo-to-ROS 2 bridges, and sensor catalogs.
- 👉 **[Algorithmic Technical Documentation (`fleet_coordination/PROJECT.md`)](./fleet_coordination/PROJECT.md)**: Mathematical formulations, invariants, and detailed state machines.
- 👉 **[Developer Handoff Guide (`fleet_coordination/ALGORITHM_HANDOFF.md`)](./fleet_coordination/ALGORITHM_HANDOFF.md)**: ROS 2 integration contracts, topic schemas, and developer workflows.
