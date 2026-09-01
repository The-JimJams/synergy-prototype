"""
Tests for metrics.py and event_logger.py — Phase 12 & 13 verification.

Covers:
- Improvement percentage calculation formula
- Event sequence metrics computation
- Aggregate metrics computation across repeated runs
- CSV experiment logging without overwriting
- JSON/JSONL event export
"""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import ExperimentMetrics
from metrics import (
    calculate_improvement_percent,
    compute_run_metrics,
    compute_aggregate_metrics,
    ExperimentLogger,
)
from event_logger import EventAuditLogger


def test_improvement_percentage_formula():
    # Baseline = 100.2, Proposed = 78.4 -> Improvement = 21.756... -> ~21.8%
    imp = calculate_improvement_percent(100.2, 78.4)
    assert round(imp, 1) == 21.8

    # Edge cases
    assert calculate_improvement_percent(0, 50) == 0.0
    assert calculate_improvement_percent(-10, 50) == 0.0


def test_compute_run_metrics():
    events = [
        {"event_type": "INFO", "timestamp": "2026-01-01T00:00:00+00:00"},
        {"event_type": "CONFLICT", "timestamp": "2026-01-01T00:00:10+00:00"},
        {"event_type": "WAIT", "message": "B waiting for I1 (2.0s)", "timestamp": "2026-01-01T00:00:12+00:00"},
        {"event_type": "TASK_COMPLETED", "timestamp": "2026-01-01T00:01:18.4+00:00"},
    ]

    metrics = compute_run_metrics(events, mode="proposed", scenario="conflict")
    assert metrics.mode == "proposed"
    assert metrics.scenario == "conflict"
    assert metrics.tasks_completed == 1
    assert metrics.total_task_time == 78.4


def test_compute_aggregate_metrics():
    runs = [
        ExperimentMetrics(mode="proposed", total_task_time=80.0, average_wait_time=8.0, tasks_completed=3),
        ExperimentMetrics(mode="proposed", total_task_time=70.0, average_wait_time=6.0, tasks_completed=3),
    ]

    agg = compute_aggregate_metrics(runs)
    assert agg["count"] == 2
    assert agg["avg_total_time"] == 75.0
    assert agg["avg_wait_time"] == 7.0
    assert agg["total_tasks_completed"] == 6


def test_csv_experiment_logger():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ExperimentLogger(csv_dir=tmpdir)
        m1 = ExperimentMetrics(run_id="run1", mode="baseline", total_task_time=100.2)
        m2 = ExperimentMetrics(run_id="run2", mode="proposed", total_task_time=78.4)

        logger.log_run(m1)
        logger.log_run(m2)

        runs = logger.load_runs()
        assert len(runs) == 2
        assert runs[0].run_id == "run1"
        assert runs[0].mode == "baseline"
        assert runs[1].run_id == "run2"
        assert runs[1].mode == "proposed"


def test_event_audit_logger():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = EventAuditLogger(events_dir=tmpdir)
        events = [{"event_type": "CONFLICT", "message": "Conflict at I1"}]

        json_file = logger.export_json(events, "test_run")
        jsonl_file = logger.export_jsonl(events, "test_run")

        assert os.path.exists(json_file)
        assert os.path.exists(jsonl_file)
