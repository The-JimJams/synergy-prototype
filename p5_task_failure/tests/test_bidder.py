import pytest
from datetime import datetime, timezone
from p5.models.robot import Robot, RobotStatus
from p5.models.task import Task, TaskStatus
from p5.allocation.bidder import Bidder

def test_bidder_creates_bid():
    robot = Robot(
        robot_id="A",
        position=(0.0, 0.0),
        battery=100.0,
        payload_capacity=100.0,
        current_task=None,
        workload=0,
        status=RobotStatus.AVAILABLE,
        capabilities=("CARRY",)
    )
    task = Task(
        task_id="T01",
        pickup_location=(3.0, 4.0),
        dropoff_location=(0.0, 0.0),
        priority=1,
        deadline=10.0,
        required_payload=50.0,
        status=TaskStatus.AVAILABLE,
        assigned_robot=None,
        required_capabilities=("CARRY",)
    )
    bidder = Bidder()
    bid = bidder.create_bid(robot, task)
    
    assert bid.robot_id == "A"
    assert bid.task_id == "T01"
    assert bid.distance == 5.0  # sqrt(3^2 + 4^2)
    assert bid.valid == True
    assert bid.score > 0
