"""
Unit tests for MetricsLogger.
"""
from __future__ import annotations

import math
import pytest

from fleet_coordination.algorithm.metrics_logger import MetricsLogger
from fleet_coordination.models.robot_state import RobotStatus
from fleet_coordination.models.task import TaskStatus


class TestMetricsLogger:
    
    def test_empty_logger_returns_zeros(self) -> None:
        logger = MetricsLogger(start_time=100.0)
        metrics = logger.compute_metrics(now=110.0)
        assert metrics.total_tasks_completed == 0
        assert metrics.total_collisions == 0
        assert metrics.average_task_completion_time == 0.0
        assert metrics.average_robot_waiting_time == 0.0
        assert metrics.throughput_tasks_per_hour == 0.0
        assert metrics.total_reroutes_successful == 0
        assert metrics.total_network_recovery_events == 0
        assert metrics.scenario_duration_seconds == 10.0

    def test_single_task_completion(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        logger.log_task_status("t1", TaskStatus.ANNOUNCED, now=5.0)
        logger.log_task_status("t1", TaskStatus.IN_PROGRESS, now=10.0)
        logger.log_task_status("t1", TaskStatus.COMPLETED, now=25.0)
        
        metrics = logger.compute_metrics(now=30.0)
        assert metrics.total_tasks_completed == 1
        assert metrics.average_task_completion_time == 20.0  # 25 - 5
        assert metrics.throughput_tasks_per_hour == (1 / 30.0) * 3600.0

    def test_multiple_tasks_and_incomplete(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        
        logger.log_task_status("t1", TaskStatus.ANNOUNCED, now=10.0)
        logger.log_task_status("t2", TaskStatus.ANNOUNCED, now=15.0)
        logger.log_task_status("t3", TaskStatus.ANNOUNCED, now=20.0)
        
        logger.log_task_status("t1", TaskStatus.COMPLETED, now=30.0) # took 20s
        logger.log_task_status("t2", TaskStatus.COMPLETED, now=45.0) # took 30s
        logger.log_task_status("t3", TaskStatus.IN_PROGRESS, now=50.0) # incomplete
        
        metrics = logger.compute_metrics(now=60.0)
        assert metrics.total_tasks_completed == 2
        assert metrics.average_task_completion_time == 25.0  # (20 + 30) / 2
        assert metrics.throughput_tasks_per_hour == (2 / 60.0) * 3600.0

    def test_robot_waiting_time(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        
        # AMR 1 waits from 10 to 20
        logger.log_robot_status("amr_1", RobotStatus.NAVIGATING, now=5.0)
        logger.log_robot_status("amr_1", RobotStatus.WAITING, now=10.0)
        logger.log_robot_status("amr_1", RobotStatus.NAVIGATING, now=20.0)
        
        # AMR 2 waits from 15 to 35 (20s). Duplicate WAITING events ignored.
        logger.log_robot_status("amr_2", RobotStatus.WAITING, now=15.0)
        logger.log_robot_status("amr_2", RobotStatus.WAITING, now=20.0)
        logger.log_robot_status("amr_2", RobotStatus.NAVIGATING, now=35.0)
        
        metrics = logger.compute_metrics(now=40.0)
        assert metrics.average_robot_waiting_time == 15.0  # (10 + 20) / 2

    def test_open_wait_closed_on_compute(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        
        # Wait starts at 10, scenario ends at 50 while still waiting
        logger.log_robot_status("amr_1", RobotStatus.WAITING, now=10.0)
        metrics = logger.compute_metrics(now=50.0)
        
        assert metrics.average_robot_waiting_time == 40.0

    def test_collision_and_other_counters(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        logger.log_collision("amr_1", "amr_2", now=5.0)
        logger.log_collision("amr_2", "amr_3", now=15.0)
        logger.log_reroute_success("amr_1", now=10.0)
        logger.log_network_recovery(now=25.0)
        
        metrics = logger.compute_metrics(now=30.0)
        assert metrics.total_collisions == 2
        assert metrics.total_reroutes_successful == 1
        assert metrics.total_network_recovery_events == 1

    def test_invalid_timestamps(self) -> None:
        logger = MetricsLogger(start_time=0.0)
        
        with pytest.raises(ValueError):
            logger.log_task_status("t1", TaskStatus.ANNOUNCED, now=-5.0)
            
        with pytest.raises(ValueError):
            logger.log_robot_status("r1", RobotStatus.WAITING, now=float("nan"))
            
        with pytest.raises(ValueError):
            logger.compute_metrics(now=float("inf"))
