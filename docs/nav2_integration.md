# Nav2 Integration Plan & Analysis

This document provides a verified, concrete plan for integrating Nav2 with the existing Gazebo multi-AMR simulation and the pure-Python Fleet Coordination Agent.

## 1. Verified Gazebo Interfaces

Based on direct inspection of `amr_blue/model.sdf` and `warehouse.sdf`:

### AMR Blue
- **Model Name:** `amr_blue`
- **Spawn Pose:** `(-3.5, 5.25, 0.05, 0, 0, 0)` (from `warehouse.sdf`)
- **Robot Footprint:** The collision geometry is `0.60 x 0.50m`. The bumper visual is `0.62 x 0.52m`. For Nav2 costmaps, the footprint polygon should be `[[-0.31, -0.26], [0.31, -0.26], [0.31, 0.26], [-0.31, 0.26]]`.
- **Odometry Topic:** `/amr_blue/odom` (Published at 20Hz)
- **LiDAR Topic:** `/amr_blue/scan` (720 samples, range 0.1m - 10.0m, 15Hz)
- **cmd_vel Topic:** `/amr_blue/cmd_vel`
- **TF Topic:** `/amr_blue/tf`
- **Kinematics:** Differential drive (`wheel_separation=0.50`, `wheel_radius=0.10`). Max linear velocity is `1.2 m/s`, max angular velocity is `2.0 rad/s`.

## 2. Verified AMR Frames & TF Analysis

From the `gz-sim-diff-drive-system` plugin configuration:
- **Odometry Frame:** `amr_blue/odom`
- **Base Frame:** `amr_blue/base_link`
- **LiDAR Frame:** `lidar_link` (Fixed joint to `base_link`)

### TF Remapping Strategy
**Decision:** Do *not* aggressively remap TF frame IDs from `amr_blue` to `amr_a`. 
Rewriting frame IDs inside TFMessage streams via bridges is brittle and complex. Instead, Nav2 will be launched in the logical `/amr_a` namespace (for topics and services), but configured via `nav2_params.yaml` to natively expect `amr_blue/odom` and `amr_blue/base_link` as its frames. This is the simplest and safest approach. 

## 3. Warehouse Navigation Requirements

From `warehouse.sdf`:
- **Dimensions:** The warehouse floor is precisely `20.0m x 20.0m` (despite any older documentation claiming 20x15m).
- **Geometry:** Bounded by 4 static walls (North, South, East, West) forming the perimeter.
- **Obstacles:** Static industrial shelving racks and vertical I-beam pillars.
- **Map Feasibility:** The geometry is entirely static and perfect for a 2D occupancy grid map (`warehouse_map.yaml` & `.pgm`). 

## 4. Proposed Nav2 Architecture

The architecture will bridge Gazebo to ROS 2 without modifying the underlying algorithmic core.

```text
[ Gazebo Sim ]
      |
      | (/amr_blue/odom, /amr_blue/scan, /amr_blue/tf)
      v
[ ros_gz_bridge ]
      |
      | (Mapped to /amr_a/odom, /amr_a/scan, /tf)
      v
[ ROS 2 (Namespace: /amr_a) ]
      |
      +-- AMCL (Localization: map -> amr_blue/odom)
      +-- Map Server (Provides warehouse_map)
      +-- Nav2 Stack (Planner, Controller, BT Navigator)
      |
      v (Velocity commands)
[ Velocity Smoother / Gating Node ]
      |
      | (/amr_a/cmd_vel) -> Bridged back to Gazebo
      v
[ Gazebo Sim ]
```

## 5. AMR A Integration Sequence

1. **Mapping:** Create the static `warehouse_map.yaml` & `.pgm` covering the 20x20m area.
2. **Bridge Configuration:** Launch `ros_gz_bridge` bridging specific topics to the `/amr_a` ROS 2 namespace.
3. **Nav2 Parameters:** Create `nav2_params_amr_a.yaml`:
   - Set `robot_base_frame: amr_blue/base_link`
   - Set `odom_frame: amr_blue/odom`
   - Configure DWB controller with max velocities (x: 1.2, theta: 2.0).
4. **Validation:** Send a `/amr_a/navigate_to_pose` goal and verify reaching the target.

## 6. Future A/B/C Replication Strategy

Once AMR A is validated, AMR B (Green) and AMR C (Orange) will be deployed identically.
- **Shared Resources:** One global Map Server node to save memory.
- **Isolated Stacks:** Dedicated AMCL and Nav2 bringup groups within namespaces `/amr_b` and `/amr_c`.
- **Isolated TF Trees:** AMCL instances will independently maintain `map -> amr_green/odom` and `map -> amr_orange/odom`.

## 7. Fleet Agent → Nav2 Control Strategy

When the Fleet Agent's `ConflictDetector` and `PriorityEngine` determine that an AMR must yield (e.g., at an intersection), the Agent must physically stop the robot.

**Recommended Approach: Velocity Gating via Velocity Smoother**
Instead of sending a complex goal-cancel to Nav2's Behavior Tree or writing a custom BT node, the Fleet Agent can simply call the parameter service of a ROS 2 Velocity Smoother node placed between Nav2's output and the Gazebo bridge. 
- **WAIT:** Agent sets `max_velocity = 0.0`. The robot halts safely. Nav2 continues computing plans but output is throttled to 0.
- **PROCEED:** Agent restores `max_velocity = 1.2`. The robot resumes following the Nav2 plan.
*Note: This is an integration decision and requires no modification to the pure-Python Fleet Agent core.*

## 8. Dependencies on Unfinished ROS 2 Work

The execution of this plan cannot begin until the teammate provides the ROS 2 workspace, specifically:
- The base `ros2_ws/src/synergy_nav2` package structure and build files.
- The `synergy_interfaces` package providing `RobotState.msg` and `RobotIntent.msg`.
- The final `synergy_fleet` ROS 2 wrapper nodes for the Python Fleet Agent.

## 9. Open Questions to Resolve Later
- **Static TF:** Will a `robot_state_publisher` be needed to publish `amr_blue/base_link -> lidar_link`, or does Gazebo bridge this automatically via the fixed joint?
- **Task Integration:** How will the pending Task Allocation node pass specific destinations to the Nav2 Action Client?

## 10. Navigation Map Design

### 1. Warehouse Geometry
- **Floor Boundaries:** `20.0m x 20.0m`
- **Perimeter Walls:** Bounding the `20x20m` space (`north_wall`, `south_wall`, `east_wall`, `west_wall`), each 0.15m thick.
- **Shelves:** 8 blocks (`NW1, NE1, NW2, NE2, SW2, SE2, SW1, SE1`) located at strict coordinates (e.g., `-4.8, 7.5`, `4.8, 7.5`).
- **Pillars/Bollards:** 12 wall pillars (I-beams) and 4 intersection choke bollards (`l1, r1, l2, r2`).
- **Obstacles:** `blocked_aisle_obstacle` at `(-0.2, 0.75)`, pallets (`pallet_tower_1/2/3`), and `green_dumpster_container` (`-2.8, -7.3`).
- **Stations:** `pickup_P1` (`0, 8.0`), `pickup_P2` (`-5.5, -7.0`), `drop_pack_D1` (`0, -8.1`), `charging_bay` (`5.5, -7.5`).

### 2. Recommended Map Generation Method
**Generating a static occupancy grid directly from the known SDF geometry** is highly recommended over simulated SLAM.
- **Why:** The warehouse is perfectly static, with geometric primitives (boxes) placed at exact coordinates. SLAM introduces noise, misalignment, and artifacts. Generating the `.pgm` programmatically (e.g., via a Python script drawing the SDF bounding boxes onto an image matrix) guarantees a perfect, flawless map. Crucially, this can be done immediately *without* waiting for the missing ROS 2 teammate's workspace.

### 3. Map Coordinate System
The map origin must perfectly align with Gazebo's world origin `(0, 0, 0)`.
- For a `20x20m` floor, the origin (bottom-left corner of the image) in Gazebo coordinates is `(-10.0, -10.0)`.
- Nav2 Map YAML `origin: [-10.0, -10.0, 0.0]`.

### 4. Proposed Map Resolution
- **Resolution:** `0.05 meters/pixel` (Nav2 standard).
- **Image Size:** `400 x 400` pixels (for precisely 20x20m).

### 5. Robot Footprint
- The collision geometry is `0.60 x 0.50m`. 
- The bumper visual is `0.62 x 0.52m`.
- To ensure absolute safety around narrow bollards and obstacles, Nav2 should use the bumper dimensions. 
- **Polygon Configuration:** `footprint: "[[-0.31, -0.26], [-0.31, 0.26], [0.31, 0.26], [0.31, -0.26]]"`

### 6. Known Limitations
- The programmatic map generator must parse the `warehouse.sdf` properly, accounting for `pose` tags and sub-model includes (like `shelf`, `pickup_station`). If sub-model dimensions aren't hardcoded in the script, they must be read from their respective `model.sdf` files.

### 7. Dependencies on ROS 2 Work
- None for the generation process itself! We can create the map purely based on Gazebo SDFs. However, we cannot actually *launch* `map_server` to serve the map until the ROS 2 workspace is provided.
