# SYNERGY — Decentralized Fleet Coordination Algorithm

## Branch Purpose

This repository contains the **decentralized algorithmic subsystem** for multi-AMR (Autonomous Mobile Robot) coordination in a smart warehouse environment.

**What this subsystem IS:**
- Pure Python decentralized fleet coordination algorithms
- Data models for robot state, intent, reservations, tasks, conflicts, obstacles, health, network degradation, and benchmarks
- Fully unit-tested (323 automated tests) with zero external simulation or middleware dependencies

**What this subsystem is NOT:**
- Not a navigation planner (Nav2 handles geometric trajectory execution and local obstacle avoidance)
- Not a physics simulation (Gazebo handles multi-robot dynamics)
- Not communication middleware (ROS 2 handles message transport)
- Not a central dispatcher (there is no central server or master coordinator)

---

## Key Principle

> **There is no central fleet decision-maker.**
>
> Every AMR runs an identical instance of the coordination logic, maintains its own local `WorldModel`, and makes independent decisions. Coordination emerges from peer-to-peer telemetry exchange and deterministic arbitration rules.

---

## Technical Documentation & Handoff Guides

- **Deep Algorithmic Documentation:** [`fleet_coordination/PROJECT.md`](fleet_coordination/PROJECT.md) — Comprehensive reference of mathematical formulations, models, algorithms, invariants, and architectural decisions.
- **Developer Handoff Guide:** [`fleet_coordination/ALGORITHM_HANDOFF.md`](fleet_coordination/ALGORITHM_HANDOFF.md) — Exact ROS 2 integration contracts, public APIs, data flow, inputs/outputs, and safety rules for integrating with Gazebo/Nav2.

---

## Architecture

```
Fleet Coordination Agent (one per robot)
    │
    ├── WorldModel            — Local private state store (working memory)
    ├── ConflictDetector      — Spatial & temporal conflict detection over shared resources
    ├── PriorityEngine        — Deterministic multi-factor priority arbitration
    ├── ReservationManager    — Mutual-exclusion resource claiming & lifecycle management
    ├── TaskAllocator         — Decentralized auction & eligibility bidding
    ├── FailureDetector       — Heartbeat-based peer health monitoring & task reclaim
    ├── ObstaclePolicy        — Dynamic obstacle detection & corridor blockage classification
    ├── RerouteEvaluator      — Deterministic alternative route evaluation
    ├── NetworkManager        — Communication quality tracking (CONNECTED/DEGRADED/DISCONNECTED/RECOVERY)
    ├── ReconciliationManager — Post-partition state convergence & deterministic conflict resolution
    ├── MetricsLogger         — Observational event historian & counter tracker
    └── BenchmarkEvaluator    — Deterministic comparison against STOP-AND-WAIT baseline
```

---

## Directory Structure

```
fleet_coordination/
    config/                    — Tunable parameters, weights, timeouts (no magic numbers)
    models/                    — Pure Python dataclasses (shared domain vocabulary)
    algorithm/                 — Core algorithms (ZERO ROS / Gazebo / Nav2 imports)
    ros_interface/             — ROS 2 adapter layer (rclpy node, serialization)
    tests/                     — 13 test suites (323 pytest unit & integration tests)
    PROJECT.md                 — In-depth algorithmic technical documentation
    ALGORITHM_HANDOFF.md       — Integration contracts and developer handoff
```

**Strict Architectural Boundary:**
`algorithm/` and `models/` never import `rclpy`, `nav2`, or `gazebo`. `ros_interface/` never contains coordination logic. This hard separation allows all algorithms to be tested in under 1 second without launching ROS 2 or Gazebo.

---

## Domain Models (`fleet_coordination/models/`)

| Model | Purpose |
|---|---|
| `Pose2D` | 2D position $(x, y)$ and heading $(\theta)$ in global frame |
| `RobotState` | Physical and operational telemetry broadcast by an AMR |
| `RobotIntent` | Declared future resource usage, waypoints, and validity deadline |
| `Reservation` | Authoritative mutual-exclusion claim on a shared resource |
| `Task` | Unit of warehouse logistics work |
| `ConflictReport` | Detected spatial/temporal contention between competing robots |
| `PriorityDecision` | Deterministic winner and scoring breakdown from `PriorityEngine` |
| `ReservationDecision` | Lifecycle outcome from `ReservationManager` (accepted, rejected, reason) |
| `TaskBid` | Individual AMR task bid score and eligibility factors |
| `AssignmentDecision` | Winner and bidding breakdown from `TaskAllocator` |
| `PeerHealthAssessment` | Individual peer health classification (`HEALTHY`, `SUSPECT`, `FAILED`) |
| `FleetHealthReport` | Fleet-wide heartbeat health assessment |
| `Obstacle` | Static or dynamic spatial obstruction impacting corridor resources |
| `RerouteDecision` | Alternative path evaluation from `RerouteEvaluator` |
| `LinkMetrics` | Communication link latency, packet loss, and telemetry freshness |
| `NetworkStatusReport` | Local communication mode (`CONNECTED`, `DEGRADED`, `DISCONNECTED`, `RECOVERY`) |
| `ReconciliationReport` | Convergence statistics following network partition healing |
| `TaskMetrics` / `RobotMetrics` / `PerformanceMetrics` | Observational benchmark and telemetry structures |

---

## Subsystem Implementation Status

| Subsystem | Status | Description |
|---|---|---|
| **Data Models & Config** | ✅ Complete | 17 typed dataclasses with zero external dependencies |
| **WorldModel** | ✅ Complete | Local state store with monotonic timestamp filtering |
| **ConflictDetector** | ✅ Complete | Multi-source spatial & temporal overlap detection |
| **PriorityEngine** | ✅ Complete | Multi-factor normalized scoring with $\epsilon$-tie-breaking |
| **ReservationManager** | ✅ Complete | Strict mutual exclusion, non-preemption, idempotent release |
| **TaskAllocator** | ✅ Complete | Decentralized auctioning with battery and deadline constraints |
| **FailureDetector** | ✅ Complete | Heartbeat freshness monitoring and automated task reclamation |
| **ObstaclePolicy** | ✅ Complete | Corridor blockage detection & spatial intersection tests |
| **RerouteEvaluator** | ✅ Complete | Deterministic alternative route evaluation |
| **NetworkManager** | ✅ Complete | Communication health FSM (CONNECTED → DEGRADED → DISCONNECTED → RECOVERY) |
| **ReconciliationManager** | ✅ Complete | Deterministic post-partition state convergence |
| **MetricsLogger & Benchmark** | ✅ Complete | Event historian & evaluation proving $\ge 20\%$ improvement over baseline |

---

## Key Subsystems Overview

### 1. WorldModel (`world_model.py`)
- **Local Private Memory**: Maintains one AMR's working memory (`_own_state`, `_own_intent`, `_peer_states`, `_peer_intents`, `_reservations`, `_tasks`, `_obstacles`).
- **Timestamp Monotonicity**: Incoming updates with timestamps $\le$ stored timestamps are rejected.
- **Query-Time Freshness**: Queries dynamically filter expired records without requiring periodic garbage collection.

### 2. ConflictDetector (`conflict_detector.py`)
- **Discrete Resource Modeling**: Evaluates overlapping reservations and broadcast intents across shared spatial resources (e.g. intersections `I1`, `I2`).
- **Open-Interval Semantics**: $A_{\text{start}} < B_{\text{end}} \land B_{\text{start}} < A_{\text{end}}$.
- **Deterministic Severity Sorting**: Outputs prioritized reports ordered by severity, overlap time, and robot ID.

### 3. PriorityEngine (`priority_engine.py`)
- **Multi-Factor Scoring**: Evaluates task priority, deadline urgency, intent commitment age, and battery status.
- **Symmetric Consensus**: Guaranteeing $\text{resolve}(A, B) \equiv \text{resolve}(B, A)$ across independent robots.
- **$\epsilon$-Tie Breaking**: Floating-point near-equality ($\epsilon = 10^{-9}$) falls back to lexicographic string comparison (`robot_id`).

### 4. ReservationManager (`reservation_manager.py`)
- **Single-View Mutual Exclusion**: Prevents granting overlapping time intervals to multiple robots on exclusive resources.
- **Non-Preemption**: Active, granted reservations are never revoked by competing requests.
- **Atomic Operations & Idempotency**: Safe release and renewal operations.

### 5. TaskAllocator (`task_allocator.py`)
- **Decentralized Bidding**: Robots independently evaluate announced tasks and score bids based on distance, battery, and capability.
- **Consensus Winner Rule**: Lowest robot ID breaks score ties, ensuring identical winner selection fleet-wide.

### 6. FailureDetector (`failure_detector.py`)
- **Heartbeat Freshness**: Classifies peers into `HEALTHY`, `SUSPECT`, or `FAILED` based on telemetry age.
- **Task Reclamation**: Reclaims uncompleted tasks from failed robots and resets status for re-auctioning.

### 7. ObstaclePolicy & RerouteEvaluator (`obstacle_policy.py`, `reroute_evaluator.py`)
- **Corridor Blockage**: Identifies when dynamic or static obstacles block planned paths.
- **Decision-Only Rerouting**: Evaluates alternative routes without mutating tasks or navigation state.

### 8. NetworkManager & ReconciliationManager (`network_manager.py`, `reconciliation_manager.py`)
- **Degradation FSM**: Adapts coordination behavior when packet loss or latency spikes occur.
- **Deterministic Reconciliation**: Merges split-brain states after reconnection using monotonic timestamp rules and reservation tie-breakers.

### 9. MetricsLogger & BenchmarkEvaluator (`metrics_logger.py`, `benchmark_evaluator.py`)
- **Observational Historian**: Tracks task completion times, waiting durations, throughput, and collision counts.
- **Baseline Verification**: Demonstrates $\ge 20\%$ Average Task Completion Time (ATCT) improvement over a sequential STOP-AND-WAIT baseline with a guaranteed 0-collision safety record.

---

## Testing & Verification

All 13 test suites run in **$< 1.0$ second** with zero external dependencies:

```bash
# Run complete test suite (323 tests)
python -m pytest -q

# Run verbose tests on a specific module
python -m pytest fleet_coordination/tests/test_reservation_manager.py -v
python -m pytest fleet_coordination/tests/test_benchmark.py -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2
collected 323 items

fleet_coordination/tests/test_models.py .............................    (29 tests)
fleet_coordination/tests/test_world_model.py ........................... (35 tests)
fleet_coordination/tests/test_conflict_detector.py ..................... (38 tests)
fleet_coordination/tests/test_priority_engine.py ....................... (37 tests)
fleet_coordination/tests/test_reservation_manager.py ................... (45 tests)
fleet_coordination/tests/test_task_allocator.py ........................ (36 tests)
fleet_coordination/tests/test_serialization.py ......................... (20 tests)
fleet_coordination/tests/test_fleet_node.py .........                    (9 tests)
fleet_coordination/tests/test_failure_detector.py ...................   (19 tests)
fleet_coordination/tests/test_obstacle_policy.py .....................  (21 tests)
fleet_coordination/tests/test_network_manager.py ...................... (22 tests)
fleet_coordination/tests/test_metrics.py .......                        (7 tests)
fleet_coordination/tests/test_benchmark.py .....                        (5 tests)

============================= 323 passed in 0.62s =============================
```

---

## Integration Boundaries

### ROS 2 Interface Boundary
- Located strictly in `fleet_coordination/ros_interface/`.
- `fleet_node.py` provides `FleetCoordinationCore` and `FleetCoordinationNode` (rclpy wrapper).
- `serialization.py` handles deterministic JSON $\leftrightarrow$ Dataclass encoding/decoding.

### Nav2 & Gazebo Boundaries
- **Nav2** manages continuous trajectory generation, local collision avoidance, and motor control.
- **Fleet Coordination** arbitrates discrete resource access, task assignment, and yield decisions.
- **Gazebo** simulates physics, sensors (LiDAR/Odometry), and robot hardware.