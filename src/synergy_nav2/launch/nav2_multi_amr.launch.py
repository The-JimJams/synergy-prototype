#!/usr/bin/env python3
import os
import sys
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

ROBOT_SPECS = {
    'amr_a': {
        'gz_model': 'amr_blue',
        'params_file': 'nav2_params_amr_a.yaml',
        'base_frame': 'amr_blue/base_link',
        'lidar_frame': 'amr_blue/lidar_link/lidar_2d',
    },
    'amr_b': {
        'gz_model': 'amr_green',
        'params_file': 'nav2_params_amr_b.yaml',
        'base_frame': 'amr_green/base_link',
        'lidar_frame': 'amr_green/lidar_link/lidar_2d',
    },
    'amr_c': {
        'gz_model': 'amr_orange',
        'params_file': 'nav2_params_amr_c.yaml',
        'base_frame': 'amr_orange/base_link',
        'lidar_frame': 'amr_orange/lidar_link/lidar_2d',
    },
}


def build_robot_nav2_group(robot_id, pkg_dir, map_yaml, use_sim_time):
    spec = ROBOT_SPECS[robot_id]
    params_path = os.path.join(pkg_dir, 'config', spec['params_file'])

    # TF publisher for LiDAR frame
    tf_node = Node(
        package='synergy_nav2',
        executable='dynamic_lidar_tf',
        name=f'dynamic_lidar_tf_{robot_id}',
        parameters=[{
            'base_frame_id': spec['base_frame'],
            'child_frame_id': spec['lidar_frame'],
            'use_sim_time': use_sim_time,
        }],
        output='screen',
    )

    # Nav2 stack group inside robot namespace
    nav2_stack = GroupAction(
        actions=[
            PushRosNamespace(robot_id),
            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                parameters=[params_path, {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}],
                output='screen',
            ),
            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                parameters=[params_path, {'use_sim_time': use_sim_time}],
                output='screen',
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                parameters=[params_path, {'use_sim_time': use_sim_time}],
                output='screen',
            ),
            Node(
                package='nav2_controller',
                executable='controller_server',
                name='controller_server',
                parameters=[params_path, {'use_sim_time': use_sim_time}],
                output='screen',
            ),
            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                parameters=[params_path, {'use_sim_time': use_sim_time}],
                output='screen',
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                parameters=[params_path, {'use_sim_time': use_sim_time}],
                output='screen',
            ),
            TimerAction(
                period=5.0,
                actions=[
                    Node(
                        package='nav2_lifecycle_manager',
                        executable='lifecycle_manager',
                        name='lifecycle_manager',
                        parameters=[params_path, {'use_sim_time': use_sim_time}],
                        output='screen',
                    )
                ]
            ),
        ]
    )

    return tf_node, nav2_stack


def generate_launch_description():
    pkg_synergy_nav2 = get_package_share_directory('synergy_nav2')
    default_map = os.path.join(pkg_synergy_nav2, 'maps', 'warehouse_map.yaml')

    map_yaml_cmd = DeclareLaunchArgument('map', default_value=default_map, description='Warehouse map path')
    use_sim_time_cmd = DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation clock')

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Comprehensive multi-robot ros_gz_bridge
    bridge_arguments = [
        # Clock
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
    ]
    bridge_remappings = []

    for r_id, spec in ROBOT_SPECS.items():
        gz_m = spec['gz_model']
        bridge_arguments.extend([
            f'/{gz_m}/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            f'/{gz_m}/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            f'/{gz_m}/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            f'/{gz_m}/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ])
        bridge_remappings.extend([
            (f'/{gz_m}/odom', f'/{r_id}/odom'),
            (f'/{gz_m}/scan', f'/{r_id}/scan'),
            (f'/{gz_m}/cmd_vel', f'/{r_id}/cmd_vel'),
            (f'/{gz_m}/tf', '/tf'),
        ])

    unified_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_multi_amr',
        arguments=bridge_arguments,
        remappings=bridge_remappings,
        output='screen',
    )

    ld = LaunchDescription()
    ld.add_action(map_yaml_cmd)
    ld.add_action(use_sim_time_cmd)
    ld.add_action(unified_bridge)

    # Launch TF and Nav2 for all 3 AMRs
    for robot_id in ('amr_a', 'amr_b', 'amr_c'):
        tf_node, nav2_group = build_robot_nav2_group(robot_id, pkg_synergy_nav2, map_yaml, use_sim_time)
        ld.add_action(tf_node)
        ld.add_action(nav2_group)

    return ld
