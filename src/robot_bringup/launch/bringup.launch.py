#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import GroupAction
from launch_ros.actions import Node
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    robot_names = ['amr_a', 'amr_b', 'amr_c']

    groups = []
    for robot_name in robot_names:
        groups.append(
            GroupAction(
                actions=[
                    PushRosNamespace(robot_name),
                    Node(
                        package='fleet_coordination',
                        executable='fleet_agent_node',
                        name='fleet_agent_node',
                        parameters=[{'robot_id': robot_name}],
                        output='screen',
                    ),
                    Node(
                        package='task_allocator',
                        executable='task_allocator_node',
                        name='task_allocator_node',
                        parameters=[{
                            'robot_id': robot_name,
                            'is_announcer': robot_name == 'amr_a',
                            'nav_enabled': True,
                        }],
                        output='screen',
                    ),
                ]
            )
        )

    groups.append(
        Node(
            package='dashboard_bridge',
            executable='dashboard_bridge_node',
            name='dashboard_bridge_node',
            output='screen',
        )
    )

    return LaunchDescription(groups)
