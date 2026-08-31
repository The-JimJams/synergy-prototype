# Fleet Coordination Algorithm — Kartik's Branch

## Branch Purpose

This branch implements the **algorithmic subsystem** for decentralized
multi-robot coordination in a smart warehouse prototype.

**What this branch IS:**
- The fleet coordination decision-making algorithms
- Data models for robot state, intent, reservations, tasks, and conflicts
- Pure Python logic that can be unit-tested without ROS 2 or Gazebo

**What this branch is NOT:**
- Not a navigation system (Nav2 handles that)
- Not a simulation environment (Gazebo handles that)
- Not a communication middleware (ROS 2 handles that)
- Not a dashboard or UI
- Not a central fleet controller

## Key Principle

> **There is no central fleet decision-maker.**
>
> Every robot runs the same coordination logic, maintains its own local
> World Model, and makes independent decisions. Coordination emerges
> from peer-to-peer communication and deterministic algorithms.

## Architecture

```
Fleet Coordination Agent (one per robot)
    │
    ├── WorldModel            — Local state store
    ├── PeerStateManager      — Peer state tracking + freshness
    ├── IntentManager         — Peer intent tracking + freshness
    ├── ConflictDetector      — Spatial + temporal conflict detection
    ├── PriorityEngine        — Deterministic priority scoring
    ├── ReservationManager    — Resource claiming + expiry
    ├── TaskAllocator         — Distributed bidding
    ├── DeadlockDetector      — Dependency graph cycle detection
    ├── FailureDetector       — Heartbeat-based health monitoring
    ├── ObstaclePolicy        — Dynamic obstacle rerouting policy
    ├── NetworkMonitor        — Communication quality tracking
    ├── ModeManager           — CONNECTED/DEGRADED/DISCONNECTED/RECOVERY
    ├── ReconciliationManager — Post-reconnection state merge
    └── DecisionLogger        — Explainable coordination audit log
```

## Directory Structure

```
fleet_coordination/
    config/                    — Tunable parameters (no magic numbers)
    models/                    — Pure dataclasses (shared vocabulary)
    algorithm/                 — Core algorithms (ZERO ROS imports)
    ros_interface/             — ROS 2 adapter layer (ONLY ROS imports here)
    tests/                     — pytest unit tests (no ROS dependency)
```

**Hard boundary:** `algorithm/` never imports `rclpy`. `ros_interface/`
never contains algorithm logic. This separation is what makes the
algorithms testable without launching Gazebo.

## Data Models

| Model | Purpose |
|---|---|
| `Pose2D` | 2D position + orientation (abstract frame) |
| `RobotState` | What a robot IS (broadcast to peers) |
| `RobotIntent` | What a robot PLANS TO DO (broadcast for conflict detection) |
| `Reservation` | Temporary claim on a shared resource |
| `Task` | Unit of work to be assigned |
| `ConflictReport` | Output of conflict detection |

## Algorithms (Implementation Status)

| Algorithm | Status |
|---|---|
| Data models + config | ✅ Complete |
| WorldModel | ✅ Complete |
| ConflictDetector | ✅ Complete |
| PriorityEngine | ✅ Complete |
| ReservationManager | 🔲 Not started |
| TaskAllocator | 🔲 Not started |
| DeadlockDetector | 🔲 Not started |
| FailureDetector | 🔲 Not started |
| NetworkMonitor | 🔲 Not started |
| ReconciliationManager | 🔲 Not started |
| DecisionLogger | 🔲 Not started |

## WorldModel Subsystem

The `WorldModel` (`fleet_coordination/algorithm/world_model.py`) is the **local, private state store** for a single robot's Fleet Coordination Agent.

### Core Architectural Characteristics:
- **Local State Store**: Maintains one AMR's working memory (`_own_state`, `_own_intent`, `_peer_states`, `_peer_intents`, `_reservations`, `_tasks`). There is NO centralized server or shared database.
- **Own vs. Peer Isolation**: Local robot state and intent are stored separately and are never mixed with peer broadcast tables.
- **Timestamp Monotonicity**: Incoming peer updates with timestamps $\le$ stored timestamps are rejected to preserve monotonic state ordering and deterministic behavior.
- **Freshness Evaluation**: Peer states are evaluated against `config.timeouts.peer_state_max_age_seconds` using an explicitly supplied `now` parameter.
- **Query-Time Expiry**: Active queries (`get_active_peer_intents(now)`, `get_active_reservations(now)`) dynamically filter out expired records at query time.
- **Cleanup / Garbage Collection**: `cleanup_expired(now)` is strictly an optional memory management utility. Query correctness never depends on cleanup having been executed.
- **ROS Boundary**: Pure Python with zero ROS/rclpy dependencies. Operates strictly on domain dataclasses.
- **Non-Responsibilities**: WorldModel contains NO decision logic — it does not calculate priorities, allocate tasks, resolve conflicts, grant reservations, or detect deadlocks.

## ConflictDetector Subsystem

The `ConflictDetector` (`fleet_coordination/algorithm/conflict_detector.py`) is the pure algorithmic engine responsible for identifying spatial and temporal contention over shared warehouse resources.

### Core Architectural Characteristics:
- **Coordination Criterion**: A `ConflictReport` is generated when the configured coordination detection criteria are satisfied. This is a discrete resource coordination tool and does NOT provide certified physical collision avoidance.
- **Read-Only Operation**: Reads intent and reservation state from `WorldModel`; performs zero state mutations.
- **Option C Occupancy Modeling**: Derives resource occupancy as $[T_{\text{start}}, T_{\text{end}}]$ where $T_{\text{start}} = \max(\text{now}, \text{eta})$ and $T_{\text{end}} = \min(T_{\text{start}} + \Delta t_{\text{default}}, \text{valid\_until})$.
- **Open-Interval Temporal Semantics**: Overlap requires $A_{\text{start}} < B_{\text{end}} \land B_{\text{start}} < A_{\text{end}}$. Boundary-touching intervals ($A_{\text{end}} == B_{\text{start}}$) are strictly non-conflicting.
- **Evidence Aggregation**: Multi-source evidence (intent vs. intent and intent vs. reservation) is grouped per `(peer_id, resource_id)` to form a bounding conflict window $[ \min(\text{start}), \max(\text{end}) ]$ with earliest onset determining severity.
- **Severity & Determinism**: Classifies urgency (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) and outputs reports deterministically sorted by `(severity_rank, overlap_start, robot_b_id)`.
- **Zero Resolution**: Detects conflicts only. Does not calculate priorities, choose winners, or grant/deny claims.

## PriorityEngine Subsystem

The `PriorityEngine` (`fleet_coordination/algorithm/priority_engine.py`) is the pure algorithmic arbitration engine that resolves pairwise coordination conflicts over contested resources.

### Core Architectural Characteristics:
- **Deterministic Arbitration**: Given identical fleet telemetry and reference time `now`, every robot independently calculating priority reaches the exact same winner.
- **Read-Only Immutability**: Queries `WorldModel` state without mutating records; creates no reservations or task allocations.
- **Normalized Multi-Factor Scoring**: Evaluates task priority ($(p-1)/9.0$), deadline urgency ($1/\max(\Delta t, 1.0)$), intent commitment age proxy ($\min(\text{age}/\text{max\_wait}, 1.0)$), and battery urgency ($(100-\text{battery})/100.0$).
- **Epsilon Tie-Breaking**: Compares composite scores with a tolerance threshold (`score_epsilon = 1e-9`) before applying the deterministic lexicographic `robot_id` tie-breaker.
- **Decentralized Agreement & Symmetry**: Invariant to conflict report perspective ($\text{resolve}(A, B) \equiv \text{resolve}(B, A)$) guaranteeing fleet-wide coordination consensus without a central server.
- **Explainable Decisions**: Produces a `PriorityDecision` detailing normalized factor breakdowns, composite scores, winner/loser IDs, and tie-break flags for auditability.

## Assumptions

1. **Coordinate frame:** Poses are in a consistent global reference frame.
   The specific frame (e.g., ROS `map`) is handled by the ROS adapter layer.
2. **Timestamps:** `time.time()` (UTC wall clock). NTP sync across robots
   is assumed (trivially met in Gazebo — all robots on one machine).
3. **2D warehouse floor:** Robots operate on a flat plane. Pose2D is sufficient.
4. **Named resources:** ConflictDetector v1 uses named shared resources
   (e.g., "I1", "I2") rather than continuous trajectory geometry.
5. **Determinism:** All decisions are deterministic. Tie-breaker: lower
   robot ID wins. No randomness, no message-order dependence.

## Testing

```bash
# Run all tests
python -m pytest fleet_coordination/tests/ -v

# Run specific test file
python -m pytest fleet_coordination/tests/test_models.py -v

# Run with coverage (requires pytest-cov)
python -m pytest fleet_coordination/tests/ --cov=fleet_coordination --cov-report=term-missing
```

Tests are deterministic — all timestamps are fixed, no `time.time()` calls
in tests. Tests pass without ROS 2, Gazebo, or any external dependencies.

## ROS 2 Integration Boundary

The `ros_interface/` package is the boundary:
1. ROS subscribers receive messages → convert to internal dataclasses
2. Algorithm modules process the dataclasses → produce results
3. ROS publishers convert results → publish ROS messages

The algorithm layer never knows it's running inside ROS.

## Nav2 Integration Boundary

This branch does NOT replace Nav2. The relationship is:
- **Nav2** handles: path planning, local obstacle avoidance, motor control
- **Fleet Agent** handles: which robot goes where, who waits, who has priority

When a reroute is needed, the Fleet Agent *requests* Nav2 to replan.
It does not compute the path itself.

## Safety Boundary

> **This is a research prototype in simulation.**
>
> The coordination algorithm is NOT a certified safety system.
> Local obstacle avoidance and emergency-stop behavior remain independent
> of peer coordination. A stale peer message must never disable local safety.

## Known Limitations

- Prototype scope — not production-hardened
- No ML-based optimization (by design for this phase)
- ConflictDetector v1 uses named resources, not continuous trajectory analysis
- Network simulation is simplified (no realistic packet loss model)

## Future Improvements

- Trajectory-based conflict detection using planned waypoints
- Adaptive priority weights based on fleet performance metrics
- Multi-resource reservation chains (e.g., reserve I1 → I3 → DOCK_2)
- Formal verification of deadlock-freedom properties