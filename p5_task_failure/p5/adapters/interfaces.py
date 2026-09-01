"""
P5 Adapter Interfaces
=====================

Defines the BOUNDARY between the P5 core and all external systems.

Rules
-----
* This file MUST NOT import ROS 2, Gazebo, Nav2, or any external framework.
* All interfaces are expressed as ``typing.Protocol`` (structural subtyping).
* External adapters (ROS 2, simulator, etc.) implement these protocols
  without any modification to P5 core code.
* During standalone testing, mock implementations are used instead.

Integration plan
----------------
Phase 7:  ROS 2 adapters implement TaskSource, RobotStateProvider,
          HeartbeatSource, EventSink, NavigationAdapter.
Phase 8:  Nav2 adapter implements NavigationAdapter.
Phase 10: Real FailureDetector replaces the stub.
Phase 14: Full TaskRecoveryManager replaces the stub.

Architecture
------------

                    P5 CORE
                       |
          +------------+------------+
          |            |            |
       Simulator    ROS 2 Adapter  Future Adapter
          |            |
       implements  implements
          |            |
          +-----> Protocol <----+
                  (this file)
"""

from __future__ import annotations

from typing import List, Optional, Protocol, runtime_checkable

# Avoid circular import — import only the minimal set from models
from p5.models.robot import Robot
from p5.models.task import Task
from p5.models.bid import Bid
from p5.models.heartbeat import Heartbeat
from p5.models.events import P5Event


# ---------------------------------------------------------------------------
# Task source
# ---------------------------------------------------------------------------

@runtime_checkable
class TaskSource(Protocol):
    """Provides tasks to the P5 allocation system.

    External adapters
    -----------------
    - ROS 2 adapter: subscribes to task announcement topic, deserialises
      messages into Task objects.
    - Simulator adapter: returns tasks from an in-memory list.
    """

    def get_available_tasks(self) -> List[Task]:
        """Return all tasks currently in AVAILABLE or ANNOUNCED state."""
        ...

    def acknowledge_task(self, task_id: str) -> None:
        """Mark a task as received (prevents duplicate announcements)."""
        ...


# ---------------------------------------------------------------------------
# Robot state provider
# ---------------------------------------------------------------------------

@runtime_checkable
class RobotStateProvider(Protocol):
    """Provides current robot states to the P5 allocation system.

    External adapters
    -----------------
    - ROS 2 adapter: subscribes to /robot_state topics, converts to Robot.
    - Simulator adapter: returns robots from an in-memory dict.

    IMPORTANT: Do NOT import another developer's RobotState definition here.
    Each external adapter is responsible for the translation.
    """

    def get_robot_state(self, robot_id: str) -> Optional[Robot]:
        """Return the current state of the robot, or None if unknown."""
        ...

    def get_all_robots(self) -> List[Robot]:
        """Return states of all known robots."""
        ...


# ---------------------------------------------------------------------------
# Bid calculator (Phase 4)
# ---------------------------------------------------------------------------

@runtime_checkable
class BidCalculator(Protocol):
    """Calculates a bid score for a (robot, task) pair.

    Phase 4 will implement the actual scoring algorithm.
    The interface is defined here to establish the contract.

    Inputs:  Robot, Task
    Output:  Bid (with score, estimated_time, distance, battery_cost populated)
    """

    def calculate_bid(self, robot: Robot, task: Task) -> Bid:
        """Calculate and return a Bid for the given robot-task pair.

        The returned Bid.valid should be False if the robot is ineligible
        (insufficient payload, missing capability, etc.).
        """
        ...


# ---------------------------------------------------------------------------
# Winner selector (Phase 5)
# ---------------------------------------------------------------------------

@runtime_checkable
class WinnerSelector(Protocol):
    """Selects the winning bid from a list of valid bids.

    Phase 5 will implement the deterministic selection algorithm.

    Determinism requirement: given the same list of bids, the selector
    must always return the same winner (no randomness, no ties broken
    arbitrarily).
    """

    def select_winner(self, bids: List[Bid]) -> Optional[Bid]:
        """Return the best Bid, or None if no valid bids exist."""
        ...


# ---------------------------------------------------------------------------
# Heartbeat source (Phase 9)
# ---------------------------------------------------------------------------

@runtime_checkable
class HeartbeatSource(Protocol):
    """Provides heartbeat information for all robots.

    Phase 9 will implement the actual heartbeat publisher/subscriber.

    External adapters
    -----------------
    - ROS 2 adapter: subscribes to /heartbeat topics.
    - Simulator adapter: generates synthetic heartbeats on a timer.
    """

    def get_latest_heartbeat(self, robot_id: str) -> Optional[Heartbeat]:
        """Return the most recent Heartbeat from the robot, or None."""
        ...

    def get_all_heartbeats(self) -> List[Heartbeat]:
        """Return the most recent heartbeat for every known robot."""
        ...


# ---------------------------------------------------------------------------
# Failure detector (Phase 10)
# ---------------------------------------------------------------------------

@runtime_checkable
class FailureDetector(Protocol):
    """Determines whether a robot has failed based on heartbeat timing.

    Phase 10 will implement the actual timeout-based detection.

    Contract
    --------
    A robot is SUSPECTED when no heartbeat has been received within
    SUSPECT_TIMEOUT seconds.
    A robot is FAILED when no heartbeat has been received within
    FAILURE_TIMEOUT seconds (FAILURE_TIMEOUT > SUSPECT_TIMEOUT).
    """

    def is_failed(self, robot_id: str) -> bool:
        """Return True if the robot is classified as FAILED."""
        ...

    def is_suspected(self, robot_id: str) -> bool:
        """Return True if the robot is classified as SUSPECTED."""
        ...


# ---------------------------------------------------------------------------
# Task recovery manager (Phase 14)
# ---------------------------------------------------------------------------

@runtime_checkable
class TaskRecoveryManager(Protocol):
    """Releases and re-announces tasks after a robot failure.

    Phase 14 will implement the full recovery flow.

    Flow
    ----
    robot_failed(robot_id)
      -> find tasks owned by robot_id
      -> for each task: release_task(task_id) -> RECOVERY
      -> re_announce_task(task_id) -> ANNOUNCED
      -> allocation system picks up the re-announced task
    """

    def release_task(self, task_id: str) -> None:
        """Move task to RECOVERY state and clear assigned_robot."""
        ...

    def re_announce_task(self, task_id: str) -> None:
        """Re-announce the task so remaining robots can bid."""
        ...


# ---------------------------------------------------------------------------
# Event sink
# ---------------------------------------------------------------------------

@runtime_checkable
class EventSink(Protocol):
    """Receives P5 internal events and forwards them to external systems.

    External adapters
    -----------------
    - ROS 2 adapter: publishes events on appropriate ROS 2 topics.
    - Logger adapter: writes events to a log file.
    - Test adapter: appends events to an in-memory list for assertions.
    """

    def emit(self, event: P5Event) -> None:
        """Emit a P5 internal event to the external system."""
        ...


# ---------------------------------------------------------------------------
# Navigation adapter (Phase 8)
# ---------------------------------------------------------------------------

@runtime_checkable
class NavigationAdapter(Protocol):
    """Hands off a task assignment to the robot's navigation stack.

    Phase 8 will implement the Nav2 adapter.

    The P5 core does NOT navigate robots.  It only informs the navigation
    system of the assignment.  The navigation system executes autonomously.
    """

    def send_navigation_goal(self, robot_id: str, task: Task) -> bool:
        """Send the task's pickup/dropoff goal to the robot's nav stack.

        Returns True if the goal was accepted, False otherwise.
        """
        ...

    def cancel_navigation_goal(self, robot_id: str) -> None:
        """Cancel any active navigation goal for the given robot."""
        ...
