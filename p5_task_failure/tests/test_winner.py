import pytest
from datetime import datetime, timezone
from p5.models.bid import Bid
from p5.allocation.winner import WinnerSelector

def test_lower_score_wins():
    bids = [
        Bid("T01", "A", 10.0, 10.0, 10.0, 10.0, True, datetime.now(timezone.utc)),
        Bid("T01", "B", 5.0, 5.0, 5.0, 5.0, True, datetime.now(timezone.utc)),
    ]
    selector = WinnerSelector()
    winner = selector.select_winner(bids)
    assert winner is not None
    assert winner.robot_id == "B"

def test_deterministic_tie_breaking():
    bids = [
        Bid("T01", "B", 10.0, 10.0, 10.0, 10.0, True, datetime.now(timezone.utc)),
        Bid("T01", "A", 10.0, 10.0, 10.0, 10.0, True, datetime.now(timezone.utc)),
    ]
    selector = WinnerSelector()
    winner = selector.select_winner(bids)
    assert winner is not None
    assert winner.robot_id == "A"

def test_no_valid_bids_returns_none():
    bids = [
        Bid("T01", "A", 10.0, 10.0, 10.0, 10.0, False, datetime.now(timezone.utc)),
    ]
    selector = WinnerSelector()
    winner = selector.select_winner(bids)
    assert winner is None
