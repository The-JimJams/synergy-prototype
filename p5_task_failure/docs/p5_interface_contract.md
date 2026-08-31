# P5 Interface Contract

## Purpose

This document defines what P5 exposes to (and expects from) external
systems.  It is divided into two sections:

**A. Internal P5 Contract** — the plain-Python objects that form
the P5 core API.  These are stable and can be used immediately.

**B. Future External Adapter Contract** — the concepts that will be
mapped to/from external systems (ROS 2, Nav2, Dashboard) in later
phases.  These are planned but not yet implemented.

---

## A. Internal P5 Contract

These objects exist today and are importable from `p5.models`.

### Robot

```python
from p5.models import Robot, RobotStatus

Robot(
    robot_id: str,
    position: Tuple[float, float],
    battery: float,            # 0.0 – 100.0 percent
    payload_capacity: float,   # warehouse units
    current_task: Optional[str],
    workload: int,
    status: RobotStatus,
    capabilities: Tuple[str, ...],
)
```

**Status:** `INTERNAL — READY`

---

### Task

```python
from p5.models import Task, TaskStatus

Task(
    task_id: str,
    pickup_location: Tuple[float, float],
    dropoff_location: Tuple[float, float],
    priority: int,             # 1 – 10
    deadline: float,           # seconds
    required_payload: float,
    status: TaskStatus,
    assigned_robot: Optional[str],
    required_capabilities: Tuple[str, ...],
)
```

**TaskStatus values:**
`AVAILABLE | ANNOUNCED | BIDDING | ASSIGNED | IN_PROGRESS | COMPLETED | FAILED | RECOVERY | CANCELLED`

**Status:** `INTERNAL — READY`

---

### Bid

```python
from p5.models import Bid

Bid(
    task_id: str,
    robot_id: str,
    score: float,          # Phase 4: not yet computed
    estimated_time: float, # Phase 4: not yet computed
    distance: float,
    battery_cost: float,   # Phase 4: not yet computed
    valid: bool,
    timestamp: datetime,
)
```

**Status:** `INTERNAL — READY (scoring deferred to Phase 4)`

---

### Heartbeat

```python
from p5.models import Heartbeat, HeartbeatStatus

Heartbeat(
    robot_id: str,
    timestamp: datetime,   # UTC, timezone-aware
    status: HeartbeatStatus,
)
```

**HeartbeatStatus values:**
`ALIVE | SUSPECTED | FAILED | RECOVERED`

**Status:** `INTERNAL — READY (monitoring deferred to Phase 9)`

---

### P5Event

```python
from p5.models import P5Event, P5EventType

P5Event(
    event_type: P5EventType,
    timestamp: datetime,
    source_robot: Optional[str],
    task_id: Optional[str],
    payload: Optional[Any],
)
```

**P5EventType values:**
`TASK_ANNOUNCED | BID_SUBMITTED | TASK_ASSIGNED | TASK_STARTED |
TASK_COMPLETED | TASK_RELEASED | TASK_REASSIGNED | ROBOT_FAILED |
ROBOT_RECOVERED`

**Status:** `INTERNAL — READY`

---

## B. Future External Adapter Contract

These concepts represent the boundary between P5 and external systems.
Status markers: **EXISTS** | **PLANNED** | **MISSING** | **TO BE CONFIRMED**

---

### Task Announcement

| Concept | Direction | Status |
|---|---|---|
| `TaskAnnouncement` | External → P5 (via `TaskSource`) | **PLANNED** (Phase 7) |
| Fields: task_id, pickup, dropoff, priority, deadline, payload | — | **PLANNED** |
| ROS 2 topic: `/p5/task_announcements` | — | **PLANNED** (Phase 7) |

---

### Task Bid

| Concept | Direction | Status |
|---|---|---|
| `TaskBid` | P5 internal → EventSink → external | **PLANNED** (Phase 7) |
| Fields: task_id, robot_id, score | — | **PLANNED** |
| ROS 2 topic: `/p5/bids` | — | **PLANNED** (Phase 7) |

---

### Task Assignment

| Concept | Direction | Status |
|---|---|---|
| `TaskAssignment` | P5 → NavigationAdapter | **PLANNED** (Phase 7–8) |
| Fields: task_id, robot_id, pickup, dropoff | — | **PLANNED** |
| ROS 2 topic: `/p5/assignments` | — | **PLANNED** (Phase 7) |

---

### Robot State

| Concept | Direction | Status |
|---|---|---|
| `RobotState` (external) | External → P5 (via `RobotStateProvider`) | **TO BE CONFIRMED** |
| Adapter converts to internal `Robot` | — | **PLANNED** |
| ROS 2 topic: TBD (depends on P3/P4 team) | — | **TO BE CONFIRMED** |

> ⚠️ **Note:** P5 does NOT import another team's `RobotState` class directly.
> A P5-owned adapter performs the translation.

---

### Robot Intent / Nav Goal

| Concept | Direction | Status |
|---|---|---|
| Navigation goal | P5 → Nav2 (via `NavigationAdapter`) | **PLANNED** (Phase 8) |
| Fields: robot_id, pickup_location, dropoff_location | — | **PLANNED** |
| Nav2 action: `navigate_to_pose` | — | **PLANNED** (Phase 8) |

---

### Heartbeat

| Concept | Direction | Status |
|---|---|---|
| Heartbeat signal | Each robot → P5 (via `HeartbeatSource`) | **PLANNED** (Phase 9) |
| Fields: robot_id, timestamp, status | — | **INTERNAL — READY** |
| ROS 2 topic: `/p5/heartbeat` | — | **PLANNED** (Phase 9) |

---

### Task Event

| Concept | Direction | Status |
|---|---|---|
| `TaskEvent` (external observable) | P5 → EventSink → external | **PLANNED** (Phase 7) |
| Maps to internal `P5Event` | — | **INTERNAL — READY** |
| ROS 2 topic: `/p5/events` | — | **PLANNED** (Phase 7) |

---

## Adapter Implementation Guide (Phase 7)

To connect a new external system, implement the relevant `Protocol`
from `p5.adapters.interfaces`.

Example (ROS 2):

```python
# NOT part of Phase 1 — shown for planning purposes only

from p5.adapters.interfaces import TaskSource
from p5.models.task import Task, TaskStatus

class ROS2TaskSource:
    """Implements TaskSource protocol using ROS 2 subscriptions."""

    def __init__(self, ros2_node):
        self._node = ros2_node
        self._pending: list[Task] = []
        # Subscribe to ROS 2 task announcement topic ...

    def get_available_tasks(self) -> list[Task]:
        return [t for t in self._pending if t.status == TaskStatus.AVAILABLE]

    def acknowledge_task(self, task_id: str) -> None:
        self._pending = [t for t in self._pending if t.task_id != task_id]
```

**The P5 core never changes.** Only the adapter changes.

---

## Summary

| Contract | Status |
|---|---|
| Internal P5 models | ✅ READY |
| Adapter interfaces (Protocols) | ✅ READY |
| ROS 2 adapter implementations | ⏳ PLANNED Phase 7 |
| Nav2 adapter | ⏳ PLANNED Phase 8 |
| Heartbeat implementation | ⏳ PLANNED Phase 9 |
| Failure detection | ⏳ PLANNED Phase 10 |
| Full recovery | ⏳ PLANNED Phase 14 |
