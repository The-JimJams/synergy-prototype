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
└── README.md                       # Master project overview
```

---

## ⚡ Quick Start

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

## 📚 Detailed Documentation

For full installation guides (macOS, Ubuntu, Windows), coordinate maps, Gazebo-to-ROS 2 bridge instructions, and troubleshooting tips, refer to the module guide:

👉 **[Gazebo Simulation Module Documentation (`gazebo/README.md`)](./gazebo/README.md)**
