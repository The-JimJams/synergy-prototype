"""
MetricsLogger — Observational event historian.
==============================================

Tracks state transitions and events across the fleet to calculate
benchmarks. Does NOT make coordination decisions or mutate WorldModel.
"""

from __future__ import annotations

import math

from fleet_coordination.models.metrics import (
    PerformanceMetrics,
    RobotMetrics,
    TaskMetrics,
)
from fleet_coordination.models.robot_state import RobotStatus
from fleet_coordination.models.task import TaskStatus


class MetricsLogger:
    """Records fleet events and computes deterministic performance benchmarks."""

    def __init__(self, start_time: float) -> None:
        """Initialize logger with explicit scenario start time."""
        if not math.isfinite(start_time) or start_time < 0.0:
            raise ValueError(f"Invalid start_time: {start_time}")
            
        self._start_time = start_time
        self._tasks: dict[str, TaskMetrics] = {}
        self._robots: dict[str, RobotMetrics] = {}
        
        self._total_collisions = 0
        self._total_reroutes = 0
        self._total_network_recoveries = 0

    def _get_or_create_robot(self, robot_id: str) -> RobotMetrics:
        if robot_id not in self._robots:
            self._robots[robot_id] = RobotMetrics(robot_id=robot_id)
        return self._robots[robot_id]

    def log_task_status(self, task_id: str, status: TaskStatus, now: float) -> None:
        if not math.isfinite(now) or now < 0.0:
            raise ValueError("Invalid time 'now'")

        if task_id not in self._tasks:
            # We assume it's ANNOUNCED when first seen
            self._tasks[task_id] = TaskMetrics(task_id=task_id, announced_at=now)
            
        task = self._tasks[task_id]
        
        # Only record first completion
        if status == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            task.completed_at = now
            task.completion_time_seconds = now - task.announced_at
            
        task.status = status

    def log_robot_status(self, robot_id: str, status: RobotStatus, now: float) -> None:
        if not math.isfinite(now) or now < 0.0:
            raise ValueError("Invalid time 'now'")

        robot = self._get_or_create_robot(robot_id)
        
        if status == RobotStatus.WAITING:
            if robot._last_wait_start is None:
                robot._last_wait_start = now
        else:
            if robot._last_wait_start is not None:
                robot.total_waiting_time_seconds += (now - robot._last_wait_start)
                robot._last_wait_start = None

    def log_collision(self, robot_a_id: str, robot_b_id: str, now: float) -> None:
        self._total_collisions += 1
        ra = self._get_or_create_robot(robot_a_id)
        rb = self._get_or_create_robot(robot_b_id)
        ra.collision_count += 1
        rb.collision_count += 1

    def log_reroute_success(self, robot_id: str, now: float) -> None:
        self._total_reroutes += 1

    def log_network_recovery(self, now: float) -> None:
        self._total_network_recoveries += 1

    def compute_metrics(self, now: float) -> PerformanceMetrics:
        if not math.isfinite(now) or now < 0.0:
            raise ValueError("Invalid time 'now'")
            
        duration = max(now - self._start_time, 1.0)
        
        completed_tasks = [t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]
        total_completed = len(completed_tasks)
        
        if total_completed > 0:
            avg_completion = sum(t.completion_time_seconds for t in completed_tasks if t.completion_time_seconds) / total_completed
        else:
            avg_completion = 0.0
            
        throughput = (total_completed / duration) * 3600.0
        
        # Close any open wait times for calculation
        for r in self._robots.values():
            if r._last_wait_start is not None:
                r.total_waiting_time_seconds += (now - r._last_wait_start)
                r._last_wait_start = now  # Reset so subsequent calls don't double count
                
        num_robots = len(self._robots)
        if num_robots > 0:
            avg_wait = sum(r.total_waiting_time_seconds for r in self._robots.values()) / num_robots
        else:
            avg_wait = 0.0
            
        return PerformanceMetrics(
            total_tasks_completed=total_completed,
            total_collisions=self._total_collisions,
            average_task_completion_time=avg_completion,
            average_robot_waiting_time=avg_wait,
            throughput_tasks_per_hour=throughput,
            total_reroutes_successful=self._total_reroutes,
            total_network_recovery_events=self._total_network_recoveries,
            scenario_duration_seconds=duration
        )
