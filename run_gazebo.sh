#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — Gazebo Warehouse Physics Simulation Launcher
#  Requires: Gazebo Sim Harmonic (or Garden/Fortress) installed.
#
#  Usage:
#    ./run_gazebo.sh              # Full simulation (server + GUI)
#    ./run_gazebo.sh --server     # Headless server-only mode
#    ./run_gazebo.sh --gui        # GUI client only (connect to running server)
#
#  Check if Gazebo is installed: gz sim --version
#  Install Gazebo Harmonic: https://gazebosim.org/docs/harmonic/install
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║   🏭  SYNERGY — Gazebo Warehouse Simulation Launcher        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Check Gazebo is installed ──────────────────────────────────────────────────
if ! command -v gz &>/dev/null; then
    echo -e "${RED}[ERROR]${RESET} Gazebo (gz) not found on PATH."
    echo ""
    echo -e "  Install Gazebo Harmonic from:"
    echo -e "  ${CYAN}https://gazebosim.org/docs/harmonic/install${RESET}"
    echo ""
    echo -e "  macOS (Homebrew):   ${BOLD}brew install gz-harmonic${RESET}"
    echo -e "  Ubuntu:             ${BOLD}sudo apt-get install gz-harmonic${RESET}"
    exit 1
fi

GZ_VERSION=$(gz sim --version 2>&1 | head -n1)
echo -e "${GREEN}[OK]${RESET}    Gazebo found: ${GZ_VERSION}"
echo ""

# ── Forward all arguments to the existing launch script ───────────────────────
echo -e "${CYAN}[INFO]${RESET}  Delegating to gazebo/scripts/launch_sim.sh $*"
echo ""

bash "$PROJECT_ROOT/gazebo/scripts/launch_sim.sh" "$@"
