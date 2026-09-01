# ALGORITHM_HANDOFF — Fleet Coordination Algorithmic Layer

> **Status:** Phase 7 Algorithmic Implementation COMPLETE  
> **Test Baseline:** 323 tests, 100% passing, < 1 second runtime  
> **Last Verified:** 2026-09-01

---

## 1. Architecture Overview

The `fleet_coordination/` package implements a **fully decentralized** multi-AMR coordination engine. There is **no central dispatcher, no master node, and no shared database**. Every robot runs an identical instance of the algorithmic stack against its own local `WorldModel`.

```
┌─────────────────────────────────────────────────────────┐
│                    PER-ROBOT STACK                       │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              ROS 2 / Gazebo Layer                 │  │
│  │  fleet_node.py  ←→  serialization.py              │  │
│  │  (subscribers, publishers, timers, odometry)      │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │ Pure Python boundary           │
│  ┌──────────────────────▼────────────────────────────┐  │
│  │              Algorithm Layer (algorithm/)          │  │
│  │                                                   │  │
│  │  WorldModel         ← local state store           │  │
│  │  ConflictDetector   ← spatial/temporal overlap    │  │
│  │  PriorityEngine     ← deterministic arbitration   │  │
│  │  ReservationManager ← mutual exclusion claims     │  │
│  │  TaskAllocator      ← decentralized auctions      │  │
│  │  FailureDetector    ← heartbeat monitoring        │  │
│  │  ObstaclePolicy     ← blockage detection          │  │
│  │  RerouteEvaluator   ← alternative route decision  │  │
│  │  NetworkManager     ← communication mode FSM      │  │
│  │  ReconciliationMgr  ← post-partition convergence  │  │
│  │  MetricsLogger      ← event history/counters      │  │
│  │  BenchmarkEvaluator ← baseline comparison         │  │
│  │                                                   │  │
│  │  ZERO rclpy / Gazebo / Nav2 imports               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Domain Models (models/)               │  │
│  │  Pose2D, RobotState, RobotIntent, Reservation,    │  │
│  │  Task, ConflictReport, PriorityDecision,           │  │
│  │  ReservationDecision, TaskBid, AssignmentDecision,  │  │
│  │  Obstacle, RerouteDecision, Health models,          │  │
│  │  Network models, ReconciliationReport,              │  │
│  │  TaskMetrics, RobotMetrics, PerformanceMetrics      │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Configuration (config/)               │  │
│  │  CoordinationConfig, PriorityWeights,              │  │
│  │  TaskBidWeights, ConflictDetectionConfig,          │  │
│  │  NetworkThresholds, ObstacleConfig                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Subsystem Responsibilities (Single-Responsibility Map)

| Subsystem | Sole Responsibility | Reads From | Writes To |
|:---|:---|:---|:---|
| **WorldModel** | Local state storage & query | Nothing (root store) | Own internal dicts |
| **ConflictDetector** | Detect spatial/temporal resource overlap | WorldModel (read-only) | Returns `list[ConflictReport]` |
| **PriorityEngine** | Deterministic priority arbitration | WorldModel (read-only) | Returns `PriorityDecision` |
| **ReservationManager** | Mutual-exclusion resource claims | WorldModel (read + write reservations) | Returns `ReservationDecision` |
| **TaskAllocator** | Decentralized task auction/assignment | WorldModel (read + write task status) | Returns `AssignmentDecision` |
| **FailureDetector** | Heartbeat monitoring & task reclaim | WorldModel (read; write task.status on reclaim) | Returns `FleetHealthReport` |
| **ObstaclePolicy** | Classify obstacles as blocking | WorldModel (read-only) | Returns `list[Obstacle]` matched |
| **RerouteEvaluator** | Evaluate alternative route options | WorldModel (read-only) | Returns `RerouteDecision` |
| **NetworkManager** | Communication mode FSM | LinkMetrics input | Returns `NetworkStatusReport` |
| **ReconciliationManager** | Post-partition state convergence | WorldModel (read + write) | Returns `ReconciliationReport` |
| **MetricsLogger** | Record fleet events, compute metrics | Event method calls only | Returns `PerformanceMetrics` |
| **BenchmarkEvaluator** | Compare decentralized vs. baseline | MetricsLogger | Returns comparison dict / bool |

**No subsystem duplicates another's responsibility.**

---

## 3. Public APIs

### WorldModel
```python
WorldModel(robot_id: str, config: CoordinationConfig | None = None)
.set_own_state(state: RobotState) -> None
.get_own_state() -> RobotState | None
.update_peer_state(state: RobotState) -> bool
.get_peer_state(robot_id: str, now: float) -> RobotState | None
.get_all_peer_states(now: float) -> dict[str, RobotState]
.update_peer_intent(intent: RobotIntent) -> bool
.get_peer_intent(robot_id: str, now: float) -> RobotIntent | None
.add_reservation(reservation: Reservation) -> bool
.get_active_reservations(resource_id: str, now: float) -> list[Reservation]
.remove_reservation(claim_id: str) -> bool
.add_task(task: Task) -> None
.get_task(task_id: str) -> Task | None
.update_obstacle(obstacle: Obstacle) -> None
.get_active_obstacles(now: float) -> list[Obstacle]
```

### ConflictDetector
```python
ConflictDetector(config: ConflictDetectionConfig | None = None)
.detect_conflicts(world_model: WorldModel, robot_id: str, now: float) -> list[ConflictReport]
```

### PriorityEngine
```python
PriorityEngine(config: CoordinationConfig | None = None)
.resolve(conflict: ConflictReport, world_model: WorldModel, now: float) -> PriorityDecision
```

### ReservationManager
```python
ReservationManager(config: CoordinationConfig | None = None)
.request_reservation(world_model: WorldModel, ..., now: float) -> ReservationDecision
.release_reservation(world_model: WorldModel, claim_id: str, ...) -> ReservationDecision
.renew_reservation(world_model: WorldModel, claim_id: str, ...) -> ReservationDecision
```

### TaskAllocator
```python
TaskAllocator(config: CoordinationConfig | None = None)
.evaluate_task(task: Task, world_model: WorldModel, now: float) -> AssignmentDecision
```

### FailureDetector
```python
FailureDetector(config: CoordinationConfig | None = None)
.evaluate_peer(world_model: WorldModel, peer_id: str, now: float) -> PeerHealthAssessment
.evaluate_fleet(world_model: WorldModel, now: float) -> FleetHealthReport
.reclaim_failed_robot_tasks(world_model: WorldModel, failed_robot_id: str) -> list[str]
```

### ObstaclePolicy
```python
ObstaclePolicy(config: CoordinationConfig | None = None)
.evaluate_obstacles(world_model: WorldModel, robot_id: str, now: float) -> list[Obstacle]
```

### RerouteEvaluator
```python
RerouteEvaluator(config: CoordinationConfig | None = None)
.evaluate_reroute(world_model: WorldModel, robot_id: str, ..., now: float) -> RerouteDecision
```

### NetworkManager
```python
NetworkManager(config: CoordinationConfig | None = None)
.evaluate_network(link_metrics: list[LinkMetrics], now: float) -> NetworkStatusReport
```

### ReconciliationManager
```python
ReconciliationManager(config: CoordinationConfig | None = None)
.reconcile(local_wm: WorldModel, remote_wm: WorldModel, now: float) -> ReconciliationReport
```

### MetricsLogger
```python
MetricsLogger(start_time: float)
.log_task_status(task_id: str, status: TaskStatus, now: float) -> None
.log_robot_status(robot_id: str, status: RobotStatus, now: float) -> None
.log_collision(robot_a_id: str, robot_b_id: str, now: float) -> None
.log_reroute_success(robot_id: str, now: float) -> None
.log_network_recovery(now: float) -> None
.compute_metrics(now: float) -> PerformanceMetrics
```

### BenchmarkEvaluator
```python
BenchmarkEvaluator(start_time: float = 1000.0, dt: float = 0.1)
.evaluate_scenario(scenario_func, use_decentralized: bool) -> PerformanceMetrics
.compare(baseline: PerformanceMetrics, decentralized: PerformanceMetrics) -> dict[str, float]
.evaluate_improvement(baseline: PerformanceMetrics, decentralized: PerformanceMetrics) -> bool
```

---

## 4. Data Flow

```
Odometry (Gazebo/ROS 2)
    │
    ▼
FleetCoordinationCore.process_odometry()
    │
    ├──▶ WorldModel.set_own_state(RobotState)
    │
    ├──▶ serialization.to_json(RobotState)
    │        │
    │        ▼
    │    /fleet/robot_state  (ROS 2 String topic — broadcast)
    │
    ▼
Peer broadcast received
    │
    ▼
FleetCoordinationCore.handle_peer_state_json()
    │
    ▼
WorldModel.update_peer_state(RobotState)  [monotonic timestamp guard]
    │
    ▼
ConflictDetector.detect_conflicts(world_model, robot_id, now)
    │
    ├──▶ If conflicts found:
    │        PriorityEngine.resolve(conflict, world_model, now)
    │            │
    │            ├──▶ If winner: ReservationManager.request_reservation(...)
    │            └──▶ If loser:  WAIT (v = 0.0 at stop line)
    │
    ├──▶ FailureDetector.evaluate_fleet(world_model, now)
    │        │
    │        └──▶ If FAILED peer: reclaim_failed_robot_tasks(...)
    │                                └──▶ TaskAllocator.evaluate_task(...)
    │
    ├──▶ ObstaclePolicy.evaluate_obstacles(world_model, robot_id, now)
    │        │
    │        └──▶ If blocked: RerouteEvaluator.evaluate_reroute(...)
    │
    ├──▶ NetworkManager.evaluate_network(link_metrics, now)
    │        │
    │        └──▶ If RECOVERY: ReconciliationManager.reconcile(...)
    │
    └──▶ MetricsLogger.log_*(...)  [observational only]
```

---

## 5. ROS 2 Integration Points

### What the ROS Layer MUST Provide to the Algorithm Layer

| # | ROS 2 Input | Algorithm Target | Data Mapping |
|:--|:---|:---|:---|
| 1 | `nav_msgs/Odometry` from `/{robot_id}/odom` | `WorldModel.set_own_state()` | `odometry_to_robot_state(pos_x, pos_y, yaw, linear_vel, angular_vel, timestamp)` |
| 2 | `std_msgs/String` from `/fleet/robot_state` | `WorldModel.update_peer_state()` | `from_json(json_str, RobotState)` |
| 3 | `std_msgs/String` from `/fleet/robot_intent` | `WorldModel.update_peer_intent()` | `from_json(json_str, RobotIntent)` — **NOT YET WIRED** |
| 4 | `std_msgs/String` from `/fleet/task` | `WorldModel.add_task()` | `from_json(json_str, Task)` — **NOT YET WIRED** |
| 5 | `std_msgs/String` from `/fleet/obstacles` | `WorldModel.update_obstacle()` | `from_json(json_str, Obstacle)` — **NOT YET WIRED** |
| 6 | Network telemetry (latency/loss metrics) | `NetworkManager.evaluate_network()` | Construct `LinkMetrics` per peer — **NOT YET WIRED** |
| 7 | Task status events | `MetricsLogger.log_task_status()` | Call when task transitions — **NOT YET WIRED** |
| 8 | Robot status events | `MetricsLogger.log_robot_status()` | Call on `RobotStatus` transitions — **NOT YET WIRED** |

### What the Algorithm Layer Produces (ROS Layer Must Consume)

| # | Algorithm Output | ROS 2 Action |
|:--|:---|:---|
| 1 | `PriorityDecision.winner_id == self` | PROCEED (publish `cmd_vel` at cruise speed) |
| 2 | `PriorityDecision.winner_id != self` | WAIT (publish `cmd_vel = 0.0` at stop line) |
| 3 | `ReservationDecision.accepted == True` | Claim granted — safe to enter resource zone |
| 4 | `ReservationDecision.accepted == False` | Claim denied — remain stopped or re-plan |
| 5 | `AssignmentDecision.is_winner(robot_id)` | Begin task execution (navigate to source) |
| 6 | `RerouteDecision.should_reroute == True` | Request Nav2 replanning to `alternative_route` |
| 7 | `FleetHealthReport` with FAILED peers | Trigger `reclaim_failed_robot_tasks()` |
| 8 | `NetworkStatusReport.mode == RECOVERY` | Trigger `ReconciliationManager.reconcile()` |
| 9 | `PerformanceMetrics` | Publish to `/fleet/metrics` for dashboards |

### How Reservations Are Communicated
Reservations are stored locally in each robot's `WorldModel`. For decentralized agreement, the ROS layer must broadcast `Reservation` objects (via `serialization.to_json()`) on a shared topic (e.g. `/fleet/reservations`) so peers can call `WorldModel.add_reservation()`. **This broadcast topic is NOT YET WIRED.**

### How Tasks Are Communicated
Tasks are announced on a shared topic (e.g. `/fleet/task`). Each robot receives the task, runs `TaskAllocator.evaluate_task()`, and deterministically computes the same winner. **This broadcast topic is NOT YET WIRED.**

### How Obstacle Reports Enter the Algorithm
LiDAR/depth data from Gazebo produces obstacle detections. The ROS layer must construct `Obstacle(obstacle_id, affected_resource_id, ...)` and call `WorldModel.update_obstacle()`. **This sensor pipeline is NOT YET WIRED.**

### How Network Metrics Enter NetworkManager
The ROS layer measures round-trip latency and packet loss to each peer (e.g. via heartbeat echo). It constructs `LinkMetrics(peer_id, latency_ms, packet_loss_ratio, last_seen_age)` and passes them to `NetworkManager.evaluate_network()`. **This measurement pipeline is NOT YET WIRED.**

---

## 6. Safety Rules (Invariants)

1. **Determinism:** Given identical `WorldModel` state and explicit `now`, all algorithms produce identical output on every robot.
2. **Lexicographic Tie-Breaking:** Scores within ε = 10⁻⁹ are resolved by `robot_id` string comparison (`"amr_a" < "amr_b"`).
3. **Monotonic Timestamps:** `WorldModel` rejects updates with `timestamp <= stored_timestamp`.
4. **Reservation Mutual Exclusion (INV-1):** No two robots hold overlapping reservations on the same resource within a single WorldModel view.
5. **Non-Preemption (INV-8):** Active granted reservations are never revoked.
6. **Idempotency (INV-4):** Re-releasing an already-released claim returns `accepted=True, reason="ALREADY_RELEASED"`.
7. **Failed Robot Exclusion:** Robots with `RobotStatus.FAILED` are excluded from task bidding and priority evaluation.
8. **Network ≠ Robot Failure:** `NetworkManager` determines communication mode; `FailureDetector` determines peer health. They are independent.
9. **Rerouting ≠ Reassignment:** `RerouteEvaluator` returns a route decision. It does NOT reassign tasks, modify reservations, or mutate intents.
10. **Metrics Are Observational:** `MetricsLogger` and `BenchmarkEvaluator` never modify `WorldModel`, tasks, reservations, or any coordination decision.

---

## 7. Test Command

```bash
# Full regression (expected: 323 passed in < 1 second)
python -m pytest -q

# Verbose single suite
python -m pytest fleet_coordination/tests/test_reservation_manager.py -v

# All 13 test suites
python -m pytest fleet_coordination/tests/ -v
```

**Current Test Count: 323 (0 failures, 0 errors)**

---

## 8. Known Limitations

1. **No physical collision avoidance.** `ConflictDetector` detects resource scheduling conflicts, not real-time obstacle proximity. Physical safety requires Nav2's local costmap and recovery behaviors.
2. **No path planning.** The algorithm layer does not compute navigation paths. Route alternatives in `RerouteEvaluator` are named resource sequences, not geometric trajectories.
3. **No real networking.** `NetworkManager` evaluates provided `LinkMetrics` but does not measure network quality itself.
4. **Single-view consistency only.** Each robot's `WorldModel` is eventually consistent with peers, not strongly consistent. Temporary divergence is expected and handled by `ReconciliationManager`.

---

## 9. Items Intentionally NOT Implemented (Integration Layer Scope)

| Item | Reason |
|:---|:---|
| ROS 2 topic wiring for intents, tasks, obstacles, reservations | Belongs to `ros_interface/` integration phase |
| Nav2 path planning / replanning | Belongs to navigation stack |
| Gazebo sensor processing (LiDAR → Obstacle) | Belongs to perception pipeline |
| `cmd_vel` velocity publishing | Belongs to `motion_controller.py` (PLANNED) |
| Network quality measurement | Belongs to ROS 2 heartbeat/echo service |
| Gazebo bridge launch configuration | Belongs to launch file infrastructure |
| Dashboard / Rviz visualization | Belongs to visualization layer |
| Multi-floor / elevator coordination | Out of Phase 7 scope |

---

## 10. File Manifest

### Algorithm Layer (`algorithm/`)
| File | Lines | Purpose |
|:---|:---|:---|
| `world_model.py` | 455 | Local state store |
| `conflict_detector.py` | 226 | Resource conflict detection |
| `priority_engine.py` | 208 | Deterministic priority arbitration |
| `reservation_manager.py` | 518 | Mutual exclusion resource claims |
| `task_allocator.py` | 355 | Decentralized task auctions |
| `failure_detector.py` | 208 | Heartbeat monitoring |
| `obstacle_policy.py` | 143 | Obstacle classification |
| `reroute_evaluator.py` | 170 | Alternative route evaluation |
| `network_manager.py` | 204 | Communication mode FSM |
| `reconciliation_manager.py` | 310 | Post-partition convergence |
| `metrics_logger.py` | 120 | Event recording & metric computation |
| `benchmark_evaluator.py` | 118 | Baseline comparison framework |

### Domain Models (`models/`)
17 dataclass files defining the complete type system.

### Tests (`tests/`)
13 test suites, 323 total tests, < 1 second runtime.

### ROS Interface (`ros_interface/`)
| File | Purpose |
|:---|:---|
| `fleet_node.py` | `FleetCoordinationCore` (testable) + `FleetCoordinationNode` (rclpy) |
| `serialization.py` | JSON ↔ dataclass conversion with schema validation |
