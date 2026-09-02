#!/usr/bin/env bash
# ==============================================================================
#  SYNERGY — Master Setup Script
#  Installs all Python dependencies for the full project (no ROS 2 required).
#  Run this ONCE before using any other run_*.sh scripts.
# ==============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# ── Colours ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║         🤖  SYNERGY AMR Platform — Setup & Install          ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── Python version check ───────────────────────────────────────────────────────
PYTHON="python3"
PY_VER=$("$PYTHON" -c 'import sys; print(sys.version_info >= (3,10))' 2>/dev/null || echo "False")
[[ "$PY_VER" == "True" ]] || error "Python 3.10+ required. Found: $($PYTHON --version 2>&1)"
success "Python version OK: $($PYTHON --version)"

# ── Virtual environment ────────────────────────────────────────────────────────
if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
    info "Creating virtual environment at ./venv ..."
    "$PYTHON" -m venv venv
    success "Virtual environment created."
else
    info "Virtual environment already exists at ./venv — skipping creation."
fi

# ── Activate venv ──────────────────────────────────────────────────────────────
# shellcheck source=/dev/null
source "$PROJECT_ROOT/venv/bin/activate"
success "Virtual environment activated."

# ── Upgrade pip ────────────────────────────────────────────────────────────────
info "Upgrading pip..."
pip install --upgrade pip -q
success "pip up to date."

# ── Dashboard dependencies ─────────────────────────────────────────────────────
info "Installing dashboard dependencies (Flask, pytest)..."
pip install -r "$PROJECT_ROOT/dashboard/requirements.txt" -q
success "Dashboard dependencies installed."

# ── P5 Task Failure dependencies ───────────────────────────────────────────────
info "Installing P5 task-failure dependencies..."
pip install -r "$PROJECT_ROOT/p5_task_failure/requirements.txt" -q
success "P5 dependencies installed."

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║                  ✅  Setup Complete!                        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  Next steps — run any of these scripts:"
echo ""
echo -e "  ${CYAN}./run_dashboard.sh${RESET}         Launch dashboard in mock mode"
echo -e "  ${CYAN}./run_tests.sh${RESET}             Run the full 402-test suite"
echo -e "  ${CYAN}./run_p5_demo.sh${RESET}           Run P5 standalone failure demo"
echo -e "  ${CYAN}./run_gazebo.sh${RESET}            Launch Gazebo physics simulation"
echo -e "  ${CYAN}./run_ros2_stack.sh${RESET}        Build & launch full ROS 2 stack"
echo ""
echo -e "  ${YELLOW}Tip:${RESET} Always activate the venv first with:"
echo -e "  ${BOLD}  source venv/bin/activate${RESET}"
echo ""
