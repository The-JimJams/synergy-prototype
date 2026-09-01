#!/usr/bin/env bash
# ==============================================================================
# Multi-AMR Warehouse Simulation - POSIX Shell Launcher (Linux & macOS)
# Automatically detects OS and handles macOS background server splitting
# ==============================================================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export GZ_IP=127.0.0.1
export GZ_SIM_RESOURCE_PATH="${PROJECT_ROOT}/simulation/models:${GZ_SIM_RESOURCE_PATH}"

OS_NAME="$(uname -s)"

echo "=================================================="
echo " 🤖 Starting AMR Warehouse Simulation Environment"
echo " Detected OS       : ${OS_NAME}"
echo " Project Directory : ${PROJECT_ROOT}"
echo " GZ_IP             : ${GZ_IP}"
echo " GZ_SIM_RESOURCE_PATH : ${GZ_SIM_RESOURCE_PATH}"
echo "=================================================="

# 1. Server-Only Mode
if [[ "$1" == "--server" || "$1" == "-s" ]]; then
  echo "[+] Launching in Headless (Server) Mode..."
  gz sim -s -r "${PROJECT_ROOT}/simulation/worlds/warehouse.sdf"

# 2. GUI-Only Mode
elif [[ "$1" == "--gui" || "$1" == "-g" ]]; then
  echo "[+] Launching GUI Client only..."
  gz sim -g

# 3. Full Simulation (Server + GUI)
else
  if [[ "${OS_NAME}" == "Darwin" ]]; then
    echo "[+] macOS detected: Spawning background server and foreground GUI..."
    gz sim -s -r "${PROJECT_ROOT}/simulation/worlds/warehouse.sdf" &
    SERVER_PID=$!

    cleanup() {
      echo ""
      echo "[+] Terminating background simulation server (PID: ${SERVER_PID})..."
      kill "${SERVER_PID}" 2>/dev/null
      wait "${SERVER_PID}" 2>/dev/null
      echo "[+] Cleaned up successfully."
    }
    trap cleanup EXIT INT TERM

    sleep 1.5
    gz sim -g
  else
    echo "[+] Linux/POSIX detected: Launching unified Gazebo process..."
    gz sim -r "${PROJECT_ROOT}/simulation/worlds/warehouse.sdf"
  fi
fi
