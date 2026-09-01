# P5 Data Model Reference

## Overview

This document describes the internal P5 data models: their fields,
semantics, and lifecycle states.

All models are plain Python dataclasses with no external dependencies.
No ROS 2, Gazebo, Nav2, or network required.

---

## Robot

```python
from p5.models.robot import Robot, RobotStatus
```

### Fields

| Field              | Type                  | Description                                          |
|--------------------|-----------------------|------------------------------------------------------|
| `robot_id`         | `str`                 | Unique identifier (e.g. `"A"`, `"robot_1"`)          |
| `position`         | `Tuple[float, float]` | Current `(x, y)` in warehouse coordinate frame      |
| `battery`          | `float`               | Battery level in percent `[0.0 – 100.0]`            |
| `payload_capacity` | `float`               | Maximum payload the robot can carry (warehouse units)|
| `current_task`     | `Optional[str]`       | `task_id` of active task, or `None` if idle          |
| `workload`         | `int`                 | Number of tasks queued / in progress                 |
| `status`           | `RobotStatus`         | Current lifecycle status                             |
| `capabilities`     | `Tuple[str, ...]`     | Immutable capability tags (e.g. `("CARRY", "LIFT")`) |

### RobotStatus

| Value       | Meaning                                          |
|-------------|--------------------------------------------------|
| `AVAILABLE` | Idle, accepting new tasks                        |
| `BUSY`      | Currently executing a task                       |
| `CHARGING`  | At a charging station, temporarily unavailable   |
| `OFFLINE`   | Graceful shutdown — unreachable                  |
| `FAILED`    | Heartbeat timeout exceeded — considered lost     |
| `RECOVERED` | Reconnected after FAILED — awaiting confirmation |

### Lifecycle Transitions

```
AVAILABLE  -> BUSY      (task accepted)
AVAILABLE  -> CHARGING  (battery low)
BUSY       -> AVAILABLE (task completed)
BUSY       -> FAILED    (heartbeat timeout)
CHARGING   -> AVAILABLE (battery restored)
FAILED     -> RECOVERED (reconnected)
RECOVERED  -> AVAILABLE (confirmed operational)
any        -> OFFLINE   (graceful shutdown)
```

---

## Task

```python
from p5.models.task import Task, TaskStatus, TASK_TRANSITIONS
```

### Fields

| Field                   | Type                  | Description                                       |
|-------------------------|-----------------------|---------------------------------------------------|
| `task_id`               | `str`                 | Unique identifier (e.g. `"T01"`)                  |
| `pickup_location`       | `Tuple[float, float]` | `(x, y)` warehouse coordinates for item pick-up  |
| `dropoff_location`      | `Tuple[float, float]` | `(x, y)` warehouse coordinates for drop-off      |
| `priority`              | `int`                 | Task urgency `[1 – 10]`. Higher = more urgent     |
| `deadline`              | `float`               | Max completion time in seconds from task creation |
| `required_payload`      | `float`               | Minimum payload capacity required                 |
| `status`                | `TaskStatus`          | Current lifecycle state                           |
| `assigned_robot`        | `Optional[str]`       | `robot_id` of winning robot, or `None`            |
| `required_capabilities` | `Tuple[str, ...]`     | Capability tags the robot must possess            |

### TaskStatus

| Value        | Meaning                                              |
|--------------|------------------------------------------------------|
| `AVAILABLE`  | Task is ready to be announced                        |
| `ANNOUNCED`  | Broadcast to robots, bidding not yet started         |
| `BIDDING`    | Auction is open                                      |
| `ASSIGNED`   | Winner selected, robot notified                      |
| `IN_PROGRESS`| Robot is executing the task                          |
| `COMPLETED`  | Task finished successfully (**terminal**)            |
| `FAILED`     | Robot failed mid-task                                |
| `RECOVERY`   | Recovery triggered — task being re-announced         |
| `CANCELLED`  | Task cancelled from any state (**terminal**)         |

### State Machine

```
AVAILABLE
    |
    v  (announce)
ANNOUNCED
    |
    v  (bidding opens)
BIDDING
    |
    v  (winner selected)
ASSIGNED
    |
    v  (robot starts moving)
IN_PROGRESS
    |
+---+---+
|       |
v       v
COMPLETED  FAILED
            |
            v  (recovery triggered)
        RECOVERY
            |
            v  (re-announced)
        ANNOUNCED  (loop)

CANCELLED  <- can be reached from most states (terminal)
```

---

## Bid

```python
from p5.models.bid import Bid
```

### Fields

| Field            | Type       | Description                                     |
|------------------|------------|-------------------------------------------------|
| `task_id`        | `str`      | The task being bid on                           |
| `robot_id`       | `str`      | The robot submitting the bid                    |
| `score`          | `float`    | Composite bid score (Phase 4: not yet computed) |
| `estimated_time` | `float`    | Estimated seconds to complete                   |
| `distance`       | `float`    | Euclidean distance from robot to task pickup    |
| `battery_cost`   | `float`    | Estimated battery consumed (percent)            |
| `valid`          | `bool`     | False if robot is ineligible                    |
| `timestamp`      | `datetime` | UTC time when this bid was created              |

**Status:** `INTERNAL — READY (scoring deferred to Phase 4)`

---

## Heartbeat

```python
from p5.models.heartbeat import Heartbeat, HeartbeatStatus
```

### Fields

| Field       | Type              | Description                               |
|-------------|-------------------|-------------------------------------------|
| `robot_id`  | `str`             | The robot that sent this heartbeat        |
| `timestamp` | `datetime`        | UTC timestamp when produced               |
| `status`    | `HeartbeatStatus` | Health classification at this moment      |

### HeartbeatStatus

| Value       | Meaning                                       |
|-------------|-----------------------------------------------|
| `ALIVE`     | Robot is healthy and active                   |
| `SUSPECTED` | Threshold 1 exceeded — investigating          |
| `FAILED`    | Threshold 2 exceeded — considered lost        |
| `RECOVERED` | Robot reconnected after FAILED                |

**Status:** `INTERNAL — READY (monitoring deferred to Phase 9)`

---

## P5Event

```python
from p5.models.events import P5Event, P5EventType
```

### Fields

| Field          | Type           | Description                                    |
|----------------|----------------|------------------------------------------------|
| `event_type`   | `P5EventType`  | The kind of event that occurred                |
| `timestamp`    | `datetime`     | UTC time when the event was created            |
| `source_robot` | `Optional[str]`| `robot_id` that triggered the event, if any   |
| `task_id`      | `Optional[str]`| `task_id` this event relates to, if any        |
| `payload`      | `Optional[Any]`| Additional structured data (no ROS 2 objects) |

### P5EventType

| Value            | Meaning                                       |
|------------------|-----------------------------------------------|
| `TASK_ANNOUNCED` | Task broadcast to all robots                  |
| `BID_SUBMITTED`  | A robot has submitted a bid                   |
| `TASK_ASSIGNED`  | Winner selected and notified                  |
| `TASK_STARTED`   | Robot confirmed task start                    |
| `TASK_COMPLETED` | Robot confirmed task completion               |
| `TASK_RELEASED`  | Task released for recovery                    |
| `TASK_REASSIGNED`| Task assigned to a different robot            |
| `ROBOT_FAILED`   | Failure detected for a robot                  |
| `ROBOT_RECOVERED`| Robot reconnected after failure               |

**Status:** `INTERNAL — READY`

---

## Capability Checking

### Purpose

The `CapabilityChecker` determines whether a **specific robot is eligible
to perform a specific task**.

This is a **filter** — it answers:

> "Can this robot perform this task?"

It does **not** answer which robot *should* perform the task.
That question belongs to Phase 4 (bidding) and Phase 5 (winner selection).

### Inputs

| Input   | Type            | Notes                                     |
|---------|-----------------|-------------------------------------------|
| `robot` | `Robot \| None` | `None` produces a clean ineligible result |
| `task`  | `Task \| None`  | `None` produces a clean ineligible result |

### Output

```python
CapabilityResult(
    eligible: bool,
    robot_id: str,           # "<none>" if robot was None
    task_id:  str,           # "<none>" if task was None
    reasons:  Tuple[str, ...],  # empty when eligible
)
```

### Validation Rules

All checks are evaluated (no short-circuit).  Every applicable reason
code is collected and returned in the result.

#### 1. None Guard

If either `robot` or `task` is `None`, returns `TASK_INVALID` immediately.

#### 2. Task Validity

| Condition                   | Reason Code  |
|-----------------------------|--------------|
| `task.required_payload < 0` | `TASK_INVALID` |

#### 3. Task Status

| Task Status | Reason Code      |
|-------------|------------------|
| `CANCELLED` | `TASK_CANCELLED` |
| `COMPLETED` | `TASK_COMPLETED` |
| All others  | no rejection     |

#### 4. Robot Status

| Robot Status | Reason Code         |
|--------------|---------------------|
| `FAILED`     | `ROBOT_FAILED`      |
| `OFFLINE`    | `ROBOT_OFFLINE`     |
| `CHARGING`   | `ROBOT_CHARGING`    |
| `BUSY`       | `ROBOT_UNAVAILABLE` |
| `AVAILABLE`  | no rejection        |
| `RECOVERED`  | no rejection        |

**Policy:** `BUSY` robots are **not eligible** for new tasks.
P5 does not support parallel task assignment in this architecture.

#### 5. Payload Capacity

| Condition                                          | Reason Code            |
|----------------------------------------------------|------------------------|
| `task.required_payload > robot.payload_capacity`   | `PAYLOAD_INSUFFICIENT` |
| `task.required_payload <= robot.payload_capacity`  | pass                   |

Uses `<=`, so exact capacity match is allowed.

#### 6. Capability Tags

For each tag in `task.required_capabilities`:

| Condition                              | Reason Code          |
|----------------------------------------|----------------------|
| tag not in `robot.capabilities`        | `MISSING_CAPABILITY` |

`MISSING_CAPABILITY` appears **at most once** in `reasons`, regardless
of how many tags are missing.

### Reason Codes

| Code                  | Cause                                           |
|-----------------------|-------------------------------------------------|
| `ROBOT_UNAVAILABLE`   | Robot status is `BUSY`                          |
| `ROBOT_FAILED`        | Robot status is `FAILED`                        |
| `ROBOT_OFFLINE`       | Robot status is `OFFLINE`                       |
| `ROBOT_CHARGING`      | Robot status is `CHARGING`                      |
| `PAYLOAD_INSUFFICIENT`| `task.required_payload > robot.payload_capacity`|
| `MISSING_CAPABILITY`  | Robot lacks a required capability tag           |
| `TASK_INVALID`        | Task or robot is `None`, or payload < 0         |
| `TASK_CANCELLED`      | Task status is `CANCELLED`                      |
| `TASK_COMPLETED`      | Task status is `COMPLETED`                      |

Reason codes are deterministic string constants defined in
`p5/allocation/capability.py`.

### Eligibility Rules

```
eligible = True
    when ALL of the following hold:
        robot is not None
        task is not None
        task.required_payload >= 0
        task.status not in {CANCELLED, COMPLETED}
        robot.status in {AVAILABLE, RECOVERED}
        task.required_payload <= robot.payload_capacity
        all tags in task.required_capabilities are in robot.capabilities
```

### Deterministic Behavior

- `check(robot, task)` called with identical inputs always returns an
  identical `CapabilityResult`.
- No randomness, no global state, no time-dependent logic.
- `CapabilityResult` is a `frozen=True` dataclass — immutable after creation.
- The checker never mutates `Robot` or `Task`.

### Usage Example

```python
from p5.allocation.capability import CapabilityChecker

checker = CapabilityChecker()

result = checker.check(robot_a, task_t01)

if result.eligible:
    print(f"Robot {result.robot_id} is ELIGIBLE for {result.task_id}")
else:
    print(f"Robot {result.robot_id} is NOT ELIGIBLE: {result.reasons}")
```

### Flow Diagram

```
Robot + Task
     |
     v
CapabilityChecker.check()
     |
     +-- None guard
     |
     +-- Task validity check (required_payload >= 0)
     |
     +-- Task status check (not CANCELLED, not COMPLETED)
     |
     +-- Robot status check (AVAILABLE or RECOVERED)
     |
     +-- Payload check (capacity >= required)
     |
     +-- Capability tag check
     |
     v
CapabilityResult
     |
     +---- eligible=False --> reject (with reasons)
     |
     +---- eligible=True
                |
                v
          Future Bidder (Phase 4)
```

**Status:** `INTERNAL — READY (Phase 3 complete)`
