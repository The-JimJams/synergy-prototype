"""
P5 Standalone Demo — Phase 3
==============================

Terminal-only demonstration of the P5 core data models and
Phase 3 capability checking.

Usage
-----
    python simulation/standalone_demo.py        (from p5_task_failure/)
    python -m simulation.standalone_demo        (from p5_task_failure/)

What this script does
---------------------
1. Creates three simulated robots (A, B, C).
2. Creates one simulated task (T01).
3. Creates a placeholder Bid (Robot A -> T01).
4. Creates heartbeats for all three robots.
5. Creates a sample P5 internal event.
6. Runs Phase 3 capability checking for each robot against T01.
7. Prints a formatted report to the terminal.

What this script does NOT do (deferred)
-----------------------------------------
- No bid score calculation (Phase 4).
- No winner selection (Phase 5).
- No heartbeat timeout monitoring (Phase 9).
- No failure detection (Phase 10).
- No task recovery (Phase 14).
- No ROS 2 connections.
- No GUI or dashboard.
- No network connections.

Dependencies
------------
None beyond the Python standard library and the p5 package itself.
No ROS 2, Gazebo, Nav2, or any external framework.
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Make p5 importable when running from the p5_task_failure/ directory
# or from the simulation/ subdirectory.
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULE_ROOT = os.path.dirname(_THIS_DIR)  # p5_task_failure/
if _MODULE_ROOT not in sys.path:
    sys.path.insert(0, _MODULE_ROOT)

from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.models.bid import Bid
from p5.models.heartbeat import Heartbeat, HeartbeatStatus
from p5.models.events import P5Event, P5EventType
from p5.allocation.capability import CapabilityChecker, CapabilityResult

# ---------------------------------------------------------------------------
# Constants / helpers
# ---------------------------------------------------------------------------

DIVIDER = "=" * 60
SUB_DIVIDER = "-" * 40
NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def section(title: str) -> None:
    print(f"\n{SUB_DIVIDER}")
    print(f"  {title}")
    print(SUB_DIVIDER)


# ---------------------------------------------------------------------------
# Deterministic simulation data
# ---------------------------------------------------------------------------

def build_robots() -> list[Robot]:
    """Create three deterministic simulated robots for Phase 3 demo.

    Robot A: AVAILABLE, capacity 500  — should be ELIGIBLE
    Robot B: AVAILABLE, capacity  50  — should be NOT ELIGIBLE (payload)
    Robot C: FAILED,    capacity 500  — should be NOT ELIGIBLE (status)
    """
    return [
        Robot(
            robot_id="A",
            position=(2.0, 2.0),
            battery=90.0,
            payload_capacity=500.0,
            current_task=None,
            workload=0,
            status=RobotStatus.AVAILABLE,
            capabilities=("CARRY", "LIFT"),
        ),
        Robot(
            robot_id="B",
            position=(8.0, 3.0),
            battery=65.0,
            payload_capacity=50.0,     # intentionally low for demo
            current_task=None,
            workload=0,
            status=RobotStatus.AVAILABLE,
            capabilities=("CARRY",),
        ),
        Robot(
            robot_id="C",
            position=(15.0, 10.0),
            battery=45.0,
            payload_capacity=500.0,
            current_task=None,
            workload=0,
            status=RobotStatus.FAILED,  # intentionally FAILED for demo
            capabilities=("CARRY", "HAZMAT"),
        ),
    ]


def build_task() -> Task:
    """Create one deterministic simulated task."""
    return Task(
        task_id="T01",
        pickup_location=(10.0, 4.0),
        dropoff_location=(18.0, 9.0),
        priority=7,
        deadline=60.0,
        required_payload=100.0,
        status=TaskStatus.AVAILABLE,
        assigned_robot=None,
        required_capabilities=("CARRY",),
    )


def build_bid(robot: Robot, task: Task) -> Bid:
    """Create a placeholder Bid (Phase 1 — score not calculated yet)."""
    return Bid(
        task_id=task.task_id,
        robot_id=robot.robot_id,
        score=0.0,        # Phase 4 will compute real scores
        estimated_time=0.0,
        distance=robot.distance_to(task.pickup_location),
        battery_cost=0.0,
        valid=True,
        timestamp=NOW,
    )


def build_heartbeats(robots: list[Robot]) -> list[Heartbeat]:
    """Create one ALIVE heartbeat per robot."""
    return [
        Heartbeat(
            robot_id=r.robot_id,
            timestamp=NOW,
            status=HeartbeatStatus.ALIVE,
        )
        for r in robots
    ]


def build_event(task: Task) -> P5Event:
    """Create a TASK_ANNOUNCED event for the given task."""
    return P5Event(
        event_type=P5EventType.TASK_ANNOUNCED,
        timestamp=NOW,
        source_robot=None,
        task_id=task.task_id,
        payload={"priority": task.priority, "deadline": task.deadline},
    )


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def print_robot(robot: Robot) -> None:
    dist_note = ""
    print(
        f"  Robot {robot.robot_id}"
        f"  pos=({robot.position[0]:.0f}, {robot.position[1]:.0f})"
        f"  battery={robot.battery:.0f}%"
        f"  capacity={robot.payload_capacity:.0f}"
        f"  status={robot.status.value}"
        f"  caps={robot.capabilities}"
    )


def print_task(task: Task) -> None:
    dist = task.transport_distance()
    print(f"  Task ID       : {task.task_id}")
    print(f"  Pickup        : {task.pickup_location}")
    print(f"  Dropoff       : {task.dropoff_location}")
    print(f"  Distance      : {dist:.2f} units")
    print(f"  Priority      : {task.priority}/10")
    print(f"  Deadline      : {task.deadline}s")
    print(f"  Required load : {task.required_payload} units")
    print(f"  Status        : {task.status.value}")
    print(f"  Assigned robot: {task.assigned_robot!r}")
    print(f"  Capabilities  : {task.required_capabilities}")
    print(f"  Allowed next  : {[s.value for s in task.allowed_transitions()]}")


def print_bid(bid: Bid, robot: Robot, task: Task) -> None:
    print(f"  Robot {bid.robot_id} -> Task {bid.task_id}")
    print(f"  Distance to pickup : {bid.distance:.2f} units")
    print(f"  Score              : {bid.score:.3f}  [Phase 4: not yet computed]")
    print(f"  Estimated time     : {bid.estimated_time:.1f}s  [Phase 4: not yet computed]")
    print(f"  Battery cost       : {bid.battery_cost:.1f}%   [Phase 4: not yet computed]")
    print(f"  Valid              : {bid.valid}")


def print_heartbeat(hb: Heartbeat) -> None:
    print(f"  Robot {hb.robot_id}  status={hb.status.value}  ts={hb.timestamp.strftime('%H:%M:%SZ')}")


def print_event(event: P5Event) -> None:
    print(f"  Type       : {event.event_type.value}")
    print(f"  Task       : {event.task_id!r}")
    print(f"  Robot      : {event.source_robot!r}")
    print(f"  Timestamp  : {event.timestamp.strftime('%H:%M:%SZ')}")
    print(f"  Payload    : {event.payload}")


def print_capability_result(result: CapabilityResult) -> None:
    """Print a single CapabilityResult in a readable format."""
    if result.eligible:
        verdict = "ELIGIBLE"
        detail  = ""
    else:
        verdict = "NOT ELIGIBLE"
        detail  = "  reasons: " + ", ".join(result.reasons)
    print(f"  Robot {result.robot_id}  ->  {verdict}{detail}")


def print_deferred() -> None:
    items = [
        ("Phase 1",  "Core data models                [DONE]"),
        ("Phase 2",  "Model validation                [DONE]"),
        ("Phase 3",  "Capability checking             [DONE]"),
        ("Phase 4",  "Bid calculation algorithm"),
        ("Phase 5",  "Deterministic winner selection"),
        ("Phase 6",  "Task state machine enforcement"),
        ("Phase 7",  "ROS 2 adapter integration"),
        ("Phase 8",  "Nav2 adapter integration"),
        ("Phase 9",  "Heartbeat monitoring"),
        ("Phase 10", "Failure detection (timeout-based)"),
        ("Phase 11", "Task release"),
        ("Phase 12", "Task re-announcement"),
        ("Phase 13", "Task reassignment"),
        ("Phase 14", "Full failure recovery"),
        ("Phase 15", "Blocked-aisle resilience"),
        ("Phase 16", "Optional: communication degradation"),
    ]
    for phase, description in items:
        print(f"  {phase:<10}  {description}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print(DIVIDER)
    print("  P5 STANDALONE DEMO  --  END-TO-END MVP")
    print(DIVIDER)
    print()

    from datetime import datetime, timedelta, timezone
    from p5.models.robot import Robot, RobotStatus
    from p5.models.task import Task, TaskStatus
    from p5.models.heartbeat import Heartbeat, HeartbeatStatus
    from p5.manager.task_manager import TaskManager
    from p5.failure.detector import FailureDetector
    from p5.recovery.task_recovery import TaskRecoveryManager
    from p5.allocation.capability import CapabilityChecker
    from p5.allocation.bidder import Bidder

    # STEP 1: INITIAL STATE (3 robots, 2 tasks)
    robots = [
        Robot("A", (2.0, 2.0), 90.0, 500.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",)),
        Robot("B", (8.0, 3.0), 65.0, 500.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",)),
        Robot("C", (15.0, 10.0), 45.0, 500.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",)),
    ]
    tasks = [
        Task("T01", (10.0, 4.0), (18.0, 9.0), 7, 60.0, 100.0, TaskStatus.AVAILABLE, None, ("CARRY",)),
        Task("T02", (3.0, 3.0), (10.0, 1.0), 5, 60.0, 100.0, TaskStatus.AVAILABLE, None, ("CARRY",)),
    ]
    
    manager = TaskManager()
    detector = FailureDetector()
    recovery = TaskRecoveryManager()
    checker = CapabilityChecker()
    bidder = Bidder()
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    print("INITIAL STATE:")
    for r in robots:
        print(f"Robot {r.robot_id} -> {r.status.value}")
    for t in tasks:
        print(f"Task {t.task_id} -> {t.status.value}")
    print()
    
    # STEP 2-5: FIRST ALLOCATION (both tasks)
    print("ALLOCATING INITIAL TASKS...")
    for t in tasks:
        # Steps 2-3: Print bids
        for r in robots:
            if checker.check(r, t).eligible:
                bid = bidder.create_bid(r, t)
                print(f"Task {t.task_id} - Robot {r.robot_id} BID: score={bid.score:.3f}")
                
        # Step 4-5: Assign
        manager.allocate_task(t, robots)
        print(f"WINNER for {t.task_id}: Robot {t.assigned_robot}")
        print()
    
    # State check
    print("STATE AFTER INITIAL ALLOCATION:")
    for r in robots:
        print(f"Robot {r.robot_id} -> {r.status.value} (Task: {r.current_task})")
    print()
    
    # STEP 6-7: SIMULATING A FAILURE
    # Find who won T01 (it should be B based on distance)
    t01 = next(t for t in tasks if t.task_id == "T01")
    failed_robot_id = t01.assigned_robot
    assert failed_robot_id is not None, "Task must have an assigned robot to fail"
    failed_robot = next(r for r in robots if r.robot_id == failed_robot_id)
    
    print(f"SIMULATING ROBOT {failed_robot_id} FAILURE...")
    hb_stale = Heartbeat(failed_robot_id, now - timedelta(seconds=10), HeartbeatStatus.ALIVE)
    detector.detect(failed_robot, hb_stale, now)
    
    print("FAILURE DETECTED:")
    print(f"Robot {failed_robot_id} -> {failed_robot.status.value}")
    print()
    
    # STEP 8: TASK RECOVERY
    print(f"TASK RECOVERY FOR {t01.task_id}...")
    recovery.recover(t01, failed_robot)
    print(f"Task {t01.task_id} -> {t01.status.value}")
    print(f"Robot {failed_robot_id} task -> {failed_robot.current_task}")
    print()
    
    # STEP 9-10: RE-ALLOCATION
    print(f"RE-ALLOCATING TASK {t01.task_id}...")
    for r in robots:
        if checker.check(r, t01).eligible:
            bid = bidder.create_bid(r, t01)
            print(f"Task {t01.task_id} - Robot {r.robot_id} BID: score={bid.score:.3f}")
            
    manager.allocate_task(t01, robots)
    print(f"NEW WINNER for {t01.task_id}: Robot {t01.assigned_robot}")
    print()
    
    # STEP 11: FINAL STATE
    print("FINAL STATE:")
    for t in tasks:
        print(f"{t.task_id} -> {t.status.value}, assigned to Robot {t.assigned_robot}")
    for r in robots:
        print(f"Robot {r.robot_id} -> {r.status.value} (Task: {r.current_task})")

    print()
    print(DIVIDER)
    print("  END-TO-END MVP  [OK]  COMPLETE")
    print(DIVIDER)
    print()

if __name__ == "__main__":
    main()

