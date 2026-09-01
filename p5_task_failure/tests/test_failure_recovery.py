import pytest
from datetime import datetime, timedelta, timezone
from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.models.heartbeat import Heartbeat, HeartbeatStatus
from p5.failure.detector import FailureDetector
from p5.recovery.task_recovery import TaskRecoveryManager
from p5.manager.task_manager import TaskManager

def test_heartbeat_detection():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    detector = FailureDetector(timeout_seconds=5.0)
    robot = Robot("A", (0, 0), 100, 100, None, 0, RobotStatus.AVAILABLE, ("CARRY",))
    
    # 1. recent heartbeat -> alive
    hb_recent = Heartbeat("A", now - timedelta(seconds=2), HeartbeatStatus.ALIVE)
    is_failed = detector.detect(robot, hb_recent, now)
    assert not is_failed
    assert robot.status == RobotStatus.AVAILABLE
    
    # 2. stale heartbeat -> failure
    # 3. failed robot gets FAILED status
    hb_stale = Heartbeat("A", now - timedelta(seconds=10), HeartbeatStatus.ALIVE)
    is_failed = detector.detect(robot, hb_stale, now)
    assert is_failed
    assert robot.status == RobotStatus.FAILED

def test_task_recovery_and_reassignment():
    task = Task("T01", (0,0), (0,0), 1, 10, 100, TaskStatus.ASSIGNED, "A", ("CARRY",))
    robot_a = Robot("A", (0,0), 100, 100, "T01", 1, RobotStatus.FAILED, ("CARRY",))
    robot_b = Robot("B", (1,1), 100, 100, None, 0, RobotStatus.AVAILABLE, ("CARRY",))
    
    recovery_manager = TaskRecoveryManager()
    recovery_manager.recover(task, robot_a)
    
    # 4. failed robot's task assignment is released
    assert task.assigned_robot is None
    assert task.status == TaskStatus.AVAILABLE
    assert robot_a.current_task is None
    assert robot_a.status == RobotStatus.FAILED  # Remains failed
    
    # Reallocation
    task_manager = TaskManager()
    task_manager.allocate_task(task, [robot_a, robot_b])
    
    # 5. failed robot does not receive a new bid (CapabilityChecker rejects FAILED)
    # 6. another robot can bid for recovered task
    # 7. recovered task gets reassigned
    # 8. new robot becomes BUSY
    # 9. recovered task stores new assigned robot
    
    assert task.status == TaskStatus.ASSIGNED
    assert task.assigned_robot == "B"
    assert robot_b.status == RobotStatus.BUSY
    assert robot_b.current_task == "T01"
    
    assert robot_a.status == RobotStatus.FAILED
    assert robot_a.current_task is None
