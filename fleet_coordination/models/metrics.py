"""
Metrics Models — Telemetry and benchmark reporting data structures.
=================================================================

Pure Python dataclasses for capturing observational data about tasks,
robots, and the overall fleet benchmark performance.

Zero ROS imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fleet_coordination.models.task import TaskStatus


@dataclass
class TaskMetrics:
    """Historical record of a task's lifecycle."""
    task_id: str
    announced_at: float
    completed_at: float | None = None
    completion_time_seconds: float | None = None
    status: TaskStatus = TaskStatus.ANNOUNCED


@dataclass
class RobotMetrics:
    """Historical record of a robot's performance and waiting states."""
    robot_id: str
    total_waiting_time_seconds: float = 0.0
    tasks_completed: int = 0
    collision_count: int = 0
    # Internal tracking for state transitions
    _last_wait_start: float | None = field(default=None, repr=False, init=False)


@dataclass
class PerformanceMetrics:
    """Aggregated benchmark metrics for a single scenario run."""
    total_tasks_completed: int
    total_collisions: int
    average_task_completion_time: float
    average_robot_waiting_time: float
    throughput_tasks_per_hour: float
    total_reroutes_successful: int
    total_network_recovery_events: int
    scenario_duration_seconds: float
