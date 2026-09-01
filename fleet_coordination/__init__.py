# Fleet Coordination Algorithm Package
# Decentralized AMR Fleet Coordination for Smart Warehouses
#
# This package contains the algorithmic subsystem for multi-robot
# coordination. It is designed to be ROS-agnostic — all algorithm
# logic lives in the algorithm/ subpackage and can be tested
# with plain pytest, without launching Gazebo or ROS 2.
#
# Subpackages:
#   config/        — Tunable parameters and thresholds
#   models/        — Pure data structures (dataclasses)
#   algorithm/     — Core coordination algorithms (ROS-free)
#   ros_interface/ — ROS 2 adapter layer (only ROS imports here)
#   tests/         — Unit tests (pytest, no ROS dependency)

__version__ = "0.1.0"
