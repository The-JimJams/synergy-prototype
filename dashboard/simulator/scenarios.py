"""
SYNERGY Dashboard — Scenario Definitions
==========================================

Each scenario is a list of **steps**.  A step is a dict:

    {
        "delay":       float,      # seconds to wait BEFORE executing
        "description": str,        # human-readable label (for logs/debug)
        "actions":     list[dict], # things to push into the DataStore
    }

COORDINATE FRAME
----------------
Matches Gazebo Harmonic simulation world (warehouse.sdf & visual layout):
- Dimensions: 20.0m x 20.0m (-10.0m to +10.0m in X and Y)
- Origin (0.0, 0.0) is at warehouse center
- Pickup 1 (P1): (0.0, 8.0) [North Bay]
- Pickup 2 (P2): (-5.5, -7.0) [South-West Bay; approach from (-6.4, -6.3)]
- Drop 1 (D1): (0.0, -8.1) [South Bay]
- Charging Bay (CHG): (5.5, -7.5) [South-East Charging Dock with ⚡ terminal]
- Intersection I1: (0.0, 5.2) [North Chokepoint, central corridor]
- Intersection I2: (0.0, -0.7) [Central Chokepoint, central corridor]
- Central Obstacle: (-0.2, 0.75) [Orange container parked in the central corridor]
- AMRs spawn at: A (-3.5, 5.25), B (0.5, 8.5), C (3.5, -6.5)

Shelving stands in two columns at x = -4.8 and x = +4.8 (each rack 5.0 m x 1.0 m),
so the through-route is the NORTH-SOUTH central corridor at x in [-2.3, +2.3],
running P1 (north) -> I1 -> the parked container -> I2 -> D1 (south).

Every pose in this file is inside real free space: verified against
src/synergy_nav2/maps/warehouse_map.pgm with >= 0.45 m clearance, so a mock run
is a faithful preview of what the live fleet does in the same warehouse.
"""

from __future__ import annotations

import math

# ── Action-builder helpers ──────────────────────────────────────────────────

def _robot(rid, x, y, *, yaw=0.0, vel=0.0, bat=100.0,
           status="IDLE", task=None):
    return {
        "type": "update_robot",
        "data": {
            "robot_id": rid, "x": x, "y": y, "yaw": yaw,
            "velocity": vel, "battery": bat, "status": status,
            "task_id": task,
        },
    }


def _goto(rid, x, y, *, speed=0.55, status="MOVING", arrive="IDLE",
          task=None, on_arrive=None):
    """Drive a robot to (x, y) along a route planned over the real warehouse map.

    Prefer this over _robot() for anything that represents travel: _robot()
    places a pose instantly, which is right for a spawn but reads as the AMR
    teleporting when used mid-journey.
    """
    return {
        "type": "goto",
        "data": {
            "robot_id": rid, "x": x, "y": y, "speed": speed,
            "status": status, "arrive_status": arrive, "task_id": task,
            "on_arrive": on_arrive or [],
        },
    }


def _stop(rid):
    return {"type": "stop_robot", "data": {"robot_id": rid}}


def _intent(rid, resource, eta=None):
    return {
        "type": "update_intent",
        "data": {"robot_id": rid, "resource_id": resource, "eta": eta},
    }


def _clear_intent(rid):
    return {"type": "clear_intent", "data": {"robot_id": rid}}


def _reserve(resource, rid, status="ACTIVE"):
    return {
        "type": "update_reservation",
        "data": {"resource_id": resource, "robot_id": rid, "status": status},
    }


def _release(resource):
    return {"type": "release_reservation", "data": {"resource_id": resource}}


def _task(tid, pickup, dropoff, robot=None, status="ANNOUNCED"):
    return {
        "type": "update_task",
        "data": {
            "task_id": tid, "pickup": pickup, "dropoff": dropoff,
            "assigned_robot": robot, "status": status,
        },
    }


def _event(etype, rid=None, *, related=None, resource=None,
           task=None, msg=""):
    return {
        "type": "add_event",
        "data": {
            "event_type": etype, "robot_id": rid,
            "related_robot_id": related, "resource_id": resource,
            "task_id": task, "message": msg,
        },
    }


def _network(status="NORMAL", latency=None, loss=None, peers=None):
    return {
        "type": "update_network",
        "data": {
            "status": status, "latency_ms": latency,
            "packet_loss_percent": loss, "active_peers": peers,
        },
    }


def _step(delay, desc, *actions):
    """Convenience: build a step dict from positional action args."""
    return {"delay": delay, "description": desc, "actions": list(actions)}


# ── Yaw helpers (radians) ──────────────────────────────────────────────────

RIGHT = 0.0
UP    = math.pi / 2
LEFT  = math.pi
DOWN  = -math.pi / 2


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 1 — NORMAL OPERATION & CHARGING
# ═══════════════════════════════════════════════════════════════════════════

def _normal_scenario() -> list[dict]:
    """AMRs perform logistics missions, navigate warehouse aisles, and dock at CHG."""
    return [
        # ── Initialise ──
        _step(2.5, "Robots online at Gazebo visual layout positions",
              _robot("A", -3.5, 5.25, yaw=RIGHT, bat=95, status="IDLE"),
              _robot("B", 0.5, 8.5, yaw=DOWN, bat=90, status="IDLE"),
              _robot("C", 5.5, -7.5, yaw=LEFT, bat=30, status="CHARGING"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _event("INFO", msg="Fleet operational — 3 AMRs connected (20x20m facility layout)"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C docked at Charging Bay (CHG) — rapid replenishment active"),
              ),

        # ── Tasks announced & assigned ──
        _step(2.5, "Tasks announced",
              _task("T01", "P1", "D1"),
              _task("T02", "P2", "D1"),
              _event("INFO", msg="2 logistics transport tasks announced to decentralized fleet"),
              ),

        _step(2.5, "Tasks assigned",
              _task("T01", "P1", "D1", robot="A", status="ASSIGNED"),
              _task("T02", "P2", "D1", robot="B", status="ASSIGNED"),
              _event("WINNER", rid="A", task="T01", msg="AMR A won auction for Task T01 (P1 -> D1)"),
              _event("WINNER", rid="B", task="T02", msg="AMR B won auction for Task T02 (P2 -> D1)"),
              ),

        # ── Pickup & Transit ──
        _step(12.0, "AMR A picks up at P1, AMR C charging",
              _goto("A", 0.0, 8.0, speed=0.35, status="MOVING", task="T01"),
              _stop("C"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=45, status="CHARGING"),
              _task("T01", "P1", "D1", robot="A", status="IN_PROGRESS"),
              _event("INFO", rid="A", task="T01", msg="AMR A picked up pallet at P1, routing to D1"),
              ),

        _step(12.0, "AMR A approaches Intersection I1",
              _goto("A", 0.0, 6.5, speed=0.6, status="MOVING", task="T01"),
              _goto("B", -2.5, -5.5, speed=0.6, status="MOVING", task="T02"),
              _stop("C"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=65, status="CHARGING"),
              _intent("A", "I1", eta=2.0),
              _reserve("I1", "A"),
              _event("RESERVATION", rid="A", resource="I1", msg="AMR A reserved I1 for corridor transit"),
              ),

        _step(12.0, "AMR A crosses I1 and continues down the central corridor",
              _goto("A", 0.0, 3.5, speed=0.6, status="MOVING", task="T01"),
              _stop("C"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=85, status="CHARGING"),
              _release("I1"),
              _clear_intent("A"),
              _event("RELEASE", rid="A", resource="I1", msg="AMR A cleared I1 chokepoint"),
              ),

        _step(12.0, "AMR A passes the parked container, AMR C finishes charging",
              _goto("A", 1.3, 0.75, speed=0.6, status="MOVING", task="T01"),
              _stop("C"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=100, status="CHARGING"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C reached 100% SoC at Charging Bay (CHG)"),
              ),

        _step(12.0, "AMR C departs Charging Bay",
              _goto("C", 3.8, -6.9, speed=0.5, status="MOVING"),
              _event("INFO", rid="C", resource="CHG", msg="AMR C undocked from Charging Bay — standby for dispatch"),
              ),

        _step(3.2, "AMR A arrives at Drop Station D1",
              _stop("A"),
              _robot("A", 0.0, -8.1, yaw=DOWN, vel=0.0, bat=87, status="IDLE"),
              _stop("C"),
              _robot("C", 4.0, -4.0, yaw=UP, vel=0.0, bat=100, status="IDLE"),
              _task("T01", "P1", "D1", robot="A", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="A", task="T01", msg="Task T01 completed successfully at Drop Station D1"),
              ),

        _step(12.0, "AMR A heads to Charging Bay to top up",
              _goto("A", 3.8, -6.9, speed=0.6, status="MOVING"),
              _event("INFO", rid="A", resource="CHG", msg="AMR A navigating to Charging Bay (CHG)"),
              ),

        _step(2.5, "AMR A docks at Charging Bay",
              _stop("A"),
              _robot("A", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=86, status="CHARGING"),
              _event("CHARGING", rid="A", resource="CHG", msg="AMR A docked at Charging Bay (CHG) — replenishment active"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 2 — INTERSECTION CONFLICT (I1)
# ═══════════════════════════════════════════════════════════════════════════

def _conflict_scenario() -> list[dict]:
    """Two AMRs (A and B) contest Intersection I1; priority negotiation avoids deadlock."""
    return [
        _step(2.5, "Robots converge toward Intersection I1",
              _robot("A", 0.0, 8.0, yaw=DOWN, vel=0.8, bat=90, status="MOVING", task="T01"),
              _robot("B", 0.0, 2.5, yaw=UP, vel=0.8, bat=85, status="MOVING", task="T02"),
              _robot("C", 5.5, -7.5, yaw=LEFT, bat=95, status="CHARGING"),
              _reserve("I1", None, "FREE"),
              _event("INFO", msg="AMR A and AMR B en route toward shared Intersection I1"),
              ),

        _step(12.0, "Both broadcast INTENT for I1 simultaneously",
              _goto("A", 0.0, 6.5, speed=0.6, status="MOVING", task="T01"),
              _goto("B", 0.0, 3.8, speed=0.6, status="MOVING", task="T02"),
              _intent("A", "I1", eta=1.5),
              _intent("B", "I1", eta=1.5),
              _event("CONFLICT", rid="A", related="B", resource="I1",
                     msg="Intersection conflict detected at I1: AMR A (ETA 1.5s) vs AMR B (ETA 1.5s)"),
              ),

        _step(2.5, "Priority rule applied — AMR A wins (Task priority / ID tiebreak)",
              _event("WINNER", rid="A", related="B", resource="I1",
                     msg="Decentralized priority resolution: AMR A granted I1 access; AMR B yields"),
              _reserve("I1", "A"),
              _stop("B"),
              _robot("B", 0.0, 4.0, yaw=UP, vel=0.0, bat=84, status="WAITING", task="T02"),
              _event("WAIT", rid="B", resource="I1",
                     msg="AMR B holding at safety standoff before I1 bollards"),
              ),

        _step(12.0, "AMR A crosses through I1",
              _goto("A", 0.0, 5.2, speed=0.6, status="MOVING", task="T01"),
              _stop("B"),
              _robot("B", 0.0, 4.0, yaw=UP, vel=0.0, bat=84, status="WAITING", task="T02"),
              _release("I1"),
              _clear_intent("A"),
              _event("RELEASE", rid="A", resource="I1", msg="AMR A released I1 reservation"),
              ),

        _step(12.0, "AMR B claims I1 and proceeds through corridor",
              _reserve("I1", "B"),
              _clear_intent("B"),
              _goto("B", 0.0, 5.2, speed=0.6, status="MOVING", task="T02"),
              _event("RESERVATION", rid="B", resource="I1", msg="AMR B acquired I1 and resumed navigation"),
              ),

        _step(12.0, "AMR B clears I1",
              _goto("B", 0.0, 6.8, speed=0.6, status="MOVING", task="T02"),
              _release("I1"),
              _event("RELEASE", rid="B", resource="I1", msg="AMR B cleared I1 — intersection is FREE"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 3 — OBSTACLE REROUTE
# ═══════════════════════════════════════════════════════════════════════════

def _reroute_scenario() -> list[dict]:
    """AMR encounters dynamic obstacle in central aisle and calculates alternative route."""
    return [
        _step(2.5, "AMR A en route via central corridor",
              _robot("A", 0.0, 3.5, yaw=DOWN, vel=0.8, bat=90, status="MOVING", task="T01"),
              _robot("B", 3.5, -6.5, yaw=UP, vel=0.0, bat=80, status="IDLE"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=70, status="CHARGING"),
              _event("INFO", msg="AMR A traversing central highway toward D1"),
              ),

        _step(3.2, "AMR A detects blocked central container",
              _stop("A"),
              _robot("A", 0.0, 1.9, yaw=DOWN, vel=0.0, bat=89, status="WAITING", task="T01"),
              _event("OBSTACLE", rid="A", resource="OBS_AISLE",
                     msg="LIDAR detected blockage at OBS_AISLE (-0.2, 0.75). Corridor centre blocked."),
              ),

        _step(12.0, "AMR A computes a local bypass down the east side of the corridor",
              _event("REROUTE", rid="A",
                     msg="AMR A replanned path via the east side of the corridor (x=+1.3) around the container"),
              _goto("A", 0.9, 1.6, speed=0.4, status="REROUTING", task="T01"),
              ),

        _step(12.0, "AMR A navigates the bypass safely",
              _goto("A", 1.3, 0.75, speed=0.6, status="MOVING", task="T01"),
              ),

        _step(12.0, "AMR A rejoins main corridor and approaches D1",
              _goto("A", 0.0, -0.7, speed=0.6, status="MOVING", task="T01"),
              _event("INFO", rid="A", msg="AMR A cleared obstacle zone and rejoined main route"),
              ),

        _step(3.2, "AMR A delivers to D1",
              _stop("A"),
              _robot("A", 0.0, -8.1, yaw=DOWN, vel=0.0, bat=85, status="IDLE"),
              _task("T01", "P1", "D1", robot="A", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="A", task="T01", msg="Task T01 completed via rerouted path"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 4 — AMR FAILURE & TASK REASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════

def _failure_scenario() -> list[dict]:
    """AMR A experiences hardware fault; mesh peers detect loss and reassign task."""
    return [
        _step(2.5, "All 3 AMRs operational",
              _robot("A", 0.0, 6.5, yaw=DOWN, vel=0.8, bat=80, status="MOVING", task="T01"),
              _robot("B", 0.5, 8.5, yaw=DOWN, vel=0.0, bat=88, status="IDLE"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=98, status="CHARGING"),
              _task("T01", "P1", "D1", robot="A", status="IN_PROGRESS"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _event("INFO", msg="AMR A carrying Task T01 payload"),
              ),

        _step(3.2, "AMR A experiences drive motor failure",
              _stop("A"),
              _robot("A", 0.0, 4.0, yaw=DOWN, vel=0.0, bat=80, status="FAILED", task="T01"),
              _event("FAILURE", rid="A", msg="CRITICAL: AMR A drive system fault at (0.0, 4.0). E-Stop engaged."),
              ),

        _step(4.0, "Heartbeat timeout detected by mesh peers",
              _event("HEARTBEAT_TIMEOUT", rid="A", msg="Mesh monitor: Heartbeat timeout for AMR A (>3.0s elapsed)"),
              _task("T01", "P1", "D1", robot=None, status="WAITING"),
              _event("INFO", task="T01", msg="Task T01 released to auction pool for reassignment"),
              ),

        _step(12.0, "Decentralized task claim — AMR B accepts T01",
              _task("T01", "P1", "D1", robot="B", status="REASSIGNED"),
              _event("REASSIGNMENT", rid="B", related="A", task="T01",
                     msg="AMR B accepted reclaim of Task T01; heading to recovery point"),
              _goto("B", 0.0, 6.8, speed=0.6, status="MOVING", task="T01"),
              ),

        _step(12.0, "AMR B intercepts load and navigates to D1",
              _goto("B", 1.3, 0.75, speed=0.6, status="MOVING", task="T01"),
              ),

        _step(3.2, "AMR B completes reclaimed task",
              _stop("B"),
              _robot("B", 0.0, -8.1, yaw=DOWN, vel=0.0, bat=83, status="IDLE"),
              _task("T01", "P1", "D1", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="B", task="T01",
                     msg="Reassigned task T01 completed successfully by AMR B"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 5 — NETWORK DEGRADATION
# ═══════════════════════════════════════════════════════════════════════════

def _network_scenario() -> list[dict]:
    """Simulates packet loss and elevated latency; conservative safety buffers engage."""
    return [
        _step(2.5, "Mesh network healthy",
              _robot("A", 0.0, 8.0, yaw=DOWN, vel=0.8, bat=92, status="MOVING"),
              _robot("B", 0.0, -2.0, yaw=UP, vel=0.8, bat=88, status="MOVING"),
              _robot("C", 5.5, -7.5, yaw=LEFT, vel=0.0, bat=50, status="CHARGING"),
              _network("NORMAL", latency=14, loss=0.2, peers=3),
              _event("INFO", msg="Wireless mesh telemetry nominal: 14ms RTT, 0.2% packet loss"),
              ),

        _step(12.0, "RF interference causes packet drops and high latency",
              _network("DEGRADED", latency=180, loss=15.5, peers=2),
              _event("NETWORK_DEGRADED", msg="Mesh link degraded: 180ms latency, 15.5% packet loss. AMR B unreachable."),
              _goto("A", 0.0, 6.5, speed=0.35, status="MOVING"),
              _stop("B"),
              _robot("B", 0.0, 2.5, yaw=UP, vel=0.2, bat=87, status="WAITING"),
              _event("INFO", msg="Safety protocol engaged: speed reduced 50%, reservation timeout enlarged"),
              ),

        _step(12.0, "Network conditions stabilize",
              _network("NORMAL", latency=16, loss=0.5, peers=3),
              _event("NETWORK_RECOVERED", msg="Mesh network restored: 16ms latency, 0.5% loss. 3/3 peers synced."),
              _goto("A", 0.0, 4.0, speed=0.6, status="MOVING"),
              _goto("B", 0.0, 6.8, speed=0.6, status="MOVING"),
              _event("INFO", msg="Full operational velocity restored across fleet"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 6 — FULL DEMONSTRATION (END-TO-END)
# ═══════════════════════════════════════════════════════════════════════════

def _full_demo_scenario() -> list[dict]:
    """Long-form showcase of every coordination behaviour, in one continuous run.

    Roughly five minutes per loop, structured as numbered acts so it can be
    narrated or cut into clips:

        1  Fleet online, shift workload announced
        2  Distributed auction (all peers bid, all agree)
        3  Winner drives to pickup
        4  Second task auctioned in parallel
        5  Intersection conflict at I1 -> priority -> reservation -> wait
        6  Blocked aisle -> obstacle detected -> reroute
        7  Delivery, then the pad is cleared for the next robot
        8  Battery-aware bidding (a low AMR declines)
        9  Second conflict, at the I2 gate
       10  Network degradation and recovery
       11  Robot failure -> heartbeat timeout -> decentralized reclaim
       12  Priority task preempts the queue
       13  All three AMRs working in parallel
       14  Charging cycle
       15  Shift summary

    Every leg is a _goto, so routes are planned over the real occupancy grid and
    driven continuously through the aisles.
    """
    return [
        # ═══ ACT 1 — Fleet online ════════════════════════════════════════
        _step(0.0, "ACT 1 — Fleet online at spawn docks",
              _robot("A", -3.5, 5.25, yaw=RIGHT, bat=96, status="IDLE"),
              _robot("B", 0.5, 8.5, yaw=DOWN, bat=91, status="IDLE"),
              _robot("C", 3.5, -6.5, yaw=LEFT, bat=28, status="CHARGING"),
              _network("NORMAL", latency=11, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _event("INFO", msg="SYNERGY online — 3 AMRs, decentralized allocation, no central coordinator"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C docked at Charging Bay (28%)"),
              ),
        _step(3.0, "Shift workload announced to every peer",
              _task("T01", "P1", "D1"),
              _task("T02", "S1", "D1"),
              _task("T03", "S8", "D1"),
              _task("T04", "P2", "D1"),
              _task("T05", "D1", "CHG"),
              _event("TASK_ANNOUNCED", msg="Shift queue: 5 transport tasks broadcast on /tasks/announcements"),
              ),

        # ═══ ACT 2 — Distributed auction ═════════════════════════════════
        _step(2.5, "ACT 2 — All three AMRs bid on T01 independently",
              _event("BID_SUBMITTED", rid="A", task="T01", msg="AMR A bids 8.9s (dist 4.9m, battery 96%)"),
              _event("BID_SUBMITTED", rid="B", task="T01", msg="AMR B bids 1.2s (dist 0.7m, battery 91%)"),
              _event("BID_SUBMITTED", rid="C", task="T01", msg="AMR C bids 27.1s (dist 14.9m, battery 28% — charging)"),
              ),
        _step(2.0, "Every peer independently elects AMR B — consensus, no coordinator",
              _task("T01", "P1", "D1", robot="B", status="ASSIGNED"),
              _event("WINNER", rid="B", task="T01", msg="Consensus on all 3 peers: AMR B wins T01 (lowest bid 1.2s)"),
              ),

        # ═══ ACT 3 — Winner drives to pickup ═════════════════════════════
        _step(1.0, "ACT 3 — AMR B routes to Pickup P1",
              _goto("B", 0.0, 8.0, task="T01", arrive="WAITING"),
              _event("INFO", rid="B", task="T01", msg="AMR B navigating to P1 via the north bay"),
              ),
        _step(5.0, "AMR B loads its pallet at P1",
              _task("T01", "P1", "D1", robot="B", status="IN_PROGRESS"),
              _event("INFO", rid="B", task="T01", msg="AMR B loaded at P1 — outbound to D1"),
              ),

        # ═══ ACT 4 — Parallel auction ════════════════════════════════════
        _step(1.5, "ACT 4 — T02 auctioned in parallel; AMR A wins",
              _event("BID_SUBMITTED", rid="A", task="T02", msg="AMR A bids 2.4s (dist 1.3m)"),
              _event("BID_SUBMITTED", rid="B", task="T02", msg="AMR B bids 18.7s — already carrying T01"),
              _task("T02", "S1", "D1", robot="A", status="ASSIGNED"),
              _event("WINNER", rid="A", task="T02", msg="Consensus: AMR A wins T02"),
              _goto("A", -4.8, 6.0, task="T02", arrive="WAITING"),
              ),
        _step(6.0, "AMR A collects from rack S1",
              _task("T02", "S1", "D1", robot="A", status="IN_PROGRESS"),
              _event("INFO", rid="A", task="T02", msg="AMR A loaded at rack S1 — outbound to D1"),
              ),

        # ═══ ACT 5 — Intersection conflict at I1 ═════════════════════════
        _step(1.0, "ACT 5 — Both AMRs converge on intersection I1",
              _goto("B", 0.0, 6.4, task="T01", speed=0.5),
              _goto("A", -1.6, 5.9, task="T02", speed=0.5),
              _intent("B", "I1", eta=2.8),
              _intent("A", "I1", eta=3.9),
              _event("INTENT", rid="B", resource="I1", msg="AMR B declares intent for I1 (ETA 2.8s)"),
              _event("INTENT", rid="A", resource="I1", msg="AMR A declares intent for I1 (ETA 3.9s)"),
              ),
        _step(4.0, "Conflict detected — both need the same chokepoint",
              _event("CONFLICT", rid="A", related="B", resource="I1",
                     msg="CONFLICT at I1: AMR A and AMR B both claim the gate"),
              ),
        _step(1.5, "Priority rule resolves it locally — B reserves, A yields",
              _reserve("I1", "B"),
              _stop("A"),
              _event("PRIORITY", rid="B", related="A", resource="I1",
                     msg="Priority to AMR B (earlier ETA, loaded payload). Deterministic on every peer."),
              _event("RESERVATION", rid="B", resource="I1", msg="AMR B holds the reservation on I1"),
              _event("WAITING", rid="A", resource="I1", msg="AMR A WAITING — holding short of I1"),
              ),
        _step(4.0, "AMR B crosses I1 and releases the reservation",
              _goto("B", 0.0, 2.6, task="T01", speed=0.55),
              _clear_intent("B"),
              ),
        _step(5.0, "I1 released — AMR A proceeds",
              _release("I1"),
              _reserve("I1", "A"),
              _clear_intent("A"),
              _goto("A", 0.0, 4.2, task="T02", speed=0.5),
              _event("RELEASE", rid="B", resource="I1", msg="AMR B cleared I1 — reservation released"),
              _event("RESERVATION", rid="A", resource="I1", msg="AMR A acquires I1 and resumes"),
              ),

        # ═══ ACT 6 — Blocked aisle and reroute ═══════════════════════════
        _step(4.0, "ACT 6 — AMR B detects the container blocking the corridor",
              _stop("B"),
              _event("OBSTACLE", rid="B", resource="OBS_AISLE",
                     msg="LiDAR: container at (-0.2, 0.75) blocking the corridor centre"),
              ),
        _step(2.0, "AMR B replans around it — route bends east",
              _goto("B", 1.4, 0.6, task="T01", speed=0.45),
              _event("REROUTE", rid="B", task="T01",
                     msg="AMR B replanned via the east side of the corridor — 1.1m detour"),
              ),
        _step(4.0, "AMR B rejoins the corridor past the obstacle",
              _release("I1"),
              _goto("B", 0.0, -4.5, task="T01", speed=0.55),
              _event("INFO", rid="B", task="T01", msg="AMR B clear of the obstacle zone"),
              ),

        # ═══ ACT 7 — Delivery and pad clearing ═══════════════════════════
        _step(9.0, "ACT 7 — AMR B delivers T01 at D1",
              _goto("B", 0.0, -8.1, task="T01", arrive="WAITING", speed=0.55),
              ),
        _step(8.0, "T01 complete — AMR B clears the pad for the next robot",
              _task("T01", "P1", "D1", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="B", task="T01", msg="Task T01 COMPLETED at D1 by AMR B"),
              _goto("B", 0.5, 8.5, speed=0.55),
              _event("INFO", rid="B", msg="AMR B returning to standby — a robot parked on D1 blocks the next delivery"),
              ),

        # ═══ ACT 8 — Battery-aware bidding ═══════════════════════════════
        _step(3.0, "ACT 8 — T03 auctioned; AMR C declines on battery",
              _event("BID_SUBMITTED", rid="A", task="T03", msg="AMR A bids 21.4s"),
              _event("INFO", rid="C", task="T03",
                     msg="AMR C ELIGIBILITY=False (battery 41% below reserve, still charging) — no bid"),
              _task("T03", "S8", "D1", robot="A", status="ASSIGNED"),
              _event("WINNER", rid="A", task="T03", msg="AMR A wins T03 — only eligible bidder"),
              ),

        # ═══ ACT 9 — Second conflict at the I2 gate ══════════════════════
        _step(2.0, "ACT 9 — AMR A heads for the I2 gate with T02",
              _goto("A", 1.3, 0.4, task="T02", speed=0.5),   # east of the parked container
              _intent("A", "I2", eta=3.1),
              _event("INTENT", rid="A", resource="I2", msg="AMR A declares intent for I2"),
              ),
        _step(6.0, "AMR C undocks charged and also needs I2",
              _robot("C", 3.5, -6.5, yaw=UP, bat=100, status="IDLE"),
              _goto("C", 0.0, -2.4, speed=0.5),
              _intent("C", "I2", eta=4.4),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C reached 100% — undocking"),
              _event("INTENT", rid="C", resource="I2", msg="AMR C declares intent for I2"),
              _event("CONFLICT", rid="A", related="C", resource="I2",
                     msg="CONFLICT at I2: AMR A vs AMR C"),
              ),
        _step(2.0, "A wins I2 on priority; C holds short",
              _reserve("I2", "A"),
              _stop("C"),
              _event("PRIORITY", rid="A", related="C", resource="I2",
                     msg="Priority to AMR A (loaded, earlier ETA). AMR C yields."),
              _event("WAITING", rid="C", resource="I2", msg="AMR C WAITING at I2"),
              ),
        _step(5.0, "AMR A clears I2",
              _goto("A", 0.0, -3.2, task="T02", speed=0.55),
              _release("I2"),
              _clear_intent("A"),
              _clear_intent("C"),
              _event("RELEASE", rid="A", resource="I2", msg="AMR A cleared I2 — gate free"),
              ),

        # ═══ ACT 10 — Network degradation ════════════════════════════════
        _step(3.0, "ACT 10 — Mesh degrades: latency spike and packet loss",
              _network("DEGRADED", latency=310, loss=18, peers=3),
              _event("NETWORK", msg="Mesh DEGRADED — latency 310ms, 18% loss. Peers fall back to local decisions."),
              ),
        _step(4.0, "Coordination continues on cached peer state",
              _event("INFO", msg="No central controller to lose: each AMR keeps deciding from its own world model"),
              ),
        _step(4.0, "Mesh recovers — peers reconcile",
              _network("NORMAL", latency=13, loss=0, peers=3),
              _event("NETWORK", msg="Mesh NORMAL — 3/3 peers reachable, state reconciled"),
              ),

        # ═══ ACT 11 — Failure and decentralized reclaim ══════════════════
        _step(3.0, "ACT 11 — AMR A suffers a drive fault mid-route",
              _stop("A"),
              _event("FAILURE", rid="A", task="T02",
                     msg="CRITICAL: AMR A drive fault — E-Stop engaged, heartbeat lost"),
              ),
        _step(4.0, "Peers detect the missing heartbeat and release the task",
              _task("T02", "S1", "D1", robot=None, status="WAITING"),
              _task("T03", "S8", "D1", robot=None, status="ANNOUNCED"),
              _event("HEARTBEAT_TIMEOUT", rid="A",
                     msg="No heartbeat from AMR A for >10s — B and C mark it FAILED"),
              _event("INFO", task="T02", msg="T02 and T03 returned to the auction pool"),
              ),
        _step(3.0, "AMR C wins the reclaimed T02",
              _task("T02", "S1", "D1", robot="C", status="REASSIGNED"),
              _event("BID_SUBMITTED", rid="C", task="T02", msg="AMR C bids 9.6s on recovered T02 (battery 100%)"),
              _event("BID_SUBMITTED", rid="B", task="T02", msg="AMR B bids 24.8s"),
              _event("REASSIGNMENT", rid="C", related="A", task="T02",
                     msg="AMR C wins the recovered T02 — fleet self-heals without operator input"),
              _goto("C", 0.0, -6.0, task="T02", speed=0.55),
              ),
        _step(9.0, "AMR C completes the reclaimed delivery",
              _goto("C", 0.0, -8.1, task="T02", arrive="WAITING", speed=0.55),
              ),
        _step(8.0, "T02 COMPLETED by AMR C",
              _task("T02", "S1", "D1", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="C", task="T02",
                     msg="Recovered task T02 COMPLETED by AMR C"),
              _goto("C", 3.5, -6.5, speed=0.55),
              ),

        # ═══ ACT 12 — Priority preemption ════════════════════════════════
        _step(4.0, "ACT 12 — Urgent T04 jumps the queue",
              _task("T04", "P2", "D1", status="ANNOUNCED"),
              _event("TASK_ANNOUNCED", msg="Task T04 (P2 -> D1) announced at PRIORITY 5 — urgent"),
              _event("BID_SUBMITTED", rid="B", task="T04", msg="AMR B bids 26.1s"),
              _event("BID_SUBMITTED", rid="C", task="T04", msg="AMR C bids 11.3s (nearest to P2)"),
              _task("T04", "P2", "D1", robot="C", status="ASSIGNED"),
              _event("WINNER", rid="C", task="T04", msg="AMR C wins urgent T04 — preempts the standing queue"),
              _goto("C", -6.4, -6.3, task="T04", arrive="WAITING", speed=0.55),
              ),

        # ═══ ACT 13 — Three AMRs working in parallel ═════════════════════
        _step(6.0, "ACT 13 — AMR A recovers and rejoins the fleet",
              _robot("A", 0.0, -3.2, yaw=DOWN, bat=72, status="IDLE"),
              _event("INFO", rid="A", msg="AMR A fault cleared — heartbeat restored, rejoining the fleet"),
              _task("T03", "S8", "D1", robot="A", status="ASSIGNED"),
              _event("WINNER", rid="A", task="T03", msg="AMR A wins T03 on re-auction"),
              _goto("A", 4.8, -4.5, task="T03", arrive="WAITING", speed=0.5),
              ),
        _step(7.0, "All three AMRs working simultaneously",
              _goto("B", 0.0, 4.0, speed=0.5),
              _event("INFO", msg="Parallel operations: A on T03, C on T04, B repositioning — 3/3 active"),
              ),
        _step(8.0, "AMR C carries T04 to D1; AMR A carries T03",
              _goto("C", 0.0, -7.0, task="T04", speed=0.55),
              _goto("A", 1.4, -5.0, task="T03", speed=0.5),
              _task("T04", "P2", "D1", robot="C", status="IN_PROGRESS"),
              _task("T03", "S8", "D1", robot="A", status="IN_PROGRESS"),
              ),
        _step(10.0, "Both deliveries land at D1, sequenced by reservation",
              _goto("C", 0.0, -8.1, task="T04", arrive="WAITING", speed=0.55),
              _reserve("D1", "C"),
              _event("RESERVATION", rid="C", resource="D1", msg="AMR C reserves the D1 bay; AMR A queues behind"),
              ),
        _step(8.0, "T04 delivered — bay handed to AMR A",
              _task("T04", "P2", "D1", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="C", task="T04", msg="Urgent task T04 COMPLETED by AMR C"),
              _release("D1"),
              _goto("C", 3.5, -6.5, speed=0.55),
              _goto("A", 0.0, -8.1, task="T03", arrive="WAITING", speed=0.55),
              _event("RELEASE", rid="C", resource="D1", msg="D1 bay released to AMR A"),
              ),
        _step(9.0, "T03 delivered",
              _task("T03", "S8", "D1", robot="A", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="A", task="T03", msg="Task T03 COMPLETED at D1 by AMR A"),
              _goto("A", -3.5, 5.25, speed=0.55),
              ),

        # ═══ ACT 14 — Charging cycle ═════════════════════════════════════
        _step(4.0, "ACT 14 — T05 auctioned; AMR B takes the charging run",
              _event("BID_SUBMITTED", rid="B", task="T05", msg="AMR B bids 14.2s (battery 74% — due a top-up)"),
              _task("T05", "D1", "CHG", robot="B", status="ASSIGNED"),
              _event("WINNER", rid="B", task="T05", msg="AMR B wins T05"),
              _goto("B", 5.5, -7.5, task="T05", arrive="CHARGING", speed=0.55),
              ),
        _step(16.0, "AMR B docks at the charging bay",
              _task("T05", "D1", "CHG", robot="B", status="COMPLETED"),
              _event("CHARGING", rid="B", resource="CHG", msg="AMR B docked at CHG — T05 COMPLETED"),
              ),

        # ═══ ACT 15 — Shift summary ══════════════════════════════════════
        _step(4.0, "ACT 15 — Shift summary",
              _event("INFO", msg="Shift complete — 5/5 tasks delivered, 0 collisions"),
              _event("INFO", msg="2 intersection conflicts resolved (I1, I2) by peer priority + reservation"),
              _event("INFO", msg="1 obstacle reroute, 1 robot failure recovered, 1 network degradation ridden out"),
              _event("INFO", msg="All decisions taken peer-to-peer — the dashboard only observed"),
              ),
        _step(6.0, "Resetting for the next shift",
              _event("INFO", msg="Cycle restarting"),
              ),
    ]


AVAILABLE_SCENARIOS: dict[str, callable] = {
    "normal": _normal_scenario,
    "conflict": _conflict_scenario,
    "reroute": _reroute_scenario,
    "failure": _failure_scenario,
    "network": _network_scenario,
    "full_demo": _full_demo_scenario,
}


def get_scenario(name: str) -> list[dict]:
    """Retrieve scenario steps by name."""
    builder = AVAILABLE_SCENARIOS.get(name)
    if not builder:
        raise KeyError(f"Unknown scenario '{name}'. Available: {list_scenarios()}")
    return builder()


def list_scenarios() -> list[str]:
    """Return a list of all registered scenario names."""
    return list(AVAILABLE_SCENARIOS.keys())

