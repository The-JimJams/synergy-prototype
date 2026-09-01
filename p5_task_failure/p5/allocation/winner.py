"""
P5 Winner Selector — Phase 5 Stub
===================================

DEFERRED to Phase 5.

Future responsibility:
  Implement the WinnerSelector protocol.  Given a list of Bid objects,
  deterministically select the single best bid.

Determinism requirement:
  The algorithm must always select the same winner for the same input.
  No randomness, no timestamp-dependent tie-breaking.

Algorithm outline (Phase 5):
  1. Filter bids: keep only bid.valid == True.
  2. Sort by bid.score descending.
  3. Tie-break by robot_id (lexicographic ascending) for determinism.
  4. Return the first bid, or None if no valid bids.
"""

from __future__ import annotations

from typing import List, Optional

from p5.models.bid import Bid


class WinnerSelector:
    def select_winner(self, bids: List[Bid]) -> Optional[Bid]:
        valid_bids = [b for b in bids if b.valid]
        if not valid_bids:
            return None
            
        valid_bids.sort(key=lambda b: (b.score, b.robot_id))
        return valid_bids[0]
