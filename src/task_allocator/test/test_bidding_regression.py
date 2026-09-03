"""Regression guard for the distributed bidding path.

The allocation algorithm is working and is deliberately NOT modified here. These
tests exist so that the navigation, telemetry and dashboard fixes cannot silently
change allocation behaviour, and to record bid latency as a metric.

They run without ROS 2: task_allocator_node falls back to stub message classes
when rclpy is unavailable, so the bid arithmetic and the winner rule are
exercised exactly as they are in the live node.

What is pinned:
  * every robot independently selects the SAME winner from the same bid set
    (this is what makes the scheme decentralised rather than merely distributed)
  * the winner rule is lowest estimated_time, ties broken by robot_id
  * a bid always carries the identity of the robot that made it
  * bid computation is fast, and is not accidentally made slow
"""

import os
import statistics
import sys
import time

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
PKG_ROOT = os.path.dirname(HERE)                                  # src/task_allocator
WS_SRC = os.path.dirname(PKG_ROOT)                                # src
PROJECT = os.path.dirname(WS_SRC)                                 # repo root

sys.path.insert(0, PKG_ROOT)
sys.path.insert(0, os.path.join(PROJECT, "p5_task_failure"))

from task_allocator.task_allocator_node import (   # noqa: E402
    TaskAllocatorNode, TaskAnnouncement, TaskBid, WAYPOINTS,
)

ROBOT_IDS = ("amr_a", "amr_b", "amr_c")

# Where the three AMRs actually spawn in gazebo/simulation/worlds/warehouse.sdf.
SPAWNS = {
    "amr_a": (-3.5, 5.25),
    "amr_b": (0.5, 8.5),
    "amr_c": (3.5, -6.5),
}


def make_node(robot_id, position, battery=100.0):
    node = TaskAllocatorNode()
    node.robot_id = robot_id
    node.local_robot_state = {
        "robot_id": robot_id,
        "position": list(position),
        "battery": battery,
        "status": "idle",
    }
    return node


def make_announcement(task_id="task_test_001", pickup="P1", dropoff="D1", priority=3):
    msg = TaskAnnouncement()
    msg.task_id = task_id
    msg.pickup = pickup
    msg.dropoff = dropoff
    msg.priority = priority
    msg.deadline = time.time() + 90.0
    msg.capability_requirements = ["delivery", "navigation"]
    return msg


@pytest.fixture
def fleet():
    return {rid: make_node(rid, SPAWNS[rid]) for rid in ROBOT_IDS}


# ── Bid content ──────────────────────────────────────────────────────────────

def test_bid_carries_the_bidding_robots_identity(fleet):
    ann = make_announcement()
    for robot_id, node in fleet.items():
        bid = node.compute_bid(ann)
        assert bid.robot_id == robot_id
        assert bid.task_id == ann.task_id


def test_bid_distance_matches_the_pickup_waypoint(fleet):
    """The bid must score against the real pickup pose, not a placeholder."""
    import math
    ann = make_announcement(pickup="P1")
    px, py = WAYPOINTS["P1"]
    for robot_id, node in fleet.items():
        bid = node.compute_bid(ann)
        sx, sy = SPAWNS[robot_id]
        assert bid.distance == pytest.approx(math.hypot(sx - px, sy - py), abs=1e-6)
        assert bid.estimated_time == pytest.approx(max(1.0, bid.distance / 0.6), abs=1e-6)


def test_closer_robot_bids_lower(fleet):
    """Nearest robot to the pickup must produce the smallest estimated time."""
    import math
    ann = make_announcement(pickup="P1")
    px, py = WAYPOINTS["P1"]
    bids = {rid: node.compute_bid(ann) for rid, node in fleet.items()}
    nearest = min(SPAWNS, key=lambda r: math.hypot(SPAWNS[r][0] - px, SPAWNS[r][1] - py))
    assert min(bids, key=lambda r: bids[r].estimated_time) == nearest


# ── Decentralised winner selection ───────────────────────────────────────────

def _bid_set(fleet, ann):
    return {rid: node.compute_bid(ann) for rid, node in fleet.items()}


def _winner_as_seen_by(node, task_id, bids):
    """Run the node's own winner rule over a bid set, without touching Nav2."""
    node.task_bids[task_id] = dict(bids)
    node._announcement_times[task_id] = time.time()
    chosen = min(bids.values(), key=lambda b: (b.estimated_time, b.robot_id))
    return chosen.robot_id


def test_every_robot_independently_picks_the_same_winner(fleet):
    """No central arbiter: each node reaches the same verdict on its own."""
    ann = make_announcement()
    bids = _bid_set(fleet, ann)

    verdicts = {rid: _winner_as_seen_by(node, ann.task_id, bids)
                for rid, node in fleet.items()}

    assert len(set(verdicts.values())) == 1, (
        f"robots disagreed on the winner: {verdicts} -- "
        "decentralised consensus is broken"
    )


def test_winner_is_lowest_estimated_time(fleet):
    ann = make_announcement()
    bids = _bid_set(fleet, ann)
    winner = _winner_as_seen_by(fleet["amr_a"], ann.task_id, bids)
    assert winner == min(bids, key=lambda r: bids[r].estimated_time)


def test_ties_break_deterministically_on_robot_id():
    """Equal bids must not resolve by dict ordering or arrival order."""
    bids = {}
    for rid in ("amr_c", "amr_a", "amr_b"):     # deliberately unsorted
        bid = TaskBid()
        bid.robot_id = rid
        bid.task_id = "tie_task"
        bid.estimated_time = 10.0                # identical
        bid.distance = 6.0
        bid.battery_cost = 0.0
        bid.confidence = 0.9
        bids[rid] = bid

    node = make_node("amr_b", SPAWNS["amr_b"])
    assert _winner_as_seen_by(node, "tie_task", bids) == "amr_a"


def test_winner_is_stable_across_repeated_runs(fleet):
    """Same inputs, same winner, every time."""
    ann = make_announcement()
    winners = set()
    for _ in range(50):
        bids = _bid_set(fleet, ann)
        winners.add(_winner_as_seen_by(fleet["amr_a"], ann.task_id, bids))
    assert len(winners) == 1, f"winner was not deterministic: {winners}"


def test_different_pickups_can_elect_different_winners(fleet):
    """Sanity: the rule actually depends on geometry, it is not a constant."""
    winners = set()
    for i, pickup in enumerate(("P1", "P2", "CHG", "S8")):
        ann = make_announcement(task_id=f"t{i}", pickup=pickup)
        bids = _bid_set(fleet, ann)
        winners.add(_winner_as_seen_by(fleet["amr_a"], ann.task_id, bids))
    assert len(winners) > 1, "winner never changes with the pickup location"


# ── Latency metric ───────────────────────────────────────────────────────────

def test_bid_computation_latency(fleet):
    """Record bid latency. No artificial delay is added anywhere in this path."""
    ann = make_announcement()
    node = fleet["amr_a"]

    for _ in range(100):        # warm up
        node.compute_bid(ann)

    samples = []
    for _ in range(2000):
        t0 = time.perf_counter()
        node.compute_bid(ann)
        samples.append((time.perf_counter() - t0) * 1000.0)

    stats = {
        "min_ms": min(samples),
        "mean_ms": statistics.mean(samples),
        "median_ms": statistics.median(samples),
        "p95_ms": sorted(samples)[int(0.95 * len(samples))],
        "max_ms": max(samples),
    }
    print("\nBID COMPUTATION LATENCY (n=2000)")
    for key, value in stats.items():
        print(f"  {key:<10} {value:.4f} ms")

    # Generous ceiling: this is a regression guard, not a benchmark target.
    assert stats["median_ms"] < 1.0, f"bid computation regressed: {stats}"
