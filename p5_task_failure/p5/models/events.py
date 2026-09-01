"""
P5 Internal Events
==================

Defines the internal event vocabulary used within the P5 subsystem.

Phase 1: Enumeration and data structure only.
Future:  These events will be published to the EventSink adapter so that
         external systems (ROS 2 topics, dashboards, logging) can observe
         P5 state changes without coupling to P5 internals.

Design note
-----------
P5 events are internal signals.  They are NOT ROS 2 messages.
A future ROS 2 adapter will translate P5Events into appropriate
ROS 2 topic publications without changing any core P5 logic.
"""

from __future__ import annotations

import enum
import dataclasses
from datetime import datetime
from typing import Any, Optional


class P5EventType(enum.Enum):
    """All internal P5 event types.

    Each event corresponds to a meaningful state transition or observation
    within the P5 subsystem.

    Mapping to future integration (Phase 7):
        TASK_ANNOUNCED   -> publish on /p5/task_announcements
        BID_SUBMITTED    -> publish on /p5/bids
        TASK_ASSIGNED    -> publish on /p5/assignments
        TASK_STARTED     -> publish on /p5/task_started
        TASK_COMPLETED   -> publish on /p5/task_completed
        TASK_RELEASED    -> publish on /p5/task_released  (failure path)
        TASK_REASSIGNED  -> publish on /p5/reassignments
        ROBOT_FAILED     -> publish on /p5/robot_failed
        ROBOT_RECOVERED  -> publish on /p5/robot_recovered
    """

    TASK_ANNOUNCED = "TASK_ANNOUNCED"
    BID_SUBMITTED = "BID_SUBMITTED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_RELEASED = "TASK_RELEASED"
    TASK_REASSIGNED = "TASK_REASSIGNED"
    ROBOT_FAILED = "ROBOT_FAILED"
    ROBOT_RECOVERED = "ROBOT_RECOVERED"


@dataclasses.dataclass(frozen=True)
class P5Event:
    """Immutable internal P5 event.

    Attributes
    ----------
    event_type : P5EventType
        The kind of event that occurred.
    timestamp : datetime
        UTC time when the event was created.
    source_robot : Optional[str]
        The robot_id that triggered the event, if applicable.
    task_id : Optional[str]
        The task_id this event relates to, if applicable.
    payload : Optional[Any]
        Additional structured data (e.g. Bid object, score).
        Must be serialisable — no ROS 2 objects should appear here.

    Example
    -------
    >>> from datetime import datetime, timezone
    >>> e = P5Event(
    ...     event_type=P5EventType.TASK_ANNOUNCED,
    ...     timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ...     source_robot=None,
    ...     task_id="T01",
    ...     payload=None,
    ... )
    """

    event_type: P5EventType
    timestamp: datetime
    source_robot: Optional[str]
    task_id: Optional[str]
    payload: Optional[Any]

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%H:%M:%SZ")
        parts = [f"P5Event({self.event_type.value}", f"t={ts}"]
        if self.source_robot:
            parts.append(f"robot={self.source_robot!r}")
        if self.task_id:
            parts.append(f"task={self.task_id!r}")
        return ", ".join(parts) + ")"
