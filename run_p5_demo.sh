#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — P5 Distributed Task Failure & Recovery Demo
#  Runs the standalone distributed fault-tolerance demo without ROS 2.
#
#  Usage:
#    ./run_p5_demo.sh            # Run standalone demo
#    ./run_p5_demo.sh tests      # Run P5 tests only
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

CYAN='\033[0;36m'; BOLD='\033[1m'; GREEN='\033[0;32m'
YELLOW='\033[1;33m'; RED='\033[0;31m'; RESET='\033[0m'

MODE="${1:-demo}"

# ── Activate venv if present ───────────────────────────────────────────────────
if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
    # shellcheck source=/dev/null
    source "$PROJECT_ROOT/venv/bin/activate"
fi

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║   🔧  SYNERGY — P5 Task Failure & Recovery Subsystem        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

if [[ "$MODE" == "tests" ]]; then
    echo -e "${CYAN}[INFO]${RESET}  Running P5 test suite..."
    python3 -m pytest p5_task_failure/tests -v --tb=short
else
    echo -e "${CYAN}[INFO]${RESET}  Launching standalone failure/recovery simulation demo..."
    echo -e "${YELLOW}[INFO]${RESET}  Pure Python — no ROS 2 or Gazebo required."
    echo ""
    python3 p5_task_failure/simulation/standalone_demo.py
fi
