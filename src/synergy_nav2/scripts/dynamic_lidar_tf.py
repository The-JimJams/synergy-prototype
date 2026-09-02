#!/usr/bin/env python3
import sys
import os

# Add package to sys.path if not installed
pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_dir not in sys.path:
    sys.path.insert(0, pkg_dir)

from synergy_nav2.dynamic_lidar_tf import main

if __name__ == '__main__':
    main()
