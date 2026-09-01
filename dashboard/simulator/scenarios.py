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
- Pickup 1 (P1): (-7.2, 0.0) [West Central Station]
- Pickup 2 (P2): (-7.2, -7.5) [South-West Station]
- Drop 1 (D1): (6.8, 0.0) [East Central Station]
- Charging Bay (CHG): (6.0, 6.0) [North-East Charging Dock with ⚡ terminal]
- Intersection I1: (-4.3, 0.0) [West-Central Chokepoint]
- Intersection I2: (0.8, 0.0) [East-Central Chokepoint]
- Central Obstacle: (-1.5, 0.0) [Orange Blocked Container in central aisle]
- AMRs spawn at: A (-7.5, 0.8), B (-4.3, -3.2), C (5.0, 3.5)
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
        _step(0.0, "Robots online at Gazebo visual layout positions",
              _robot("A", -7.5, 0.8, yaw=RIGHT, bat=95, status="IDLE"),
              _robot("B", -4.3, -3.2, yaw=UP, bat=90, status="IDLE"),
              _robot("C", 6.0, 6.0, yaw=DOWN, bat=30, status="CHARGING"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _event("INFO", msg="Fleet operational — 3 AMRs connected (20x20m facility layout)"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C docked at Charging Bay (CHG) — rapid replenishment active"),
              ),

        # ── Tasks announced & assigned ──
        _step(1.5, "Tasks announced",
              _task("T01", "P1", "D1"),
              _task("T02", "P2", "D1"),
              _event("INFO", msg="2 logistics transport tasks announced to decentralized fleet"),
              ),

        _step(1.0, "Tasks assigned",
              _task("T01", "P1", "D1", robot="A", status="ASSIGNED"),
              _task("T02", "P2", "D1", robot="B", status="ASSIGNED"),
              _event("WINNER", rid="A", task="T01", msg="AMR A won auction for Task T01 (P1 -> D1)"),
              _event("WINNER", rid="B", task="T02", msg="AMR B won auction for Task T02 (P2 -> D1)"),
              ),

        # ── Pickup & Transit ──
        _step(1.5, "AMR A picks up at P1, AMR C charging",
              _robot("A", -7.2, 0.0, yaw=RIGHT, vel=0.3, bat=94, status="MOVING", task="T01"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=45, status="CHARGING"),
              _task("T01", "P1", "D1", robot="A", status="IN_PROGRESS"),
              _event("INFO", rid="A", task="T01", msg="AMR A picked up pallet at P1, routing to D1"),
              ),

        _step(2.0, "AMR A approaches Intersection I1",
              _robot("A", -5.5, 0.0, yaw=RIGHT, vel=0.8, bat=93, status="MOVING", task="T01"),
              _robot("B", -6.0, -5.5, yaw=DOWN, vel=0.6, bat=88, status="MOVING", task="T02"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=65, status="CHARGING"),
              _intent("A", "I1", eta=2.0),
              _reserve("I1", "A"),
              _event("RESERVATION", rid="A", resource="I1", msg="AMR A reserved I1 for corridor transit"),
              ),

        _step(2.0, "AMR A crosses I1 and moves North of central obstacle",
              _robot("A", -3.0, 1.5, yaw=UP, vel=0.8, bat=91, status="MOVING", task="T01"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=85, status="CHARGING"),
              _release("I1"),
              _clear_intent("A"),
              _event("RELEASE", rid="A", resource="I1", msg="AMR A cleared I1 chokepoint"),
              ),

        _step(2.5, "AMR A travels East aisle, AMR C finishes charging",
              _robot("A", 2.0, 1.5, yaw=RIGHT, vel=0.9, bat=89, status="MOVING", task="T01"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=100, status="CHARGING"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C reached 100% SoC at Charging Bay (CHG)"),
              ),

        _step(1.5, "AMR C departs Charging Bay",
              _robot("C", 5.0, 4.5, yaw=DOWN, vel=0.5, bat=100, status="MOVING"),
              _event("INFO", rid="C", resource="CHG", msg="AMR C undocked from Charging Bay — standby for dispatch"),
              ),

        _step(2.0, "AMR A arrives at Drop Station D1",
              _robot("A", 6.8, 0.0, yaw=RIGHT, vel=0.0, bat=87, status="IDLE"),
              _robot("C", 5.0, 3.5, yaw=LEFT, vel=0.0, bat=100, status="IDLE"),
              _task("T01", "P1", "D1", robot="A", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="A", task="T01", msg="Task T01 completed successfully at Drop Station D1"),
              ),

        _step(1.5, "AMR A heads to Charging Bay to top up",
              _robot("A", 6.0, 4.0, yaw=UP, vel=0.6, bat=86, status="MOVING"),
              _event("INFO", rid="A", resource="CHG", msg="AMR A navigating to Charging Bay (CHG)"),
              ),

        _step(1.5, "AMR A docks at Charging Bay",
              _robot("A", 6.0, 6.0, yaw=UP, vel=0.0, bat=86, status="CHARGING"),
              _event("CHARGING", rid="A", resource="CHG", msg="AMR A docked at Charging Bay (CHG) — replenishment active"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 2 — INTERSECTION CONFLICT (I1)
# ═══════════════════════════════════════════════════════════════════════════

def _conflict_scenario() -> list[dict]:
    """Two AMRs (A and B) contest Intersection I1; priority negotiation avoids deadlock."""
    return [
        _step(0.0, "Robots converge toward Intersection I1",
              _robot("A", -7.2, 0.0, yaw=RIGHT, vel=0.8, bat=90, status="MOVING", task="T01"),
              _robot("B", -4.3, -3.5, yaw=UP, vel=0.8, bat=85, status="MOVING", task="T02"),
              _robot("C", 6.0, 6.0, yaw=DOWN, bat=95, status="CHARGING"),
              _reserve("I1", None, "FREE"),
              _event("INFO", msg="AMR A and AMR B en route toward shared Intersection I1"),
              ),

        _step(2.0, "Both broadcast INTENT for I1 simultaneously",
              _robot("A", -5.5, 0.0, yaw=RIGHT, vel=0.8, bat=89, status="MOVING", task="T01"),
              _robot("B", -4.3, -1.8, yaw=UP, vel=0.8, bat=84, status="MOVING", task="T02"),
              _intent("A", "I1", eta=1.5),
              _intent("B", "I1", eta=1.5),
              _event("CONFLICT", rid="A", related="B", resource="I1",
                     msg="Intersection conflict detected at I1: AMR A (ETA 1.5s) vs AMR B (ETA 1.5s)"),
              ),

        _step(1.0, "Priority rule applied — AMR A wins (Task priority / ID tiebreak)",
              _event("WINNER", rid="A", related="B", resource="I1",
                     msg="Decentralized priority resolution: AMR A granted I1 access; AMR B yields"),
              _reserve("I1", "A"),
              _robot("B", -4.3, -1.2, yaw=UP, vel=0.0, bat=84, status="WAITING", task="T02"),
              _event("WAIT", rid="B", resource="I1",
                     msg="AMR B holding at safety standoff before I1 bollards"),
              ),

        _step(2.0, "AMR A crosses through I1",
              _robot("A", -3.0, 1.5, yaw=UP, vel=0.8, bat=88, status="MOVING", task="T01"),
              _robot("B", -4.3, -1.2, yaw=UP, vel=0.0, bat=84, status="WAITING", task="T02"),
              _release("I1"),
              _clear_intent("A"),
              _event("RELEASE", rid="A", resource="I1", msg="AMR A released I1 reservation"),
              ),

        _step(1.0, "AMR B claims I1 and proceeds through corridor",
              _reserve("I1", "B"),
              _clear_intent("B"),
              _robot("B", -4.3, 0.5, yaw=UP, vel=0.7, bat=83, status="MOVING", task="T02"),
              _event("RESERVATION", rid="B", resource="I1", msg="AMR B acquired I1 and resumed navigation"),
              ),

        _step(2.0, "AMR B clears I1",
              _robot("B", -4.3, 2.5, yaw=UP, vel=0.8, bat=82, status="MOVING", task="T02"),
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
        _step(0.0, "AMR A en route via central corridor",
              _robot("A", -3.5, 0.0, yaw=RIGHT, vel=0.8, bat=90, status="MOVING", task="T01"),
              _robot("B", 3.2, -5.5, yaw=UP, vel=0.0, bat=80, status="IDLE"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=70, status="CHARGING"),
              _event("INFO", msg="AMR A traversing central highway toward D1"),
              ),

        _step(2.0, "AMR A detects blocked central container",
              _robot("A", -2.2, 0.0, yaw=RIGHT, vel=0.0, bat=89, status="WAITING", task="T01"),
              _event("OBSTACLE", rid="A", resource="OBS_AISLE",
                     msg="LIDAR detected blockage at OBS_AISLE (-1.5, 0.0). Main corridor blocked."),
              ),

        _step(1.5, "AMR A computes local bypass route via North safety lane",
              _event("REROUTE", rid="A",
                     msg="AMR A replanned path via North aisle (y=+1.5) around obstacle"),
              _robot("A", -2.2, 0.8, yaw=UP, vel=0.4, bat=88, status="REROUTING", task="T01"),
              ),

        _step(2.5, "AMR A navigates bypass lane safely",
              _robot("A", 0.0, 1.5, yaw=RIGHT, vel=0.8, bat=87, status="MOVING", task="T01"),
              ),

        _step(2.0, "AMR A rejoins main corridor and approaches D1",
              _robot("A", 3.5, 0.0, yaw=RIGHT, vel=0.8, bat=86, status="MOVING", task="T01"),
              _event("INFO", rid="A", msg="AMR A cleared obstacle zone and rejoined main route"),
              ),

        _step(2.0, "AMR A delivers to D1",
              _robot("A", 6.8, 0.0, yaw=RIGHT, vel=0.0, bat=85, status="IDLE"),
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
        _step(0.0, "All 3 AMRs operational",
              _robot("A", -5.5, 0.0, yaw=RIGHT, vel=0.8, bat=80, status="MOVING", task="T01"),
              _robot("B", -4.3, -3.2, yaw=UP, vel=0.0, bat=88, status="IDLE"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=98, status="CHARGING"),
              _task("T01", "P1", "D1", robot="A", status="IN_PROGRESS"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _event("INFO", msg="AMR A carrying Task T01 payload"),
              ),

        _step(2.0, "AMR A experiences drive motor failure",
              _robot("A", -3.5, 0.0, yaw=RIGHT, vel=0.0, bat=80, status="FAILED", task="T01"),
              _event("FAILURE", rid="A", msg="CRITICAL: AMR A drive system fault at (-3.5, 0.0). E-Stop engaged."),
              ),

        _step(2.5, "Heartbeat timeout detected by mesh peers",
              _event("HEARTBEAT_TIMEOUT", rid="A", msg="Mesh monitor: Heartbeat timeout for AMR A (>3.0s elapsed)"),
              _task("T01", "P1", "D1", robot=None, status="WAITING"),
              _event("INFO", task="T01", msg="Task T01 released to auction pool for reassignment"),
              ),

        _step(1.5, "Decentralized task claim — AMR B accepts T01",
              _task("T01", "P1", "D1", robot="B", status="REASSIGNED"),
              _event("REASSIGNMENT", rid="B", related="A", task="T01",
                     msg="AMR B accepted reclaim of Task T01; heading to recovery point"),
              _robot("B", -4.3, -1.5, yaw=UP, vel=0.7, bat=87, status="MOVING", task="T01"),
              ),

        _step(2.5, "AMR B intercepts load and navigates to D1",
              _robot("B", 2.0, 1.5, yaw=RIGHT, vel=0.8, bat=85, status="MOVING", task="T01"),
              ),

        _step(2.0, "AMR B completes reclaimed task",
              _robot("B", 6.8, 0.0, yaw=RIGHT, vel=0.0, bat=83, status="IDLE"),
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
        _step(0.0, "Mesh network healthy",
              _robot("A", -7.2, 0.0, yaw=RIGHT, vel=0.8, bat=92, status="MOVING"),
              _robot("B", -4.3, -3.2, yaw=UP, vel=0.8, bat=88, status="MOVING"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=50, status="CHARGING"),
              _network("NORMAL", latency=14, loss=0.2, peers=3),
              _event("INFO", msg="Wireless mesh telemetry nominal: 14ms RTT, 0.2% packet loss"),
              ),

        _step(2.0, "RF interference causes packet drops and high latency",
              _network("DEGRADED", latency=180, loss=15.5, peers=2),
              _event("NETWORK_DEGRADED", msg="Mesh link degraded: 180ms latency, 15.5% packet loss. AMR B unreachable."),
              _robot("A", -5.0, 0.0, yaw=RIGHT, vel=0.3, bat=91, status="MOVING"),
              _robot("B", -4.3, -2.0, yaw=UP, vel=0.2, bat=87, status="WAITING"),
              _event("INFO", msg="Safety protocol engaged: speed reduced 50%, reservation timeout enlarged"),
              ),

        _step(3.0, "Network conditions stabilize",
              _network("NORMAL", latency=16, loss=0.5, peers=3),
              _event("NETWORK_RECOVERED", msg="Mesh network restored: 16ms latency, 0.5% loss. 3/3 peers synced."),
              _robot("A", -3.0, 0.0, yaw=RIGHT, vel=0.8, bat=90, status="MOVING"),
              _robot("B", -4.3, 0.0, yaw=UP, vel=0.8, bat=86, status="MOVING"),
              _event("INFO", msg="Full operational velocity restored across fleet"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 6 — FULL DEMONSTRATION (END-TO-END)
# ═══════════════════════════════════════════════════════════════════════════

def _full_demo_scenario() -> list[dict]:
    """Comprehensive demonstration featuring tasks, intersection negotiation, charging, and reroute."""
    return [
        # Step 0: Spawn & System Startup
        _step(0.0, "System startup & spawn",
              _robot("A", -7.5, 0.8, yaw=RIGHT, vel=0.0, bat=95, status="IDLE"),
              _robot("B", -4.3, -3.2, yaw=UP, vel=0.0, bat=90, status="IDLE"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=20, status="CHARGING"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _event("INFO", msg="SYNERGY fleet command online — 3 AMRs operational"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C charging at Charging Bay (CHG) [20% SoC]"),
              ),

        # Step 1: Tasks announced
        _step(2.0, "Tasks announced & assigned",
              _task("T01", "P1", "D1", robot="A", status="ASSIGNED"),
              _task("T02", "P2", "D1", robot="B", status="ASSIGNED"),
              _task("T03", "P1", "CHG", robot=None, status="ANNOUNCED"),
              _event("WINNER", rid="A", task="T01", msg="AMR A assigned Task T01 (P1 -> D1)"),
              _event("WINNER", rid="B", task="T02", msg="AMR B assigned Task T02 (P2 -> D1)"),
              _event("INFO", msg="Task T03 (P1 -> CHG) queued in decentralized auction pool"),
              ),

        # Step 2: AMR A picks up payload, AMR C charges up
        _step(1.5, "AMR A picks up load at P1",
              _robot("A", -7.2, 0.0, yaw=RIGHT, vel=0.4, bat=94, status="MOVING", task="T01"),
              _robot("B", -6.0, -5.5, yaw=DOWN, vel=0.7, bat=89, status="MOVING", task="T02"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=50, status="CHARGING"),
              _task("T01", "P1", "D1", robot="A", status="IN_PROGRESS"),
              _event("INFO", rid="A", task="T01", msg="AMR A pallet loaded at P1, moving East"),
              ),

        # Step 3: Intersection Conflict at I1
        _step(2.0, "AMRs contest I1",
              _robot("A", -5.5, 0.0, yaw=RIGHT, vel=0.8, bat=93, status="MOVING", task="T01"),
              _robot("B", -4.3, -1.8, yaw=UP, vel=0.8, bat=88, status="MOVING", task="T02"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=75, status="CHARGING"),
              _intent("A", "I1", eta=1.5),
              _intent("B", "I1", eta=1.5),
              _event("CONFLICT", rid="A", related="B", resource="I1", msg="Contention at I1: AMR A vs AMR B"),
              ),

        # Step 4: Resolution & Passing
        _step(1.5, "AMR A wins I1, AMR B yields",
              _reserve("I1", "A"),
              _robot("B", -4.3, -1.2, yaw=UP, vel=0.0, bat=88, status="WAITING", task="T02"),
              _event("WINNER", rid="A", related="B", resource="I1", msg="Priority granted to AMR A"),
              _event("WAIT", rid="B", resource="I1", msg="AMR B holds at I1 chokepoint"),
              ),

        # Step 5: AMR A crosses I1 and bypasses central obstacle
        _step(2.0, "AMR A traverses North lane bypass",
              _robot("A", -3.0, 1.5, yaw=UP, vel=0.8, bat=92, status="MOVING", task="T01"),
              _release("I1"),
              _clear_intent("A"),
              _reserve("I1", "B"),
              _clear_intent("B"),
              _robot("B", -4.3, 0.0, yaw=UP, vel=0.7, bat=87, status="MOVING", task="T02"),
              _event("RELEASE", rid="A", resource="I1", msg="AMR A released I1; AMR B proceeding"),
              ),

        # Step 6: AMR C completes charging and undocks
        _step(2.0, "AMR C reaches 100% and undocks from CHG",
              _robot("A", 2.0, 1.5, yaw=RIGHT, vel=0.8, bat=90, status="MOVING", task="T01"),
              _robot("B", -4.3, 2.5, yaw=UP, vel=0.8, bat=86, status="MOVING", task="T02"),
              _robot("C", 6.0, 6.0, yaw=DOWN, vel=0.0, bat=100, status="CHARGING"),
              _release("I1"),
              _event("CHARGING", rid="C", resource="CHG", msg="AMR C reached 100% SoC at Charging Bay (CHG)"),
              ),

        _step(1.5, "AMR C deploys into fleet",
              _robot("C", 5.0, 4.0, yaw=DOWN, vel=0.6, bat=100, status="MOVING"),
              _event("INFO", rid="C", resource="CHG", msg="AMR C undocked from Charging Bay (CHG) — operational"),
              ),

        # Step 7: AMR A delivers payload to D1
        _step(2.0, "AMR A drops payload at D1",
              _robot("A", 6.8, 0.0, yaw=RIGHT, vel=0.0, bat=89, status="IDLE"),
              _robot("C", 5.0, 2.5, yaw=LEFT, vel=0.0, bat=100, status="IDLE"),
              _task("T01", "P1", "D1", robot="A", status="COMPLETED"),
              _event("TASK_COMPLETED", rid="A", task="T01", msg="Task T01 completed at Drop Station D1"),
              ),

        # Step 8: AMR A routes to Charging Bay for replenishment
        _step(1.5, "AMR A moves to Charging Bay CHG",
              _robot("A", 6.0, 3.5, yaw=UP, vel=0.7, bat=88, status="MOVING"),
              _event("INFO", rid="A", resource="CHG", msg="AMR A navigating to Charging Bay (CHG) for recharge"),
              ),

        # Step 9: AMR A docks at Charging Bay CHG
        _step(1.5, "AMR A docks at Charging Bay",
              _robot("A", 6.0, 6.0, yaw=UP, vel=0.0, bat=88, status="CHARGING"),
              _event("CHARGING", rid="A", resource="CHG", msg="AMR A docked at Charging Bay (CHG) — rapid replenishment active"),
              ),
    ]


# ── Scenario registry ───────────────────────────────────────────────────────

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

