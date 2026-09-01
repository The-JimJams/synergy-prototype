"""
Unit tests for BenchmarkEvaluator and Benchmark Scenarios.
"""
from __future__ import annotations

import pytest

from fleet_coordination.algorithm.benchmark_evaluator import BenchmarkEvaluator
from fleet_coordination.algorithm.metrics_logger import MetricsLogger
from fleet_coordination.models.metrics import PerformanceMetrics
from fleet_coordination.models.robot_state import RobotStatus
from fleet_coordination.models.task import TaskStatus


class TestBenchmarkEvaluator:
    
    def test_compare_and_improvement_exact_20_percent(self) -> None:
        evaluator = BenchmarkEvaluator()
        
        baseline = PerformanceMetrics(
            total_tasks_completed=10,
            total_collisions=0,
            average_task_completion_time=100.0,
            average_robot_waiting_time=50.0,
            throughput_tasks_per_hour=100.0,
            total_reroutes_successful=0,
            total_network_recovery_events=0,
            scenario_duration_seconds=360.0
        )
        
        # Exactly 20% improvement -> 80.0 ATCT
        decentralized_pass = PerformanceMetrics(
            total_tasks_completed=10,
            total_collisions=0,
            average_task_completion_time=80.0,
            average_robot_waiting_time=30.0,
            throughput_tasks_per_hour=125.0,
            total_reroutes_successful=0,
            total_network_recovery_events=0,
            scenario_duration_seconds=288.0
        )
        
        comp = evaluator.compare(baseline, decentralized_pass)
        assert comp["atct_improvement_percent"] == pytest.approx(20.0)
        assert evaluator.evaluate_improvement(baseline, decentralized_pass) is True

    def test_improvement_fails_at_19_percent(self) -> None:
        evaluator = BenchmarkEvaluator()
        
        baseline = PerformanceMetrics(
            total_tasks_completed=10, total_collisions=0,
            average_task_completion_time=100.0, average_robot_waiting_time=50.0,
            throughput_tasks_per_hour=100.0, total_reroutes_successful=0,
            total_network_recovery_events=0, scenario_duration_seconds=360.0
        )
        
        # 19% improvement -> 81.0 ATCT
        decentralized_fail = PerformanceMetrics(
            total_tasks_completed=10, total_collisions=0,
            average_task_completion_time=81.0, average_robot_waiting_time=40.0,
            throughput_tasks_per_hour=110.0, total_reroutes_successful=0,
            total_network_recovery_events=0, scenario_duration_seconds=300.0
        )
        
        comp = evaluator.compare(baseline, decentralized_fail)
        assert comp["atct_improvement_percent"] == pytest.approx(19.0)
        assert evaluator.evaluate_improvement(baseline, decentralized_fail) is False

    def test_zero_collision_safety_gate(self) -> None:
        evaluator = BenchmarkEvaluator()
        
        baseline = PerformanceMetrics(
            total_tasks_completed=10, total_collisions=0,
            average_task_completion_time=100.0, average_robot_waiting_time=50.0,
            throughput_tasks_per_hour=100.0, total_reroutes_successful=0,
            total_network_recovery_events=0, scenario_duration_seconds=360.0
        )
        
        # 50% improvement but 1 collision!
        decentralized_unsafe = PerformanceMetrics(
            total_tasks_completed=10, total_collisions=1,
            average_task_completion_time=50.0, average_robot_waiting_time=10.0,
            throughput_tasks_per_hour=200.0, total_reroutes_successful=0,
            total_network_recovery_events=0, scenario_duration_seconds=180.0
        )
        
        assert evaluator.evaluate_improvement(baseline, decentralized_unsafe) is False

    def test_deadlocked_baseline_is_100_percent_improvement(self) -> None:
        evaluator = BenchmarkEvaluator()
        
        # 0 tasks completed = deadlocked
        baseline = PerformanceMetrics(
            total_tasks_completed=0, total_collisions=0,
            average_task_completion_time=0.0, average_robot_waiting_time=500.0,
            throughput_tasks_per_hour=0.0, total_reroutes_successful=0,
            total_network_recovery_events=0, scenario_duration_seconds=600.0
        )
        
        decentralized = PerformanceMetrics(
            total_tasks_completed=5, total_collisions=0,
            average_task_completion_time=120.0, average_robot_waiting_time=20.0,
            throughput_tasks_per_hour=30.0, total_reroutes_successful=1,
            total_network_recovery_events=0, scenario_duration_seconds=600.0
        )
        
        comp = evaluator.compare(baseline, decentralized)
        assert comp["atct_improvement_percent"] == 100.0
        assert evaluator.evaluate_improvement(baseline, decentralized) is True

    def test_evaluate_scenario_deterministic_replay(self) -> None:
        evaluator = BenchmarkEvaluator(start_time=0.0, dt=0.1)
        
        def mock_scenario(logger: MetricsLogger, use_decentralized: bool, start: float, dt: float) -> float:
            now = start
            logger.log_task_status("t1", TaskStatus.ANNOUNCED, now)
            now += 5.0
            logger.log_task_status("t1", TaskStatus.IN_PROGRESS, now)
            
            if use_decentralized:
                now += 15.0 # fast
            else:
                now += 25.0 # slow
                
            logger.log_task_status("t1", TaskStatus.COMPLETED, now)
            return now
            
        b_metrics = evaluator.evaluate_scenario(mock_scenario, use_decentralized=False)
        d_metrics = evaluator.evaluate_scenario(mock_scenario, use_decentralized=True)
        
        assert b_metrics.average_task_completion_time == 30.0
        assert d_metrics.average_task_completion_time == 20.0
        
        # Replaying produces exact same
        b_metrics2 = evaluator.evaluate_scenario(mock_scenario, use_decentralized=False)
        assert b_metrics2.average_task_completion_time == 30.0
