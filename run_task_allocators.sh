#!/bin/bash
source ~/amr_ws/install/setup.bash

ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/robot_a -p robot_id:=robot_a -p is_announcer:=true &
ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/robot_b -p robot_id:=robot_b &
ros2 run task_allocator task_allocator_node --ros-args -r __ns:=/robot_c -p robot_id:=robot_c &

wait
