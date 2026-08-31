# ROS 2 Part – AMR Fleet Coordination

This branch contains the ROS 2 implementation developed for the **SYNERGY decentralized AMR fleet coordination project**.

## Work Completed

* Set up the ROS 2 workspace using `colcon`
* Created the ROS 2 package structure
* Implemented the basic ROS 2 coordinator node in Python
* Created a ROS 2 publisher for robot/system status
* Added periodic status publishing
* Implemented the initial task-allocation logic
* Added robot/task status handling
* Added task execution and completion flow
* Prepared the ROS 2 code for integration with the team's AMR simulation

## Workspace Structure

```text
amr_ws/
└── src/
├── fleet_msgs/
│   ├── package.xml
│   ├── CMakeLists.txt
│   └── msg/
│       ├── Heartbeat.msg
│       ├── RobotState.msg
│       ├── TaskBid.msg
│       ├── TaskAnnouncement.msg
│       ├── ResourceClaim.msg
│       └── RobotIntent.msg
│
├── dashboard_bridge/
│   ├── package.xml
│   ├── setup.py
│   └── dashboard_bridge/
│       ├── __init__.py
│       └── dashboard_bridge_node.py
│
├── fleet_coordination/
│   ├── package.xml
│   ├── setup.py
│   └── fleet_coordination/
│       ├── __init__.py
│       └── fleet_agent_node.py
│
├── task_allocator/
│   ├── package.xml
│   ├── setup.py
│   └── task_allocator/
│       ├── __init__.py
│       └── task_allocator_node.py
│
└── robot_bringup/
    ├── package.xml
    ├── setup.py
    ├── robot_bringup/
    │   └── __init__.py
    └── launch/
        ├── bringup.launch.py
        └── .keep
```

## Build

From the workspace:

```bash
cd ~/amr_ws
colcon build
source install/setup.bash
```

## Run

After building and sourcing the workspace:

```bash
ros2 run <package_name> <node_name>
```

Replace `<package_name>` and `<node_name>` with the actual package and node names.

| Package              | Main purpose                       |
| -------------------- | ---------------------------------- |
| `fleet_msgs`         | Custom ROS 2 messages              |
| `dashboard_bridge`   | Dashboard ↔ ROS 2 communication    |
| `fleet_coordination` | Fleet Agent / coordination         |
| `task_allocator`     | Task allocation                    |
| `robot_bringup`      | Launch files / starting the system |


3 actual application nodes:
dashboard_bridge_node.py
fleet_agent_node.py
task_allocator_node.py

And bringup.launch.py is a launch file, not a node itself.

5 packages → 3 nodes + 1 message/interface package + 1 launch/bringup package.
The ROS 2 workspace contains five packages supporting three main executable nodes: Fleet Agent, Task Allocator, and Dashboard Bridge.

## Project Role

This ROS 2 component provides the communication and coordination layer for the AMR prototype. It is intended to integrate with the warehouse simulation developed by the other team members.

## Branch

**ROS2-part**

Part of the **SYNERGY – Decentralized AMR Fleet Coordination** project.
