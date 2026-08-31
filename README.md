# Synergy Prototype

> **Multi-Agent Autonomous Mobile Robot (AMR) Orchestration & Logistics Simulation Framework**

A high-fidelity, competition-ready multi-robot logistics simulation platform built on **Gazebo Sim** (SDF 1.9) with full **ROS 2** integration support. Designed for benchmarking decentralized multi-agent coordination, collision avoidance, fleet routing, and SLAM navigation in an industrial warehouse environment.

---

## 📁 Repository Architecture

```
synergy-prototype/
├── gazebo/                         # Gazebo Simulation Environment Sub-Package
│   ├── README.md                   # Detailed Gazebo module manual & topic catalog
│   ├── scripts/                    # Universal cross-platform simulation launchers
│   └── simulation/
│       ├── models/                 # Modular SDF 1.9 models (AMRs, Shelves, Stations)
│       └── worlds/
│           ├── warehouse.sdf       # Master 20m × 20m multi-robot warehouse world
│           └── amr_test.sdf        # Isolated single-robot testing environment
├── fleet_coordination/             # Fleet Coordination Algorithmic Subsystem
│   ├── config/                     # Tunable parameters
│   ├── models/                     # Pure dataclasses (shared vocabulary)
│   ├── algorithm/                  # Core algorithms (ZERO ROS imports)
│   ├── ros_interface/              # ROS 2 adapter layer
│   └── tests/                      # pytest unit tests
└── README.md                       # Master project overview
```

---

## ⚡ Quick Start (Gazebo Simulation)

Launch the complete multi-robot simulation environment with a single command on any operating system:

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
| **AMR Blue** | 🔵 Sapphire Blue | `(-3.5, 5.25)` | `/amr_blue/cmd_vel` | `/amr_blue/odom` | `/amr_blue/scan` |
| **AMR Green** | 🟢 Emerald Green | `(0.5, 8.5)` | `/amr_green/cmd_vel` | `/amr_green/odom` | `/amr_green/scan` |
| **AMR Orange**| 🟠 Safety Orange | `(3.5, -6.5)` | `/amr_orange/cmd_vel` | `/amr_orange/odom` | `/amr_orange/scan` |

### Sample Velocity CLI Command
```bash
# Drive AMR Blue forward at 0.5 m/s
gz topic -t "/amr_blue/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.0}"
```

---

## 🧠 Fleet Coordination Algorithm

This repository also includes the **algorithmic subsystem** for decentralized multi-robot coordination in a smart warehouse prototype (`fleet_coordination/`).

### Key Principle

> **There is no central fleet decision-maker.**
>
> Every robot runs the same coordination logic, maintains its own local
> World Model, and makes independent decisions. Coordination emerges
> from peer-to-peer communication and deterministic algorithms.

### Data Models

| Model | Purpose |
|---|---|
| `Pose2D` | 2D position + orientation (abstract frame) |
| `RobotState` | What a robot IS (broadcast to peers) |
| `RobotIntent` | What a robot PLANS TO DO (broadcast for conflict detection) |
| `Reservation` | Temporary claim on a shared resource |
| `Task` | Unit of work to be assigned |
| `ConflictReport` | Output of conflict detection |
| `PriorityDecision` | Output of PriorityEngine arbitration |
| `ReservationDecision` | Output of ReservationManager lifecycle operations |
| `TaskBid` | Individual robot bid score and eligibility factors |
| `AssignmentDecision` | Output of TaskAllocator evaluation |

### Algorithms

The algorithm layer is pure Python and isolated from ROS 2 to ensure it is fully unit-testable. Key subsystems include:
- **WorldModel:** Local, private state store for a single robot's Fleet Coordination Agent.
- **ConflictDetector:** Pure algorithmic engine identifying spatial and temporal contention over shared warehouse resources.
- **PriorityEngine:** Deterministic arbitration engine resolving pairwise coordination conflicts.
- **ReservationManager:** Stateless algorithmic service for resource reservation lifecycle.
- **TaskAllocator:** Distributed task bidding and allocation.

For full algorithmic documentation, see `fleet_coordination/PROJECT.md`.

---

## 📚 Detailed Documentation

- **Gazebo Simulation:** [`gazebo/README.md`](./gazebo/README.md)
- **Fleet Coordination Subsystem:** [`fleet_coordination/PROJECT.md`](./fleet_coordination/PROJECT.md)
