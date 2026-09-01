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
    def __init__(self):
        self._registry: Dict[str, Heartbeat] = {}

    def register(self, heartbeat: Heartbeat) -> None:
        self._registry[heartbeat.robot_id] = heartbeat

    def get_latest(self, robot_id: str) -> Optional[Heartbeat]:
        return self._registry.get(robot_id)

    def get_all(self) -> List[Heartbeat]:
        return list(self._registry.values())
