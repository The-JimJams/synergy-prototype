#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — ROS 2 Full Stack Launcher
#  Builds the ROS 2 workspace with colcon and spawns all 3 AMR nodes.
#
#  Requires: ROS 2 (Humble / Iron / Jazzy / Lyrical) installed and sourced.
#
#  Usage:
#    ./run_ros2_stack.sh [ros-distro]
#
#  Examples:
#    ./run_ros2_stack.sh          # auto-detect distro
#    ./run_ros2_stack.sh humble
#    ./run_ros2_stack.sh jazzy
#    ./run_ros2_stack.sh lyrical
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║   🔵  SYNERGY — ROS 2 Full Stack Builder & Launcher         ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Detect / source ROS 2 distro ──────────────────────────────────────────────
DISTRO="${1:-}"

if [[ -z "$DISTRO" ]]; then
    # Try to detect from environment
    if [[ -n "${ROS_DISTRO:-}" ]]; then
        DISTRO="$ROS_DISTRO"
        info "Detected active ROS 2 distro from environment: ${BOLD}${DISTRO}${RESET}"
    else
        # Probe common distros in priority order
        for d in lyrical jazzy iron humble; do
            if [[ -f "/opt/ros/${d}/setup.bash" ]]; then
                DISTRO="$d"
                break
            fi
        done
    fi
fi

[[ -z "$DISTRO" ]] && error "No ROS 2 installation found in /opt/ros/. Install ROS 2 first:\n  https://docs.ros.org/en/humble/Installation.html"

ROS_SETUP="/opt/ros/${DISTRO}/setup.bash"
[[ -f "$ROS_SETUP" ]] || error "ROS 2 setup file not found: ${ROS_SETUP}\n  Is '${DISTRO}' installed?"

info "Sourcing ROS 2 ${DISTRO}..."
# shellcheck source=/dev/null
source "$ROS_SETUP"
success "ROS 2 ${DISTRO} sourced."

# ── Check colcon ───────────────────────────────────────────────────────────────
command -v colcon &>/dev/null || error "colcon not found. Install with:\n  sudo apt install python3-colcon-common-extensions"
success "colcon found: $(colcon version-check 2>&1 | head -n1 || echo 'ok')"

# ── Build workspace ────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Step 1/3 — Building ROS 2 workspace with colcon${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
info "Running: colcon build --symlink-install"
colcon build --symlink-install
success "Workspace built."

# ── Source install overlay ─────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Step 2/3 — Sourcing install overlay${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
# shellcheck source=/dev/null
source "$PROJECT_ROOT/install/setup.bash"
success "Install overlay sourced."

# ── Launch task allocator nodes ────────────────────────────────────────────────
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Step 3/3 — Launching the fleet stack (agents, allocators, bridge)${RESET}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# The bringup launch starts, per robot: fleet_agent_node (map-frame telemetry on
# /<id>/state + heartbeat) and task_allocator_node (announce/bid/win/Nav2 goal),
# plus the read-only dashboard_bridge_node.  Launching the allocators on their own
# left /<id>/state silent, so every bid scored from a default (0,0) position and
# the dashboard had no live pose to draw.
info "Launching fleet agents + task allocators + dashboard bridge (bringup.launch.py)..."
ros2 launch robot_bringup bringup.launch.py &

# rosbridge is what the Flask dashboard's live adapter connects to on :9090.
# It is optional: the fleet coordinates perfectly well without it.
if ros2 pkg prefix rosbridge_server &>/dev/null; then
    info "Launching rosbridge_server on :9090 (dashboard live telemetry)..."
    ros2 launch rosbridge_server rosbridge_websocket_launch.xml &
else
    echo -e "${YELLOW}[WARN]${RESET}  rosbridge_server not installed; the dashboard cannot enter LIVE mode."
    echo -e "         Install with: ${BOLD}sudo apt install ros-${DISTRO}-rosbridge-suite${RESET}"
fi

success "Fleet stack launched. Press Ctrl+C to stop all."
echo ""
echo -e "${YELLOW}[TIP]${RESET}  Monitor topics with:"
echo -e "         ${BOLD}ros2 topic list${RESET}"
echo -e "         ${BOLD}ros2 topic echo /amr_a/state${RESET}          # map-frame pose"
echo -e "         ${BOLD}ros2 topic echo /tasks/announcements${RESET}  # task announcements"
echo -e "         ${BOLD}ros2 topic echo /tasks/bids${RESET}           # distributed bids"
echo ""

# ── Wait and clean up on exit ──────────────────────────────────────────────────
cleanup() {
    echo ""
    info "Shutting down all AMR nodes..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    success "All nodes stopped."
}
trap cleanup EXIT INT TERM

wait
