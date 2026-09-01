"""
State Reconciliation Data Model.
================================

Represents the audit report produced by ReconciliationManager during
post-partition state reconciliation across the multi-AMR fleet.

Zero ROS imports — pure dataclass.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ReconciliationReport:
    """Audit summary of state reconciliation performed during RECOVERY mode."""

    states_updated: int = 0
    intents_updated: int = 0
    conflicting_reservations_resolved: int = 0
    conflicting_tasks_resolved: int = 0
    stale_records_rejected: int = 0
    is_clean: bool = True
    reconciled_at: float = field(default_factory=time.time)

    def total_modifications(self) -> int:
        """Total number of state entities updated or resolved during reconciliation."""
        return (
            self.states_updated
            + self.intents_updated
            + self.conflicting_reservations_resolved
            + self.conflicting_tasks_resolved
        )

    def __repr__(self) -> str:
        return (
            f"ReconciliationReport(states_updated={self.states_updated}, "
            f"intents_updated={self.intents_updated}, "
            f"conflicting_res_resolved={self.conflicting_reservations_resolved}, "
            f"conflicting_tasks_resolved={self.conflicting_tasks_resolved}, "
            f"stale_rejected={self.stale_records_rejected}, clean={self.is_clean})"
        )
