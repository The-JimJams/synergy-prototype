# 🏭 Industrial Multi-AMR Warehouse Simulation

A competition-ready, high-fidelity **Autonomous Mobile Robot (AMR)** logistics simulation built on **Gazebo Sim** (SDF 1.9) with full **ROS 2** integration support.

Designed for testing fleet management, multi-agent path planning, collision avoidance, and warehouse material handling across diverse operating systems (**macOS, Linux, Windows**).

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Required Software & Prerequisites](#-required-software--prerequisites)
3. [Installation & Setup by OS](#-installation--setup-by-os)
   - [macOS (Apple Silicon & Intel)](#1-macos-apple-silicon--intel)
   - [Ubuntu / Debian Linux](#2-ubuntu--debian-linux)
   - [Windows (WSL2 & Native)](#3-windows-wsl2--native)
4. [Quick Start & Running the Simulation](#-quick-start--running-the-simulation)
5. [Warehouse Zone & Coordinate Map](#-warehouse-zone--coordinate-map)
6. [Active AMR Fleet & ROS 2 / Gazebo Topic Interface](#-active-amr-fleet--ros-2--gazebo-topic-interface)
7. [Directory Structure & Model Catalog](#-directory-structure--model-catalog)
8. [Troubleshooting & Platform FAQs](#-troubleshooting--platform-faqs)

---

## 🌟 Project Overview

This simulation replicates a real-world automated logistics fulfillment center featuring:
- **3 Color-Coded AMRs** with distinct namespaces (`amr_blue`, `amr_green`, `amr_orange`), 2D planar LiDARs, differential-drive controllers, and wheel odometry.
- **Dedicated Staging Zones**: 2 Intake Pickup Stations (**P1**, **P2**), an Order Packing/Drop Station (**D1**), an Automated Wireless Charging Bay, and 2 critical traffic intersections (**I1**, **I2**).
- **Industrial Storage Racks**: 8 High-Bay Shelving Units (**S1** through **S8**) with stacked pallet cargo boxes and high-contrast identification numbers.
- **Safety Navigation Markings**: 5m × 5m concrete floor grid, wall skirting, I-beam perimeter structural pillars, and wall-mounted industrial LED lighting.

```mermaid
graph TD
    subgraph Warehouse Environment
        NW1[Shelf S1 - NW1] --- I1[Intersection I1 Zone]
        NE1[Shelf S2 - NE1] --- I1
        NW2[Shelf S3 - NW2] --- I1
        NE2[Shelf S4 - NE2] --- I1
        SW2[Shelf S5 - SW2] --- I2[Intersection I2 Zone]
        SE2[Shelf S6 - SE2] --- I2
        SW1[Shelf S7 - SW1] --- I2
        SE1[Shelf S8 - SE1] --- I2
        I1 --- P1[Pickup Station P1]
        I2 --- P2[Pickup Station P2]
        I2 --- D1[Drop Station D1]
        I2 --- CH[Charging Bay]
    end
    subgraph Autonomous Fleet
        AMR_Blue[AMR Blue] --> I1
        AMR_Green[AMR Green] --> I1
        AMR_Orange[AMR Orange] --> I2
    end
```

---

## 📦 Required Software & Prerequisites

| Software | Recommended Version | Purpose |
| :--- | :--- | :--- |
| **Gazebo Sim** | **Harmonic** (or Garden / Fortress) | Physics engine, sensor simulation & 3D rendering |
| **Python** | **3.8+** | Universal cross-platform launcher & automation scripts |
| **ROS 2** *(Optional)* | **Humble** / **Iron** / **Jazzy** | Robot navigation, path planning, and SLAM nodes |
| **ros_gz_bridge** *(Optional)* | Compatible with ROS 2 distro | Bridges Gazebo topics to ROS 2 standard messages |

---

## 💻 Installation & Setup by OS

### 1. macOS (Apple Silicon & Intel)
Install Gazebo Sim using Homebrew:
```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Add Open Robotics tap and install Gazebo Harmonic
brew tap osrf/simulation
brew install gz-harmonic

# 3. macOS Networking Route (Required once per session for local IPC communication)
sudo route change -net 224.0.0.0/4 127.0.0.1
# Note: If it says "not in table", run:
# sudo route add -net 224.0.0.0/4 127.0.0.1
```

### 2. Ubuntu / Debian Linux
Install Gazebo Harmonic via the official OSRF package repository:
```bash
# 1. Install prerequisites
sudo apt-get update && sudo apt-get install -y curl lsb-release gnupg

# 2. Add OSRF repository key & source
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

# 3. Install Gazebo Harmonic
sudo apt-get update
sudo apt-get install -y gz-harmonic python3
```

### 3. Windows (WSL2 & Native)
#### Option A: WSL2 Ubuntu (Recommended)
1. Open PowerShell and install Ubuntu WSL2: `wsl --install -d Ubuntu-22.04`
2. Follow the **Ubuntu / Debian Linux** steps above inside the WSL2 terminal.
3. Use WSLg for hardware-accelerated GUI rendering.

#### Option B: Native Windows
1. Download Gazebo Sim binary installer from [Gazebo Sim Windows Releases](https://gazebosim.org/docs/harmonic/install_windows).
2. Ensure `gz` is added to your System `PATH` environment variable.
3. Install [Python 3](https://www.python.org/downloads/).

---

## 🚀 Quick Start & Running the Simulation

We provide dedicated cross-platform launchers so you never have to manually configure paths or environment variables:

### 🌟 Universal Python Launcher (Works on macOS, Linux, Windows)
```bash
# Launch Server + GUI automatically
python3 scripts/launch_sim.py

# Headless / Physics Server only
python3 scripts/launch_sim.py --server

# GUI Client only (connect to active server)
python3 scripts/launch_sim.py --gui
```

---

### 🐧 Linux & 🍎 macOS (POSIX Shell)
```bash
# Full Simulation (Server + GUI)
./scripts/launch_sim.sh

# Headless mode
./scripts/launch_sim.sh --server

# GUI Client only
./scripts/launch_sim.sh --gui
```

---

### 🪟 Windows (Command Prompt & PowerShell)

**Command Prompt (`cmd.exe`):**
```cmd
scripts\launch_sim.bat
```

**PowerShell:**
```powershell
.\scripts\launch_sim.ps1
```

---

## 🗺️ Warehouse Zone & Coordinate Map

The warehouse is enclosed in a **20.0m × 20.0m × 2.5m** perimeter. Origin `(0, 0, 0)` is at the geometric center of the concrete floor.

| Zone / Asset | Coordinates `(X, Y, Z)` | Visual Marker | Functional Purpose |
| :--- | :--- | :--- | :--- |
| **Pickup Station P1** | `(0.0, 8.0, 0.0)` | 🟢 Emerald Green **P** | Primary intake staging pad (North bay) |
| **Pickup Station P2** | `(-5.5, -7.0, 0.0)` | 🟢 Emerald Green **P** | Auxiliary cargo receiving bay (SW zone) |
| **Drop Station D1** | `(0.0, -8.1, 0.0)` | 🔵 Royal Blue **D** | Packing, sorting, and dispatch area (South bay) |
| **Charging Station** | `(5.5, -7.5, 0.0)` | 🟡 Gold Battery + ⚡ Bolt | Autonomous induction docking station (SE zone) |
| **Intersection I1** | `(0.0, 5.2, 0.0)` | 🔴 Red Cross + Bollards | High-traffic north corridor intersection |
| **Intersection I2** | `(0.0, -0.7, 0.0)` | 🔴 Red Cross + Bollards | High-traffic south corridor intersection |
| **Shelf Rack S1 (NW1)**| `(-4.8, 7.5, 0.0)` | ⬛ Black **S1** (on top) | High-bay pallet inventory rack 1 |
| **Shelf Rack S2 (NE1)**| `(4.8, 7.5, 0.0)` | ⬛ Black **S2** (on top) | High-bay pallet inventory rack 2 |
| **Shelf Rack S3 (NW2)**| `(-4.8, 3.0, 0.0)` | ⬛ Black **S3** (on top) | High-bay pallet inventory rack 3 |
| **Shelf Rack S4 (NE2)**| `(4.8, 3.0, 0.0)` | ⬛ Black **S4** (on top) | High-bay pallet inventory rack 4 |
| **Shelf Rack S5 (SW2)**| `(-4.8, 1.5, 0.0)` | ⬛ Black **S5** (on top) | High-bay pallet inventory rack 5 |
| **Shelf Rack S6 (SE2)**| `(4.8, 1.5, 0.0)` | ⬛ Black **S6** (on top) | High-bay pallet inventory rack 6 |
| **Shelf Rack S7 (SW1)**| `(-4.8, -3.0, 0.0)`| ⬛ Black **S7** (on top) | High-bay pallet inventory rack 7 |
| **Shelf Rack S8 (SE1)**| `(4.8, -3.0, 0.0)`| ⬛ Black **S8** (on top) | High-bay pallet inventory rack 8 |

---

## 🤖 Active AMR Fleet & ROS 2 / Gazebo Topic Interface

All 3 AMRs operate under isolated namespaces to support true multi-robot decentralized control:

```
                  ┌───────────────────────────────┐
                  │    Warehouse Simulation       │
                  └──────────────┬────────────────┘
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   [ AMR Blue ]            [ AMR Green ]           [ AMR Orange ]
   /amr_blue/cmd_vel       /amr_green/cmd_vel      /amr_orange/cmd_vel
   /amr_blue/odom          /amr_green/odom         /amr_orange/odom
   /amr_blue/scan          /amr_green/scan         /amr_orange/scan
   /amr_blue/tf            /amr_green/tf           /amr_orange/tf
   /amr_blue_contact       /amr_green_contact      /amr_orange_contact
```

### Fleet Topic Specifications

| Robot | Theme | Initial Spawn `(X, Y, Z)` | Velocity Control (Pub) | Odometry Feedback (Sub) | 2D LiDAR (Sub) | Bumper Contact (Sub) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AMR Blue** | 🔵 Sapphire Blue | `(-3.5, 5.25, 0.05)` | `/amr_blue/cmd_vel` | `/amr_blue/odom` | `/amr_blue/scan` | `/amr_blue_contact` |
| **AMR Green** | 🟢 Emerald Green | `(0.5, 8.5, 0.05)` | `/amr_green/cmd_vel` | `/amr_green/odom` | `/amr_green/scan` | `/amr_green_contact` |
| **AMR Orange**| 🟠 Safety Orange | `(3.5, -6.5, 0.05)` | `/amr_orange/cmd_vel` | `/amr_orange/odom` | `/amr_orange/scan` | `/amr_orange_contact` |

### Sample Velocity Commands (Gazebo CLI)

```bash
# Drive AMR Blue forward at 0.5 m/s
gz topic -t "/amr_blue/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.0}"

# Rotate AMR Green counter-clockwise at 0.8 rad/s
gz topic -t "/amr_green/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.0}, angular: {z: 0.8}"

# Stop AMR Orange
gz topic -t "/amr_orange/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.0}, angular: {z: 0.0}"
```

---

## 📁 Directory Structure & Model Catalog

```
gazebo/
├── README.md                       # Comprehensive master documentation
├── scripts/                        # Cross-platform simulation execution scripts
│   ├── launch_sim.py               # Universal launcher (macOS, Linux, Windows)
│   ├── launch_sim.sh               # POSIX Bash launcher (macOS / Linux)
│   ├── launch_sim.bat              # Windows Command Prompt batch script
│   └── launch_sim.ps1              # Windows PowerShell script
└── simulation/
    ├── models/                     # Modular simulation models (SDF 1.9)
    │   ├── amr/                    # Base AMR model template with lidar & diff-drive
    │   ├── amr_blue/               # AMR Blue model instance (/amr_blue)
    │   ├── amr_green/              # AMR Green model instance (/amr_green)
    │   ├── amr_orange/             # AMR Orange model instance (/amr_orange)
    │   ├── shelf/                  # 3-tier industrial warehouse rack with cargo boxes
    │   ├── pickup_station/         # Floor intake staging zone with 45° hazard lines
    │   ├── drop_station/           # Floor discharge zone with 45° hazard lines
    │   ├── charging_station/       # Induction charging dock with status LED indicator
    │   ├── pallet_stack/           # Stack of wooden logistics pallets
    │   ├── dumpster/               # Industrial recycling disposal container
    │   └── obstacle/               # Safety bollard obstacle
    └── worlds/
        ├── warehouse.sdf           # Master competition warehouse world
        └── amr_test.sdf            # Lightweight single-robot testing ground
```

---

## 🔧 Troubleshooting & Platform FAQs

### 1. `gz sim: command not found`
- **Linux:** Ensure Gazebo Harmonic is installed: `sudo apt install gz-harmonic`
- **macOS:** Ensure Homebrew path is in your shell profile: `brew install gz-harmonic`
- **Windows:** Add `C:\Program Files\condabin` or your Gazebo installation path to Environment Variable `Path`.

### 2. macOS: GUI opens but displays a blank window or fails to connect
On macOS, loopback multicast routing must be directed to `127.0.0.1`:
```bash
sudo route change -net 224.0.0.0/4 127.0.0.1
```
Then use the provided launcher: `./scripts/launch_sim.py`.

### 3. Model meshes or textures not showing
The launchers automatically set `GZ_SIM_RESOURCE_PATH` to `<project_root>/simulation/models`. If running `gz sim` manually, export it first:
```bash
export GZ_SIM_RESOURCE_PATH="$(pwd)/simulation/models:$GZ_SIM_RESOURCE_PATH"
```
