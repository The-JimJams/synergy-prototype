"""
WorldModel — Local state store for a single robot's Fleet Coordination Agent.
=============================================================================

The WorldModel maintains a local, private view of known fleet states,
intents, reservations, and tasks.

CRITICAL ARCHITECTURAL PRINCIPLES:
1. Decentralized: Each robot has its own instance of WorldModel. There is NO
   central database or global source of truth.
2. Store & Query Only: The WorldModel contains NO decision logic (no conflict
   resolution, priority scoring, task auctioning, or deadlock detection).
3. ROS-free: Contains zero rclpy or ROS dependencies.
4. Monotonic State Ordering: Incoming peer updates with older or equal timestamps
   are rejected to preserve monotonic state and deterministic behavior.
5. Query-Time Correctness: Active queries dynamically filter expired records.
   Garbage collection via cleanup_expired() is an optional memory management
   utility and is never required for algorithmic correctness.
"""

from __future__ import annotations

from fleet_coordination.config.coordination_config import CoordinationConfig
from fleet_coordination.models.reservation import Reservation
from fleet_coordination.models.robot_intent import RobotIntent
from fleet_coordination.models.robot_state import RobotState
from fleet_coordination.models.task import Task


class WorldModel:
    """Local working memory and state repository for one AMR."""

    def __init__(
        self,
        robot_id: str,
        config: CoordinationConfig | None = None,
    ) -> None:
        """Initialize local WorldModel for a specific robot.

        Args:
            robot_id: The unique string identifier of this robot.
            config: Fleet coordination configuration. Defaults to CoordinationConfig().

        Raises:
            ValueError: If robot_id is empty.
        """
        if not robot_id:
            raise ValueError("WorldModel robot_id cannot be empty")

        self._robot_id: str = robot_id
        self._config: CoordinationConfig = config if config is not None else CoordinationConfig()

        # Local robot state & intent (strictly isolated from peer tables)
        self._own_state: RobotState | None = None
        self._own_intent: RobotIntent | None = None

        # Peer robot state & intent (keyed by robot_id)
        self._peer_states: dict[str, RobotState] = {}
        self._peer_intents: dict[str, RobotIntent] = {}

        # Shared resource reservations & fleet tasks
        self._reservations: dict[str, Reservation] = {}  # Key: claim_id
        self._tasks: dict[str, Task] = {}  # Key: task_id

    @property
    def robot_id(self) -> str:
        """The local robot ID owning this WorldModel."""
        return self._robot_id

    @property
    def config(self) -> CoordinationConfig:
        """Active coordination configuration."""
        return self._config

    # =========================================================================
    # 1. Own Robot State & Intent
    # =========================================================================

    def set_own_state(self, state: RobotState) -> None:
        """Set or update the local robot's state snapshot.

        Args:
            state: The RobotState representing this robot.

        Raises:
            ValueError: If state.robot_id does not match this WorldModel's robot_id,
                        or if state.robot_id is empty.
        """
        if not state.robot_id:
            raise ValueError("RobotState robot_id cannot be empty")
        if state.robot_id != self._robot_id:
            raise ValueError(
                f"Cannot set own state with mismatched ID: expected {self._robot_id!r}, "
                f"got {state.robot_id!r}"
            )
        self._own_state = state

    def get_own_state(self) -> RobotState | None:
        """Retrieve the local robot's state snapshot, or None if not set."""
        return self._own_state

    def set_own_intent(self, intent: RobotIntent) -> None:
        """Set or update the local robot's future planned intent.

        Args:
            intent: The RobotIntent representing this robot's plan.

        Raises:
            ValueError: If intent.robot_id does not match this WorldModel's robot_id,
                        or if intent.robot_id is empty.
        """
        if not intent.robot_id:
            raise ValueError("RobotIntent robot_id cannot be empty")
        if intent.robot_id != self._robot_id:
            raise ValueError(
                f"Cannot set own intent with mismatched ID: expected {self._robot_id!r}, "
                f"got {intent.robot_id!r}"
            )
        self._own_intent = intent

    def get_own_intent(self) -> RobotIntent | None:
        """Retrieve the local robot's future intent, or None if not set."""
        return self._own_intent

    # =========================================================================
    # 2. Peer Robot States
    # =========================================================================

    def update_peer_state(self, state: RobotState) -> bool:
        """Add or update a peer robot's state.

        Monotonic Ordering Policy:
        - Self-updates (state.robot_id == self.robot_id) are rejected.
        - Incoming timestamps <= stored timestamps are treated as non-newer
          updates and rejected to preserve monotonic state and deterministic behavior.
        - Incoming timestamps > stored timestamps (or first observation) are accepted.

        Args:
            state: Incoming peer RobotState.

        Returns:
            True if the state was accepted and updated, False if rejected.

        Raises:
            ValueError: If state.robot_id is empty or timestamp is negative.
        """
        if not state.robot_id:
            raise ValueError("RobotState robot_id cannot be empty")
        if state.timestamp < 0:
            raise ValueError("RobotState timestamp cannot be negative")

        # Reject self-telemetry arriving over peer channel
        if state.robot_id == self._robot_id:
            return False

        stored = self._peer_states.get(state.robot_id)
        if stored is not None and state.timestamp <= stored.timestamp:
            return False

        self._peer_states[state.robot_id] = state
        return True

    def get_peer_state(self, robot_id: str) -> RobotState | None:
        """Retrieve latest state for a peer robot, or None if unknown."""
        return self._peer_states.get(robot_id)

    def get_all_peer_states(self) -> dict[str, RobotState]:
        """Return a shallow copy of all known peer states."""
        return dict(self._peer_states)

    def get_fresh_peer_states(self, now: float) -> dict[str, RobotState]:
        """Return all peer states whose age <= peer_state_max_age_seconds at time 'now'.

        Args:
            now: Current reference time (Unix epoch seconds).
        """
        max_age = self._config.timeouts.peer_state_max_age_seconds
        return {
            rid: st for rid, st in self._peer_states.items() if st.age(now) <= max_age
        }

    def is_peer_state_fresh(self, robot_id: str, now: float) -> bool:
        """Check if a specific peer robot's state is fresh at time 'now'.

        Args:
            robot_id: Target peer ID.
            now: Current reference time.

        Returns:
            True if peer is known and age <= max_age; False otherwise.
        """
        st = self.get_peer_state(robot_id)
        if st is None:
            return False
        return st.age(now) <= self._config.timeouts.peer_state_max_age_seconds

    def get_known_peer_ids(self) -> set[str]:
        """Return a set of all registered peer robot IDs."""
        return set(self._peer_states.keys())

    def get_peer_count(self) -> int:
        """Return total count of known peers."""
        return len(self._peer_states)

    # =========================================================================
    # 3. Peer Robot Intents
    # =========================================================================

    def update_peer_intent(self, intent: RobotIntent) -> bool:
        """Add or update a peer robot's planned intent.

        Monotonic Ordering Policy:
        - Self-intents (intent.robot_id == self.robot_id) are rejected.
        - Incoming timestamps <= stored timestamps are rejected as non-newer.
        - Incoming timestamps > stored timestamps (or first observation) are accepted.
        - An intent is NOT rejected at store-time merely for being expired;
          expiry is evaluated at query time.

        Args:
            intent: Incoming peer RobotIntent.

        Returns:
            True if accepted and stored, False if rejected.

        Raises:
            ValueError: If intent.robot_id is empty or timestamp is negative.
        """
        if not intent.robot_id:
            raise ValueError("RobotIntent robot_id cannot be empty")
        if intent.timestamp < 0:
            raise ValueError("RobotIntent timestamp cannot be negative")

        # Reject self-intent arriving over peer channel
        if intent.robot_id == self._robot_id:
            return False

        stored = self._peer_intents.get(intent.robot_id)
        if stored is not None and intent.timestamp <= stored.timestamp:
            return False

        self._peer_intents[intent.robot_id] = intent
        return True

    def get_peer_intent(self, robot_id: str) -> RobotIntent | None:
        """Retrieve raw stored intent for a peer robot, or None if unknown."""
        return self._peer_intents.get(robot_id)

    def get_active_peer_intents(self, now: float) -> dict[str, RobotIntent]:
        """Return all peer intents that are NOT expired at time 'now'.

        Args:
            now: Current reference time (Unix epoch seconds).
        """
        return {
            rid: intent
            for rid, intent in self._peer_intents.items()
            if not intent.is_expired(now)
        }

    def get_intents_for_resource(
        self, resource_id: str, now: float
    ) -> list[RobotIntent]:
        """Return non-expired peer intents targeting the specified resource_id.

        Args:
            resource_id: Shared resource identifier (e.g. 'I1').
            now: Current reference time.
        """
        return [
            intent
            for intent in self._peer_intents.values()
            if intent.target_resource_id == resource_id and not intent.is_expired(now)
        ]

    # =========================================================================
    # 4. Reservations (Shared Resource Claims)
    # =========================================================================

    def add_reservation(self, reservation: Reservation) -> None:
        """Store or update a resource reservation by claim_id.

        Note: Duplicate claim_ids overwrite existing records. WorldModel does
        NOT perform conflict resolution or evaluate competing claims.

        Args:
            reservation: The Reservation object to store.

        Raises:
            ValueError: If claim_id is empty or end_time < start_time.
        """
        if not reservation.claim_id:
            raise ValueError("Reservation claim_id cannot be empty")
        if reservation.end_time < reservation.start_time:
            raise ValueError("Reservation end_time cannot be earlier than start_time")

        self._reservations[reservation.claim_id] = reservation

    def get_reservation(self, claim_id: str) -> Reservation | None:
        """Retrieve reservation by claim_id, or None if unknown."""
        return self._reservations.get(claim_id)

    def get_all_reservations(self) -> dict[str, Reservation]:
        """Return a shallow copy of all stored reservations."""
        return dict(self._reservations)

    def get_reservations_for_resource(
        self, resource_id: str, now: float
    ) -> list[Reservation]:
        """Return all non-expired reservations for the given resource_id.

        Args:
            resource_id: Target resource name (e.g. 'I1').
            now: Current reference time.
        """
        return [
            res
            for res in self._reservations.values()
            if res.resource_id == resource_id and not res.is_expired(now)
        ]

    def get_active_reservations(self, now: float) -> list[Reservation]:
        """Return all reservations currently active at time 'now'.

        Active is defined as: within [start_time, end_time] and not expired.

        Args:
            now: Current reference time.
        """
        return [res for res in self._reservations.values() if res.is_active(now)]

    def remove_reservation(self, claim_id: str) -> bool:
        """Remove/release a reservation by claim_id.

        Args:
            claim_id: Unique claim ID to remove.

        Returns:
            True if found and removed; False if claim_id was unknown.
        """
        if claim_id in self._reservations:
            del self._reservations[claim_id]
            return True
        return False

    # =========================================================================
    # 5. Tasks
    # =========================================================================

    def add_task(self, task: Task) -> None:
        """Store or update a task by task_id.

        Args:
            task: The Task object to store.

        Raises:
            ValueError: If task.task_id is empty.
        """
        if not task.task_id:
            raise ValueError("Task task_id cannot be empty")
        self._tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Task | None:
        """Retrieve task by task_id, or None if unknown."""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> dict[str, Task]:
        """Return a shallow copy of all known tasks."""
        return dict(self._tasks)

    def get_assignable_tasks(self) -> list[Task]:
        """Return all tasks eligible for bidding/assignment."""
        return [t for t in self._tasks.values() if t.is_assignable()]

    # =========================================================================
    # 6. Garbage Collection & Extension Points
    # =========================================================================

    def cleanup_expired(self, now: float) -> dict[str, int]:
        """Purge expired peer intents and reservations from storage.

        NOTE: This is strictly an optional memory-management utility. Correctness
        of all active query methods is independent of cleanup_expired() execution.

        Args:
            now: Reference time (Unix epoch seconds).

        Returns:
            Dictionary with counts: {"intents_removed": N, "reservations_removed": M}
        """
        expired_intent_keys = [
            k for k, v in self._peer_intents.items() if v.is_expired(now)
        ]
        for k in expired_intent_keys:
            del self._peer_intents[k]

        expired_res_keys = [
            k for k, v in self._reservations.items() if v.is_expired(now)
        ]
        for k in expired_res_keys:
            del self._reservations[k]

        return {
            "intents_removed": len(expired_intent_keys),
            "reservations_removed": len(expired_res_keys),
        }

    def update_obstacle(self, *args, **kwargs) -> None:
        """Extension point: placeholder for dynamic obstacle telemetry.

        Intentionally no-op until dynamic obstacle simulation format is defined.
        """
        pass
