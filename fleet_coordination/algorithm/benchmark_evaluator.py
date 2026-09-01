"""
BenchmarkEvaluator — Runs scenarios to calculate and compare performance metrics.
=================================================================================

Evaluates the SYNERGY coordination layer against a baseline stop-and-wait
algorithm to definitively prove >= 20% improvement.
"""

from __future__ import annotations
from typing import Callable

from fleet_coordination.algorithm.metrics_logger import MetricsLogger
from fleet_coordination.models.metrics import PerformanceMetrics


class BenchmarkEvaluator:
    """Evaluates coordination performance against a baseline."""

    def __init__(self, start_time: float = 1000.0, dt: float = 0.1) -> None:
        """Initialize the evaluator with a synthetic clock base.
        
        Args:
            start_time: Initial synthetic clock time.
            dt: Simulation timestep interval.
        """
        self.start_time = start_time
        self.dt = dt

    def evaluate_scenario(
        self,
        scenario_func: Callable[[MetricsLogger, bool, float, float], float],
        use_decentralized: bool
    ) -> PerformanceMetrics:
        """Run a deterministic scenario and return its metrics.
        
        Args:
            scenario_func: A callable of type (logger, use_decentralized, start_time, dt) -> final_time
            use_decentralized: True for SYNERGY, False for baseline STOP-AND-WAIT.
            
        Returns:
            Computed PerformanceMetrics for the run.
        """
        logger = MetricsLogger(start_time=self.start_time)
        final_time = scenario_func(logger, use_decentralized, self.start_time, self.dt)
        return logger.compute_metrics(final_time)

    def compare(
        self,
        baseline: PerformanceMetrics,
        decentralized: PerformanceMetrics
    ) -> dict[str, float]:
        """Compare decentralized metrics against baseline.
        
        Returns a dictionary of percentage improvements (or differences).
        Positive percentages indicate the decentralized approach performed better.
        """
        b_atct = baseline.average_task_completion_time
        d_atct = decentralized.average_task_completion_time
        
        if b_atct > 0 and baseline.total_tasks_completed > 0:
            atct_improvement = ((b_atct - d_atct) / b_atct) * 100.0
        elif baseline.total_tasks_completed == 0 and decentralized.total_tasks_completed > 0:
            # Baseline deadlocked, decentralized succeeded
            atct_improvement = 100.0
        else:
            atct_improvement = 0.0

        b_wait = baseline.average_robot_waiting_time
        d_wait = decentralized.average_robot_waiting_time
        if b_wait > 0:
            wait_improvement = ((b_wait - d_wait) / b_wait) * 100.0
        else:
            wait_improvement = 0.0

        b_tp = baseline.throughput_tasks_per_hour
        d_tp = decentralized.throughput_tasks_per_hour
        if b_tp > 0:
            tp_improvement = ((d_tp - b_tp) / b_tp) * 100.0
        elif b_tp == 0 and d_tp > 0:
            tp_improvement = 100.0
        else:
            tp_improvement = 0.0

        return {
            "atct_improvement_percent": atct_improvement,
            "wait_improvement_percent": wait_improvement,
            "throughput_improvement_percent": tp_improvement,
            "collisions_avoided": baseline.total_collisions - decentralized.total_collisions,
            "additional_tasks_completed": decentralized.total_tasks_completed - baseline.total_tasks_completed
        }

    def evaluate_improvement(
        self,
        baseline: PerformanceMetrics,
        decentralized: PerformanceMetrics
    ) -> bool:
        """Determine if the decentralized system meets the project success criteria.
        
        Criteria:
        - improvement_percent >= 20.0
        - decentralized_collisions == 0
        """
        if decentralized.total_collisions > 0:
            return False

        b_atct = baseline.average_task_completion_time
        d_atct = decentralized.average_task_completion_time
        
        if baseline.total_tasks_completed == 0 and decentralized.total_tasks_completed > 0:
            return True  # 100% improvement over deadlock
            
        if b_atct <= 0:
            return False
            
        improvement_percent = ((b_atct - d_atct) / b_atct) * 100.0
        
        # We need to account for floating point inaccuracies near exactly 20.0
        # e.g. 19.99999999999999
        return improvement_percent >= 19.9999
