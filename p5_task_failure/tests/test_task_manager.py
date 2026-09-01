import pytest
from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.manager.task_manager import TaskManager

def test_successful_task_allocation():
    robot_a = Robot("A", (0.0, 0.0), 100.0, 100.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",))
    robot_b = Robot("B", (10.0, 10.0), 100.0, 50.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",))
    task = Task("T01", (3.0, 4.0), (0.0, 0.0), 1, 10.0, 100.0, TaskStatus.AVAILABLE, None, ("CARRY",))
    
    manager = TaskManager()
    manager.allocate_task(task, [robot_a, robot_b])
    
    # 6. successful task allocation
    # 7. assigned robot becomes BUSY
    # 8. task stores assigned robot
    # 2. incapable robot does not get bid (Robot B has only 50 payload, task needs 100, so A wins)
    
    assert task.status == TaskStatus.ASSIGNED
    assert task.assigned_robot == "A"
    assert robot_a.status == RobotStatus.BUSY
    assert robot_a.current_task == "T01"
    
    assert robot_b.status == RobotStatus.AVAILABLE
    assert robot_b.current_task is None

def test_invalid_task_cannot_be_allocated():
    robot_a = Robot("A", (0.0, 0.0), 100.0, 100.0, None, 0, RobotStatus.AVAILABLE, ("CARRY",))
    task = Task("T01", (3.0, 4.0), (0.0, 0.0), 1, 10.0, 200.0, TaskStatus.AVAILABLE, None, ("CARRY",))
    
    manager = TaskManager()
    manager.allocate_task(task, [robot_a])
    
    # 9. invalid task cannot be allocated (payload too high)
    assert task.status == TaskStatus.AVAILABLE
    assert task.assigned_robot is None
    assert robot_a.status == RobotStatus.AVAILABLE
