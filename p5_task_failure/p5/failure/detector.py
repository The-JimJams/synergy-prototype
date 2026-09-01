"""
P5 Failure Detector — Phase 10 Stub
=====================================

DEFERRED to Phase 10.

Future responsibility:
  Implement the FailureDetector protocol.  Compare the current UTC time
  against each robot's most recent heartbeat timestamp.

Timeout constants (to be confirmed in Phase 10):
  SUSPECT_TIMEOUT  = 3.0 seconds
  FAILURE_TIMEOUT  = 7.0 seconds

Detection algorithm (Phase 10):
  age = now_utc - latest_heartbeat.timestamp
  if age > FAILURE_TIMEOUT  -> classify as FAILED
  elif age > SUSPECT_TIMEOUT -> classify as SUSPECTED
  else                        -> classify as ALIVE
"""

from __future__ import annotations

from p5.models.heartbeat import HeartbeatStatus


from datetime import datetime, timedelta
from p5.models.robot import Robot, RobotStatus
from typing import Optional

class FailureDetector:
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout = timedelta(seconds=timeout_seconds)

    def detect(self, robot: Robot, heartbeat: Optional[Heartbeat], current_time: datetime) -> bool:
        if heartbeat is None:
            robot.status = RobotStatus.FAILED
            return True
            
        age = current_time - heartbeat.timestamp
        if age > self.timeout:
            robot.status = RobotStatus.FAILED
            return True
            
        return False
