"""
P5 Heartbeat Model
==================

Represents a single heartbeat signal from a robot.

Phase 1: Data structure and failure status enumeration only.
Phase 9: HeartbeatMonitor will send periodic heartbeats.
Phase 10: FailureDetector will compare timestamps to detect timeouts.

Design note
-----------
The heartbeat is modelled as an immutable snapshot.  The monitor (Phase 9)
will maintain a mutable registry mapping robot_id -> latest Heartbeat.
The detector (Phase 10) will compare datetime.now(UTC) against the
latest timestamp to classify each robot's health status.
"""

from __future__ import annotations

import enum
import dataclasses
from datetime import datetime


class HeartbeatStatus(enum.Enum):
    """Health classification of a robot as assessed by P5 failure detection.

    Transitions (to be enforced in Phase 10):

        ALIVE
         |
         v  (timeout threshold 1 exceeded)
        SUSPECTED
         |
         v  (timeout threshold 2 exceeded)
        FAILED
         |
         v  (robot reconnects)
        RECOVERED
         |
         v  (confirmed operational)
        ALIVE
    """

    ALIVE = "ALIVE"
    SUSPECTED = "SUSPECTED"
    FAILED = "FAILED"
    RECOVERED = "RECOVERED"


@dataclasses.dataclass(frozen=True)
class Heartbeat:
    """Immutable snapshot of a single heartbeat message from a robot.

    Attributes
    ----------
    robot_id : str
        The robot that sent this heartbeat.
    timestamp : datetime
        UTC timestamp when the heartbeat was produced.
    status : HeartbeatStatus
        The health classification reported (or inferred) at this moment.

    Note: ``frozen=True`` ensures heartbeats are immutable records.
    The FailureDetector creates new Heartbeat instances rather than
    mutating existing ones.

    Example
    -------
    >>> from datetime import datetime, timezone
    >>> hb = Heartbeat(
    ...     robot_id="A",
    ...     timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    ...     status=HeartbeatStatus.ALIVE,
    ... )
    """

    robot_id: str
    timestamp: datetime
    status: HeartbeatStatus

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"Heartbeat({self.robot_id!r}, {ts}, {self.status.value})"
