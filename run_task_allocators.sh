#!/bin/bash
source /workspace/synergy-prototype/install/setup.bash

ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/amr_a -p robot_id:=amr_a -p is_announcer:=true -p nav_enabled:=true &
ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/amr_b -p robot_id:=amr_b -p nav_enabled:=false &
ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/amr_c -p robot_id:=amr_c -p nav_enabled:=false &

wait
