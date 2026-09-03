# Developer tools

Standalone helpers. Nothing here is part of the runtime system — the fleet,
Nav2, Gazebo and the dashboard all run without anything in this directory.

| File | Purpose |
|---|---|
| `standalone_amr_radar.html` | Minimal single-robot viewer. Opens directly in a browser and subscribes to `/amr_a/odom` over rosbridge (`ws://localhost:9090`) with no Flask backend. Useful for confirming that rosbridge and odometry are alive when the full dashboard is not running. |

Subsystem-specific verification scripts live next to the subsystem they check,
and are run by `run_tests.sh`:

- `src/synergy_nav2/tools/verify_map_routes.py` — occupancy grid / route checks
- `gazebo/scripts/verify_lidar_obstacles.py` — LiDAR vs world geometry checks
- `dashboard/tools/check_square_view.js` — 20x20 square-viewport check
