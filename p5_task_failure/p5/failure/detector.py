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


class FailureDetector:
    """Detects robot failures based on heartbeat timing.

    Phase 1: Stub only — methods raise NotImplementedError.
    Phase 10: Will implement FailureDetector protocol.
    """

    def is_failed(self, robot_id: str) -> bool:
        """Return True if the robot is classified as FAILED.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 10.
        """
        raise NotImplementedError(
            "FailureDetector.is_failed() is deferred to Phase 10."
        )

    def is_suspected(self, robot_id: str) -> bool:
        """Return True if the robot is classified as SUSPECTED.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 10.
        """
        raise NotImplementedError(
            "FailureDetector.is_suspected() is deferred to Phase 10."
        )

    def classify(self, robot_id: str) -> HeartbeatStatus:
        """Return the full HeartbeatStatus classification for the robot.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 10.
        """
        raise NotImplementedError(
            "FailureDetector.classify() is deferred to Phase 10."
        )
