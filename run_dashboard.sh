#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — Dashboard Launcher
#  Runs the Fleet Operations Command Center (Flask web UI).
#
#  Usage:
#    ./run_dashboard.sh [mock|ros2] [scenario] [port]
#
#  Examples:
#    ./run_dashboard.sh                           # mock + full_demo + port 5055
#    ./run_dashboard.sh mock intersection_conflict 5055
#    ./run_dashboard.sh ros2                       # live ROS 2 mode
#
#  Scenarios: full_demo | normal_ops | intersection_conflict
#             task_failure | battery_charging | blocked_aisle
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

MODE="${1:-mock}"
SCENARIO="${2:-full_demo}"
PORT="${3:-5055}"

# ── Activate venv if present ───────────────────────────────────────────────────
if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║       🖥️  SYNERGY Fleet Operations Command Center           ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${CYAN}Mode     :${RESET} ${BOLD}${MODE}${RESET}"

if [[ "$MODE" == "mock" ]]; then
    echo -e "  ${CYAN}Scenario :${RESET} ${BOLD}${SCENARIO}${RESET}"
fi

echo -e "  ${CYAN}Port     :${RESET} ${BOLD}${PORT}${RESET}"
echo -e "  ${CYAN}URL      :${RESET} ${BOLD}http://localhost:${PORT}${RESET}"
echo ""

# ── Validate Flask is available ────────────────────────────────────────────────
python3 -c "import flask" 2>/dev/null || {
    echo -e "${RED}[ERROR]${RESET} Flask not found. Run ${BOLD}./setup.sh${RESET} first."
    exit 1
}

echo -e "${GREEN}[OK]${RESET}    Flask found. Starting server..."
echo -e "${YELLOW}[INFO]${RESET}  Press Ctrl+C to stop."
echo ""

# ── Launch ─────────────────────────────────────────────────────────────────────
if [[ "$MODE" == "ros2" ]]; then
    python3 dashboard/run_dashboard.py --mode ros2 --port "$PORT"
else
    python3 dashboard/run_dashboard.py --mode mock --scenario "$SCENARIO" --port "$PORT"
fi
