import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, TimerAction, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    pkg_synergy_nav2 = get_package_share_directory('synergy_nav2')

    default_map = os.path.join(pkg_synergy_nav2, 'maps', 'warehouse_map.yaml')
    default_params = os.path.join(pkg_synergy_nav2, 'config', 'nav2_params_amr_a.yaml')

    map_yaml_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Full path to map file to load',
    )

    params_file_cmd = DeclareLaunchArgument(
        'params_file',
        default_value=default_params,
        description='Full path to the ROS 2 parameters file for Nav2',
    )

    use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true',
    )

    map_yaml = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # 1. ros_gz_bridge node for AMR A
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_amr_a',
        arguments=[
            '/amr_blue/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/amr_blue/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/amr_blue/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/amr_blue/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        remappings=[
            ('/amr_blue/odom', '/amr_a/odom'),
            ('/amr_blue/scan', '/amr_a/scan'),
            ('/amr_blue/cmd_vel', '/amr_a/cmd_vel'),
            ('/amr_blue/tf', '/tf'),
        ],
        output='screen',
    )

    # 3. Nav2 stack for AMR A inside /amr_a namespace
    nav2_nodes = GroupAction(
        actions=[
            PushRosNamespace('amr_a'),

            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                output='screen',
                parameters=[params_file, {'yaml_filename': map_yaml, 'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_amcl',
                executable='amcl',
                name='amcl',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_controller',
                executable='controller_server',
                name='controller_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_bt_navigator',
                executable='bt_navigator',
                name='bt_navigator',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            Node(
                package='nav2_behaviors',
                executable='behavior_server',
                name='behavior_server',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
            TimerAction(
                period=5.0,
                actions=[
                    Node(
                        package='nav2_lifecycle_manager',
                        executable='lifecycle_manager',
                        name='lifecycle_manager',
                        output='screen',
                        parameters=[params_file, {'use_sim_time': use_sim_time}],
                    )
                ]
            ),
        ]
    )

    dynamic_tf_cmd = ExecuteProcess(
        cmd=['python3', '/workspace/synergy-prototype/src/synergy_nav2/scripts/dynamic_lidar_tf.py'],
        output='screen'
    )

    ld = LaunchDescription()
    ld.add_action(map_yaml_cmd)
    ld.add_action(params_file_cmd)
    ld.add_action(use_sim_time_cmd)
    ld.add_action(bridge_node)
    ld.add_action(dynamic_tf_cmd)

    ld.add_action(nav2_nodes)

    return ld
