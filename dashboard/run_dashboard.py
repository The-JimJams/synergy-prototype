"""
SYNERGY Dashboard — Standalone Launcher Script
================================================

Usage:
    python run_dashboard.py [--mode mock|ros2] [--scenario full_demo] [--speed 1.0] [--port 5000]
"""

import sys
import os

# Ensure dashboard root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import main

if __name__ == "__main__":
    main()
