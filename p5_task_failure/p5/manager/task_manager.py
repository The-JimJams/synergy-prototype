"""
P5 Task Manager — Phase 6 Stub
================================

DEFERRED to Phase 6.

Future responsibility:
  Implement the central P5 coordination loop (within-process only —
  NOT a centralised decision-making server).

  The TaskManager orchestrates the following in a decentralised way:
    - Receives task announcements from TaskSource.
    - For each task, asks each robot's local FleetAgent to calculate a bid.
    - Collects bids and passes them to WinnerSelector.
    - Publishes the assignment via EventSink.
    - Monitors heartbeats and triggers TaskRecoveryManager on failure.

  Decentralisation note:
    In the real distributed system, each robot runs its own FleetAgent.
    In standalone simulation, multiple FleetAgent instances run in a
    single Python process to allow testing without ROS 2.
"""

from __future__ import annotations


class TaskManager:
    """Coordinates the full P5 allocation and failure recovery cycle.

    Phase 1: Stub only — raises NotImplementedError.
    Phase 6: Will implement the task state machine and coordination loop.
    """

    def run_once(self) -> None:
        """Execute one cycle of the task allocation loop.

        Raises
        ------
        NotImplementedError
            Always in Phase 1. Will be implemented in Phase 6.
        """
        raise NotImplementedError(
            "TaskManager.run_once() is deferred to Phase 6."
        )
