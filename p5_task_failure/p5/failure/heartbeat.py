"""
P5 Heartbeat Monitor — Phase 9 Stub
=====================================

DEFERRED to Phase 9.

Future responsibility:
  Maintain a registry of the most recent Heartbeat received from each
  robot.  On each tick, update the registry and classify each robot's
  health status (ALIVE / SUSPECTED / FAILED / RECOVERED).

Design outline (Phase 9):
  - HeartbeatMonitor.register(heartbeat: Heartbeat) -> None
  - HeartbeatMonitor.get_latest(robot_id: str) -> Optional[Heartbeat]
  - HeartbeatMonitor.get_all() -> List[Heartbeat]
  - Internal dict: {robot_id: Heartbeat}
"""

from __future__ import annotations

from typing import Dict, List, Optional

from p5.models.heartbeat import Heartbeat


class HeartbeatMonitor:
    """Maintains the latest heartbeat for each robot.

    Phase 1: Stub only — methods raise NotImplementedError.
    Phase 9: Will implement HeartbeatSource protocol.
    """

    def register(self, heartbeat: Heartbeat) -> None:
        """Record an incoming heartbeat.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 9.
        """
        raise NotImplementedError(
            "HeartbeatMonitor.register() is deferred to Phase 9."
        )

    def get_latest(self, robot_id: str) -> Optional[Heartbeat]:
        """Return the most recent heartbeat from the robot.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 9.
        """
        raise NotImplementedError(
            "HeartbeatMonitor.get_latest() is deferred to Phase 9."
        )

    def get_all(self) -> List[Heartbeat]:
        """Return the most recent heartbeat for every known robot.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 9.
        """
        raise NotImplementedError(
            "HeartbeatMonitor.get_all() is deferred to Phase 9."
        )
