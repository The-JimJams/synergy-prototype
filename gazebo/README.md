# 🏭 Industrial Multi-AMR Warehouse Simulation (`gazebo/`)

> **High-Fidelity Autonomous Mobile Robot (AMR) Physics Simulation built on Gazebo Sim (SDF 1.9) with ROS 2 Bridge & Nav2 Navigation Support**

[![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic%20(SDF%201.9)-blueviolet.svg)](https://gazebosim.org/)
[![ROS 2](https://img.shields.io/badge/ROS_2-Humble%20%7C%20Iron%20%7C%20Jazzy%20%7C%20Lyrical-orange.svg)](https://docs.ros.org/)
[![Physics](https://img.shields.io/badge/Physics%20Engine-ODE%20(1000%20Hz)-brightgreen.svg)]()
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-blue.svg)]()

The `gazebo/` package provides a competition-ready, industrial 3D digital-twin environment designed for multi-agent path planning, decentralized conflict resolution, intersection arbitration, and automated material handling.

---

## 📑 Table of Contents

1. [Warehouse Environment & Layout](#-warehouse-environment--layout)
2. [Warehouse Zones & Coordinate Map](#-warehouse-zones--coordinate-map)
3. [Active AMR Fleet Specifications](#-active-amr-fleet-specifications)
4. [Gazebo & ROS 2 Topic Architecture](#-gazebo--ros-2-topic-architecture)
5. [Cross-Platform Launchers & Quick Start](#-cross-platform-launchers--quick-start)
6. [Platform Installation & Setup](#-platform-installation--setup)
   - [macOS (Apple Silicon & Intel)](#1-macos-apple-silicon--intel)
   - [Ubuntu / Debian Linux](#2-ubuntu--debian-linux)
   - [Windows (WSL2 & Native)](#3-windows-wsl2--native)
7. [ROS 2 Bridge & Nav2 Integration](#-ros-2-bridge--nav2-integration)
8. [Directory Structure & SDF Model Catalog](#-directory-structure--sdf-model-catalog)
9. [Troubleshooting & Platform FAQs](#-troubleshooting--platform-faqs)

---

## 🌟 Warehouse Environment & Layout

The master simulation world (`simulation/worlds/warehouse.sdf`) replicates an active industrial distribution and fulfillment center:
- **Dimensions:** $20.0\text{ m} \times 20.0\text{ m} \times 2.5\text{ m}$ enclosed concrete floor with perimeter skirting and structural I-beam pillars.
- **Physics Engine:** Open Dynamics Engine (ODE) configured for $1000\text{ Hz}$ update rate ($\Delta t = 0.001\text{ s}$).
- **3 Color-Coded AMRs:** Distinct namespaces (`amr_blue`, `amr_green`, `amr_orange`) with differential drive kinematics, planar LiDARs, 6-axis IMUs, and wheel odometry.
- **8 High-Bay Shelving Racks:** Numbered units ($S1$ through $S8$) with palletized cargo boxes.
- **Dedicated Staging Zones:** 2 Intake Pickup Stations ($P1$, $P2$), an Outbound Packing/Drop Station ($D1$), and an Automated Rapid Charging Bay ($CHG$).
- **Traffic Intersections:** 2 high-contention corridor intersections ($I1$, $I2$) equipped with visual hazard cross-hatching and safety bollards.
- **Dynamic Blockage Scenario:** An obstacle placed in the central aisle for detour and rerouting validation.

```
(-10, 10) ┌───────────────────────────[+Y]───────────────────────────┐ (10, 10)
          │                                                          │
          │   [ S1: NW1 ]   [ S2: NE1 ]    [ S3: NW2 ]   [ S4: NE2 ] │
          │   (-4.8, 7.5)   (4.8, 7.5)     (-4.8, 3.0)   (4.8, 3.0)  │
          │                                                          │
[-X]      │   ═══════════════════[ Intersection I1 ]═════════════════│      [+X]
          │                        (0.0, 5.2)                        │
          │                                                          │
          │   [ S5: SW2 ]   [ S6: SE2 ]    [ S7: SW1 ]   [ S8: SE1 ] │
          │   (-4.8, 1.5)   (4.8, 1.5)     (-4.8, -3.0)  (4.8, -3.0) │
          │                                                          │
          │   ═══════════════════[ Intersection I2 ]═════════════════│
          │                        (0.0, -0.7)                       │
          │                                                          │
          │   [ P2: Intake ]    [ D1: Drop ]    [ P1: Staging ]   [ CHG ⚡]
          │   (-5.5, -7.0)      (0.0, -8.1)      (0.0, 8.0)     (5.5, -7.5)
(-10, -10)└───────────────────────────[-Y]───────────────────────────┘ (10, -10)
```

---

## 🗺️ Warehouse Zones & Coordinate Map

The world origin `(0, 0, 0)` is located at the geometric center of the warehouse floor:

| Zone / Landmark | Identifier | Coordinate `(X, Y, Z)` | Visual Identifier | Functional Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Pickup Station 1** | `P1` | `(0.0, 8.0, 0.0)` | 🟢 Emerald Green **P** | Primary intake staging pad (North bay) |
| **Pickup Station 2** | `P2` | `(-5.5, -7.0, 0.0)`| 🟢 Emerald Green **P** | Auxiliary cargo intake receiving zone (SW bay) |
| **Drop Station 1** | `D1` | `(0.0, -8.1, 0.0)` | 🔵 Royal Blue **D** | Outbound packing, sorting & dispatch bay |
| **Charging Bay** | `CHG` | `(5.5, -7.5, 0.0)` | 🟡 Gold Battery + ⚡ | Autonomous inductive fast-charging dock |
| **Intersection 1** | `I1` | `(0.0, 5.2, 0.0)` | 🔴 Red Cross + Bollards | North cross-aisle traffic chokepoint |
| **Intersection 2** | `I2` | `(0.0, -0.7, 0.0)`| 🔴 Red Cross + Bollards | South cross-aisle traffic chokepoint |
| **Blocked Aisle Obstacle**| `OBS` | `(-0.2, 0.75, 0.0)`| 🟠 Orange Traffic Cone | Scenario obstacle for rerouting tests |
| **Shelf Rack S1** | `S1` | `(-4.8, 7.5, 0.0)` | ⬛ Top Marker **S1** | High-bay inventory storage unit 1 |
| **Shelf Rack S2** | `S2` | `(4.8, 7.5, 0.0)` | ⬛ Top Marker **S2** | High-bay inventory storage unit 2 |
| **Shelf Rack S3** | `S3` | `(-4.8, 3.0, 0.0)` | ⬛ Top Marker **S3** | High-bay inventory storage unit 3 |
| **Shelf Rack S4** | `S4` | `(4.8, 3.0, 0.0)` | ⬛ Top Marker **S4** | High-bay inventory storage unit 4 |
| **Shelf Rack S5** | `S5` | `(-4.8, 1.5, 0.0)` | ⬛ Top Marker **S5** | High-bay inventory storage unit 5 |
| **Shelf Rack S6** | `S6` | `(4.8, 1.5, 0.0)` | ⬛ Top Marker **S6** | High-bay inventory storage unit 6 |
| **Shelf Rack S7** | `S7` | `(-4.8, -3.0, 0.0)`| ⬛ Top Marker **S7** | High-bay inventory storage unit 7 |
| **Shelf Rack S8** | `S8` | `(4.8, -3.0, 0.0)` | ⬛ Top Marker **S8** | High-bay inventory storage unit 8 |

---

## 🤖 Active AMR Fleet Specifications

```
                     ┌────────────────────────────────┐
                     │    Warehouse World (SDF 1.9)   │
                     └───────────────┬────────────────┘
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
   [ AMR Blue (A) ]            [ AMR Green (B) ]           [ AMR Orange (C) ]
   /amr_blue/cmd_vel           /amr_green/cmd_vel          /amr_orange/cmd_vel
   /amr_blue/odom              /amr_green/odom             /amr_orange/odom
   /amr_blue/scan              /amr_green/scan             /amr_orange/scan
   /amr_blue/imu               /amr_green/imu              /amr_orange/imu
   /amr_blue_contact           /amr_green_contact          /amr_orange_contact
```

### Fleet Configuration Table

| Robot | Theme | Spawn Pose `(X, Y, Yaw)` | Velocity Topic (Pub) | Odometry Topic (Sub) | 2D LiDAR (Sub) | Contact (Sub) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AMR Blue (A)** | 🔵 Sapphire Blue | `(-3.5, 5.25, 0.0)` | `/amr_blue/cmd_vel` | `/amr_blue/odom` | `/amr_blue/scan` | `/amr_blue_contact` |
| **AMR Green (B)** | 🟢 Emerald Green | `(0.5, 8.5, -1.57)` | `/amr_green/cmd_vel` | `/amr_green/odom` | `/amr_green/scan` | `/amr_green_contact` |
| **AMR Orange (C)**| 🟠 Safety Orange | `(3.5, -6.5, 3.14)` | `/amr_orange/cmd_vel` | `/amr_orange/odom` | `/amr_orange/scan` | `/amr_orange_contact` |

### Kinematic & Sensor Properties
- **Drive Kinematics:** Differential drive with $0.10\text{ m}$ drive wheel radius and $0.40\text{ m}$ track width.
- **Chassis Dimensions:** $0.65\text{ m} \times 0.50\text{ m} \times 0.25\text{ m}$ with $100\text{ kg}$ payload rating.
- **Stability:** 4-point dynamic caster layout (front/rear, left/right) preventing acceleration pitch pitching.
- **2D Planar LiDAR:** $360^\circ$ scan FOV, $12.0\text{ m}$ range, $0.05\text{ m}$ min range, $10\text{ Hz}$ update rate, 720 samples.
- **IMU Sensor:** 6-axis linear acceleration and angular velocity tracking via `gz-sim-imu-system`.

---

## 📡 Gazebo & ROS 2 Topic Architecture

### Direct Gazebo Control (Command Line)
You can command and monitor AMRs directly via the `gz topic` CLI:

```bash
# 1. Drive AMR Blue forward at 0.5 m/s
gz topic -t "/amr_blue/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.0}"

# 2. Turn AMR Green in place at 0.8 rad/s
gz topic -t "/amr_green/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.0}, angular: {z: 0.8}"

# 3. Stop AMR Orange
gz topic -t "/amr_orange/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.0}, angular: {z: 0.0}"

# 4. Echo AMR Blue Odometry
gz topic -e -t "/amr_blue/odom"
```

---

## 🚀 Cross-Platform Launchers & Quick Start

Dedicated cross-platform launchers handle model resource paths, environment variables, and platform-specific routing automatically:

### 🌟 Universal Python Launcher (Recommended for all OS)
```bash
# Launch Server + 3D GUI
python3 gazebo/scripts/launch_sim.py

# Launch Headless Physics Server only (CI / High-Performance)
python3 gazebo/scripts/launch_sim.py --server

# Launch GUI Client only (connect to running simulation server)
python3 gazebo/scripts/launch_sim.py --gui
```

---

### 🐧 Linux & 🍎 macOS (POSIX Bash)
```bash
# Launch full simulation
./gazebo/scripts/launch_sim.sh

# Headless mode
./gazebo/scripts/launch_sim.sh --server

# GUI only
./gazebo/scripts/launch_sim.sh --gui
```

---

### 🪟 Windows (Command Prompt & PowerShell)

**Command Prompt (`cmd.exe`):**
```cmd
gazebo\scripts\launch_sim.bat
```

**PowerShell (`pwsh`):**
```powershell
.\gazebo\scripts\launch_sim.ps1
```

---

## 💻 Platform Installation & Setup

### 1. macOS (Apple Silicon & Intel)
Install Gazebo Harmonic via Homebrew:
```bash
# 1. Add Open Robotics Homebrew tap
brew tap osrf/simulation
brew install gz-harmonic

# 2. Configure macOS loopback multicast routing (required once per reboot)
sudo route change -net 224.0.0.0/4 127.0.0.1
# Note: If not present, run:
# sudo route add -net 224.0.0.0/4 127.0.0.1
```

---

### 2. Ubuntu / Debian Linux
Install Gazebo Harmonic from the official OSRF apt repository:
```bash
# 1. Add OSRF repository keys and sources
sudo apt-get update && sudo apt-get install -y curl lsb-release gnupg
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# 2. Install Gazebo Harmonic
sudo apt-get update
sudo apt-get install -y gz-harmonic python3
```

---

### 3. Windows (WSL2 & Native)

#### Option A: WSL2 Ubuntu (Recommended)
1. Install WSL2 Ubuntu: `wsl --install -d Ubuntu-22.04`
2. Follow the **Ubuntu / Debian Linux** steps above inside the WSL2 terminal.
3. WSLg automatically handles OpenGL GPU-accelerated rendering.

#### Option B: Native Windows
1. Download Gazebo Harmonic installer from [Gazebo Sim Windows Releases](https://gazebosim.org/docs/harmonic/install_windows).
2. Ensure `gz` is in your Windows System `PATH`.

---

## 🔗 ROS 2 Bridge & Nav2 Integration

When coupling Gazebo with the ROS 2 navigation stack (`src/synergy_nav2` and `src/robot_bringup`), standard bridge mappings translate Gazebo messages to ROS 2 types:

```
┌───────────────────────────┐                ┌───────────────────────────┐
│     Gazebo Sim World      │                │       ROS 2 / Nav2        │
├───────────────────────────┤                ├───────────────────────────┤
│ /amr_blue/cmd_vel         │ ◄────────────  │ /amr_blue/cmd_vel         │
│   (gz.msgs.Twist)         │   ros_gz_bridge│   (geometry_msgs/Twist)   │
│                           │                │                           │
│ /amr_blue/odom            │ ─────────────► │ /amr_blue/odom            │
│   (gz.msgs.OdometryWithCov)                │   (nav_msgs/Odometry)     │
│                           │                │                           │
│ /amr_blue/scan            │ ─────────────► │ /amr_blue/scan            │
│   (gz.msgs.LaserScan)     │                │   (sensor_msgs/LaserScan) │
└───────────────────────────┘                └───────────────────────────┘
```

### Launching with ROS 2 Bringup
```bash
# Build ROS 2 workspace
colcon build --symlink-install
source install/setup.bash

# Launch multi-AMR bringup with Gazebo bridge and Nav2
ros2 launch robot_bringup bringup.launch.py
```

---

## 📁 Directory Structure & SDF Model Catalog

```
gazebo/
├── README.md                       # Comprehensive simulation manual
├── scripts/                        # Universal launch automation scripts
│   ├── launch_sim.py               # Universal Python launcher (macOS, Linux, Windows)
│   ├── launch_sim.sh               # POSIX Bash launcher
│   ├── launch_sim.bat              # Windows Command Prompt batch file
│   └── launch_sim.ps1              # Windows PowerShell script
└── simulation/
    ├── models/                     # Modular simulation models (SDF 1.9)
    │   ├── amr/                    # Generic AMR base model with LiDAR & differential drive
    │   ├── amr_blue/               # AMR Blue instance (Sapphire Blue theme)
    │   ├── amr_green/              # AMR Green instance (Emerald Green theme)
    │   ├── amr_orange/             # AMR Orange instance (Safety Orange theme)
    │   ├── shelf/                  # 3-tier industrial warehouse rack with pallet cargo
    │   ├── pickup_station/         # Floor intake staging zone with 45° hazard lines
    │   ├── drop_station/           # Floor discharge zone with 45° hazard lines
    │   ├── charging_station/       # Induction charging dock with status LED indicator
    │   ├── pallet_stack/           # Stack of wooden logistics pallets
    │   ├── dumpster/               # Industrial recycling disposal container
    │   └── obstacle/               # Safety traffic cone obstacle
    └── worlds/
        ├── warehouse.sdf           # Master 20m × 20m multi-robot warehouse world
        └── amr_test.sdf            # Isolated single-robot testing environment
```

---

## 🔧 Troubleshooting & Platform FAQs

### 1. `gz sim: command not found`
- **Linux:** Ensure Gazebo Harmonic is installed: `sudo apt install gz-harmonic`
- **macOS:** Ensure Homebrew path is in your environment: `eval $(/opt/homebrew/bin/brew shellenv)`
- **Windows:** Add Gazebo `bin` path to your Windows User/System `Path`.

### 2. macOS: GUI opens but shows a black window or fails to connect
On macOS, loopback multicast networking must be enabled:
```bash
sudo route change -net 224.0.0.0/4 127.0.0.1
# If not present, run:
sudo route add -net 224.0.0.0/4 127.0.0.1
```
Then launch using: `python3 gazebo/scripts/launch_sim.py`.

### 3. Model meshes or textures not found
The launcher scripts automatically set `GZ_SIM_RESOURCE_PATH`. If running `gz sim` directly from the terminal, export the path manually:
```bash
export GZ_SIM_RESOURCE_PATH="$(pwd)/gazebo/simulation/models:$GZ_SIM_RESOURCE_PATH"
```

### 4. Adjusting Real-Time Factor (RTF)
If simulation runs slow on constrained hardware, adjust `<real_time_update_rate>` in `simulation/worlds/warehouse.sdf` from `1000` to `500` or launch in headless server mode (`--server`).
