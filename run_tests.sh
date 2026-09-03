#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — Full Test Suite Runner
#  Runs all 402 automated tests across all subsystems.
#
#  Usage:
#    ./run_tests.sh               # Run all tests
#    ./run_tests.sh fleet         # Only fleet_coordination tests (323)
#    ./run_tests.sh dashboard     # Only dashboard tests (79)
#    ./run_tests.sh p5            # Only P5 task failure tests
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

SUITE="${1:-all}"

# ── Activate venv if present ───────────────────────────────────────────────────
if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║            🧪  SYNERGY — Test Suite Runner                  ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Validate pytest ────────────────────────────────────────────────────────────
python3 -m pytest --version 2>/dev/null || {
    echo -e "${RED}[ERROR]${RESET} pytest not found. Run ${BOLD}./setup.sh${RESET} first."
    exit 1
}

PASS=0
FAIL=0

run_suite() {
    local name="$1"
    local path="$2"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}  🔬 Running: ${name}${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    if python3 -m pytest "$path" -v --tb=short; then
        echo -e "${GREEN}  ✅ ${name} — PASSED${RESET}"
        PASS=$((PASS + 1))
    else
        echo -e "${RED}  ❌ ${name} — FAILED${RESET}"
        FAIL=$((FAIL + 1))
    fi
    echo ""
}

case "$SUITE" in
    fleet)
        run_suite "Fleet Coordination Algorithm Tests" "fleet_coordination/tests"
        ;;
    dashboard)
        run_suite "Dashboard REST API, Telemetry & Live Adapter Tests" "dashboard/tests"
        ;;
    p5)
        run_suite "P5 Task Failure & Recovery Tests" "p5_task_failure/tests"
        ;;
    allocator)
        run_suite "Task Allocation & Bidding Regression" "src/task_allocator/test"
        ;;
    all|*)
        run_suite "Fleet Coordination Algorithm Tests"                "fleet_coordination/tests"
        run_suite "Task Allocation & Bidding Regression"              "src/task_allocator/test"
        run_suite "Dashboard REST API, Telemetry & Live Adapter Tests" "dashboard/tests"
        run_suite "P5 Task Failure & Recovery Tests"                  "p5_task_failure/tests"
        ;;
esac

# ── Simulation checks that need a running Gazebo / warehouse map ───────────────
# The map/costmap check is pure offline analysis and always runs.
run_suite_cmd() {
    local name="$1"; shift
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${BOLD}  🔬 Running: ${name}${RESET}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    if "$@"; then
        echo -e "${GREEN}  ✅ ${name} — PASSED${RESET}"; PASS=$((PASS + 1))
    else
        echo -e "${RED}  ❌ ${name} — FAILED${RESET}"; FAIL=$((FAIL + 1))
    fi
    echo ""
}

if [[ "$SUITE" == "all" || "$SUITE" == "map" ]]; then
    run_suite_cmd "Warehouse Map / Costmap / Route Feasibility" \
        python3 "$PROJECT_ROOT/src/synergy_nav2/tools/verify_map_routes.py"
fi

# LiDAR obstacle visibility needs a live Gazebo server; skipped when none is up.
if [[ "$SUITE" == "all" || "$SUITE" == "lidar" ]]; then
    if GZ_IP=127.0.0.1 gz topic -l 2>/dev/null | grep -q "/amr_blue/scan"; then
        run_suite_cmd "LiDAR Obstacle Visibility (live Gazebo)" \
            env GZ_IP=127.0.0.1 python3 "$PROJECT_ROOT/gazebo/scripts/verify_lidar_obstacles.py"
    else
        echo -e "${YELLOW}[SKIP]${RESET}  LiDAR obstacle check — no Gazebo server publishing /amr_blue/scan."
        echo -e "         Start one with: ${BOLD}./run_gazebo.sh --server${RESET}"
        echo ""
    fi
fi

# ── Summary ────────────────────────────────────────────────────────────────────
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
if [[ "$FAIL" -eq 0 ]]; then
    echo -e "${BOLD}║  ${GREEN}✅  All test suites passed (${PASS}/${PASS} suites)${RESET}${BOLD}                    ║${RESET}"
else
    echo -e "${BOLD}║  ${RED}❌  ${FAIL} suite(s) failed, ${PASS} passed${RESET}${BOLD}                             ║${RESET}"
fi
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
