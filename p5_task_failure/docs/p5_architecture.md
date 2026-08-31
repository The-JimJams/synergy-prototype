# P5 Architecture — Distributed Task Allocation & Failure Recovery

## Overview

The P5 subsystem is responsible for:

1. **Distributed task allocation** — robots bid for tasks and the best
   bid wins using a deterministic auction.
2. **Robot failure detection** — missed heartbeats reveal a failed robot.
3. **Task recovery** — failed-robot tasks are released and re-auctioned.
4. **Resilience features** — blocked-aisle recovery (Phase 15+).

P5 is designed to be **completely independent** of every other team's
code.  It develops, tests, and demonstrates on its own.
External systems connect through the adapter layer — without modifying
any P5 core code.

---

## Architecture Diagram

```
                        P5 CORE
                           |
           +---------------+---------------+
           |               |               |
       Task Model      Robot Model      Events
           |               |               |
           +---------------+---------------+
                           |
                      P5 Managers
                           |
           +---------------+---------------+
           |               |               |
       Allocation       Failure        Recovery
       (Phase 4-5)    (Phase 10)     (Phase 11-14)
                           |
                    Adapter Layer
                           |
          +----------------+----------------+
          |                |                |
     ROS 2 Adapter   Simulator Adapter   Future
     (Phase 7-8)     (standalone)        Systems
```

---

## Layer Descriptions

### Core Models (`p5/models/`)

Plain Python dataclasses.  No external dependency.

| File | Contents |
|---|---|
| `robot.py` | `Robot`, `RobotStatus` |
| `task.py` | `Task`, `TaskStatus`, `TASK_TRANSITIONS` |
| `bid.py` | `Bid` |
| `heartbeat.py` | `Heartbeat`, `HeartbeatStatus` |
| `events.py` | `P5Event`, `P5EventType` |

### Adapter Layer (`p5/adapters/`)

`typing.Protocol` interfaces — no implementations, no external imports.

| Interface | Responsibility |
|---|---|
| `TaskSource` | Provides tasks to allocation |
| `RobotStateProvider` | Provides robot state snapshots |
| `BidCalculator` | Computes bid score for a (robot, task) pair |
| `WinnerSelector` | Deterministically selects the winning bid |
| `HeartbeatSource` | Provides heartbeat data |
| `FailureDetector` | Classifies robots as ALIVE/SUSPECTED/FAILED |
| `TaskRecoveryManager` | Releases and re-announces failed tasks |
| `EventSink` | Forwards P5 events to external observers |
| `NavigationAdapter` | Sends navigation goals to robot nav stack |

### Allocation (`p5/allocation/`) — Phase 3–5

| File | Phase |
|---|---|
| `capability.py` | Phase 3 — eligibility checking |
| `bidder.py` | Phase 4 — bid score calculation |
| `winner.py` | Phase 5 — deterministic winner selection |

### Failure (`p5/failure/`) — Phase 9–10

| File | Phase |
|---|---|
| `heartbeat.py` | Phase 9 — heartbeat registry |
| `detector.py` | Phase 10 — timeout-based failure detection |

### Recovery (`p5/recovery/`) — Phase 11–14

| File | Phase |
|---|---|
| `task_recovery.py` | Phase 11-14 — release, re-announce, reassign |

### Manager (`p5/manager/`) — Phase 6

| File | Phase |
|---|---|
| `task_manager.py` | Phase 6 — coordination loop |

---

## Decentralisation

> **No central decision server exists.**

Each robot runs a local `FleetAgent` (to be implemented in Phase 6).
The FleetAgent:
- Observes task announcements.
- Independently calculates its bid using local state.
- Submits its bid.
- Accepts or rejects the allocation result.

In **standalone simulation**, multiple FleetAgents run inside a single
Python process.  This does NOT make the architecture centralised —
each simulated agent uses only its own state to make decisions.

In **ROS 2 deployment**, each FleetAgent runs as a separate node on its
robot.

---

## Decentralised Auction Flow

```
Task appears (AVAILABLE)
        |
        v
Task Announced (broadcast)
        |
        +----------+----------+
        |          |          |
     Robot A    Robot B    Robot C
        |          |          |
  Local bid   Local bid   Local bid
  calculated  calculated  calculated
        |          |          |
        +----------+----------+
                   |
        Deterministic winner
        (highest score, tie-break by robot_id)
                   |
                   v
            Task Assigned
```

---

## Failure Recovery Flow

```
Robot owns a task
        |
        v
Heartbeat timeout exceeded
        |
        v
FailureDetector: FAILED
        |
        v
TaskRecoveryManager.release_task()
        |
        v
Task -> RECOVERY state, assigned_robot cleared
        |
        v
TaskRecoveryManager.re_announce_task()
        |
        v
Task -> ANNOUNCED (remaining robots bid again)
        |
        v
New winner selected
        |
        v
Task reassigned
```

---

## Independence Contract

| Dependency | Core | Adapter |
|---|---|---|
| ROS 2 | ❌ NONE | ✅ Future Phase 7 |
| Gazebo | ❌ NONE | ❌ Not needed |
| Nav2 | ❌ NONE | ✅ Future Phase 8 |
| UI / Dashboard | ❌ NONE | ❌ Not needed |
| Other team code | ❌ NONE | ✅ Via adapter only |
| Python stdlib | ✅ YES | ✅ YES |

---

## Deferred Work

| Phase | Description |
|---|---|
| Phase 2 | Task data model validation |
| Phase 3 | Capability checking |
| Phase 4 | Bid calculation algorithm |
| Phase 5 | Deterministic winner selection |
| Phase 6 | Task state machine enforcement |
| Phase 7 | ROS 2 adapter integration |
| Phase 8 | Nav2 adapter integration |
| Phase 9 | Heartbeat monitoring |
| Phase 10 | Failure detection (timeout-based) |
| Phase 11 | Task release |
| Phase 12 | Task re-announcement |
| Phase 13 | Task reassignment |
| Phase 14 | Full failure recovery |
| Phase 15 | Blocked-aisle resilience |
| Phase 16 | Optional: communication degradation |

---

## Running Standalone

```bash
# From p5_task_failure/
python simulation/standalone_demo.py

# Run tests
python -m pytest tests/ -v
```

No ROS 2.  No Gazebo.  No Nav2.  No network.  No UI.
