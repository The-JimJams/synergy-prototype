"""
P5 Standalone Demo — Phase 1
==============================

Terminal-only demonstration of the P5 core data models.

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
6. Prints a formatted report to the terminal.

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
    """Create three deterministic simulated robots."""
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
            payload_capacity=300.0,
            current_task=None,
            workload=0,
            status=RobotStatus.AVAILABLE,
            capabilities=("CARRY",),
        ),
        Robot(
            robot_id="C",
            position=(15.0, 10.0),
            battery=45.0,
            payload_capacity=400.0,
            current_task=None,
            workload=0,
            status=RobotStatus.AVAILABLE,
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


def print_deferred() -> None:
    items = [
        ("Phase 2",  "Task data model validation"),
        ("Phase 3",  "Capability checking"),
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
    print("  P5 STANDALONE DEMO  --  Phase 1 Foundation")
    print("  Distributed Task Allocation & Failure Recovery")
    print(DIVIDER)
    print()
    print("  Core dependencies: Python standard library only.")
    print("  ROS 2 : NOT REQUIRED    Gazebo : NOT REQUIRED")
    print("  Nav2  : NOT REQUIRED    UI     : NOT REQUIRED")

    # ------------------------------------------------------------------
    robots = build_robots()
    task = build_task()
    bid = build_bid(robots[0], task)          # Robot A bids on T01
    heartbeats = build_heartbeats(robots)
    event = build_event(task)
    # ------------------------------------------------------------------

    section("ROBOTS")
    for r in robots:
        print_robot(r)

    section("TASK")
    print_task(task)

    section("SAMPLE BID  (Robot A -> T01)")
    print_bid(bid, robots[0], task)

    section("HEARTBEATS")
    for hb in heartbeats:
        print_heartbeat(hb)

    section("INTERNAL EVENT")
    print_event(event)

    section("ADAPTER INTERFACES  (Phase 1: defined, not yet wired)")
    interfaces = [
        "TaskSource",
        "RobotStateProvider",
        "BidCalculator",
        "WinnerSelector",
        "HeartbeatSource",
        "FailureDetector",
        "TaskRecoveryManager",
        "EventSink",
        "NavigationAdapter",
    ]
    for iface in interfaces:
        print(f"  [DEFINED]  {iface}")

    section("DEFERRED WORK")
    print_deferred()

    print()
    print(DIVIDER)
    print("  P5 PHASE 1 -- STANDALONE FOUNDATION  [OK]  COMPLETE")
    print("  All models instantiated successfully.")
    print("  No external systems required.")
    print(DIVIDER)
    print()


if __name__ == "__main__":
    main()
