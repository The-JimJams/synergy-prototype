"""
SYNERGY Dashboard — Scenario Definitions
==========================================

Each scenario is a list of **steps**.  A step is a dict:

    {
        "delay":       float,      # seconds to wait BEFORE executing
        "description": str,        # human-readable label (for logs/debug)
        "actions":     list[dict], # things to push into the DataStore
    }

Each action is:

    {"type": "<store_method_key>", "data": {<model fields>}}

Supported action types (mapped to DataStore methods by FleetSimulator):
    update_robot, update_intent, clear_intent,
    update_reservation, release_reservation,
    update_task, add_event,
    update_network, update_metrics

IMPORTANT
---------
The simulator is NOT implementing the real SYNERGY coordination algorithm.
It replays deterministic telemetry so the dashboard UI can be developed and
demonstrated independently.  The "winner" in a conflict, the "reassigned"
task, etc. are scripted outcomes — not algorithm outputs.

Timestamps are **omitted** from action data so the simulator adds fresh
ISO-8601 timestamps at execution time, keeping the feed realistic.
"""

from __future__ import annotations

import math

# ── Action-builder helpers ──────────────────────────────────────────────────
# These keep scenario definitions readable and typo-resistant.


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
    d = {
        "type": "update_task",
        "data": {
            "task_id": tid, "pickup": pickup, "dropoff": dropoff,
            "assigned_robot": robot, "status": status,
        },
    }
    return d


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
# SCENARIO 1 — NORMAL OPERATION
# ═══════════════════════════════════════════════════════════════════════════

def _normal_scenario() -> list[dict]:
    """Three robots move around the warehouse and complete tasks."""
    return [
        # ── Initialise ──
        _step(0.0, "Robots online at home positions",
              _robot("A", 2.0, 4.0, bat=95, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=88, status="IDLE"),
              _robot("C", 10.0, 4.0, bat=92, status="IDLE"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              ),

        # ── Tasks announced & assigned ──
        _step(1.5, "Tasks announced",
              _task("T01", "S1", "S3"),
              _task("T02", "S3", "S2"),
              _task("T03", "S4", "S1"),
              _event("INFO", msg="3 tasks announced"),
              ),

        _step(1.0, "Tasks assigned",
              _task("T01", "S1", "S3", robot="A", status="ASSIGNED"),
              _task("T02", "S3", "S2", robot="B", status="ASSIGNED"),
              _task("T03", "S4", "S1", robot="C", status="ASSIGNED"),
              _robot("A", 2.0, 4.0, bat=95, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _robot("B", 6.0, 1.5, bat=88, status="MOVING", task="T02", vel=0.8, yaw=RIGHT),
              _robot("C", 10.0, 4.0, bat=92, status="MOVING", task="T03", vel=0.8, yaw=UP),
              _event("INFO", "A", task="T01", msg="A assigned T01: S1→S3"),
              _event("INFO", "B", task="T02", msg="B assigned T02: S3→S2"),
              _event("INFO", "C", task="T03", msg="C assigned T03: S4→S1"),
              ),

        # ── Movement updates ──
        _step(1.5, "Robots moving to pickups",
              _robot("A", 2.0, 2.8, bat=94, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _robot("B", 8.0, 1.5, bat=87, status="MOVING", task="T02", vel=0.8, yaw=RIGHT),
              _robot("C", 10.0, 5.5, bat=91, status="MOVING", task="T03", vel=0.8, yaw=UP),
              ),

        _step(1.5, "Robots arriving at pickups",
              _robot("A", 2.0, 1.5, bat=93, status="MOVING", task="T01", vel=0.2, yaw=DOWN),
              _robot("B", 10.0, 1.5, bat=86, status="MOVING", task="T02", vel=0.2, yaw=RIGHT),
              _robot("C", 10.0, 6.5, bat=90, status="MOVING", task="T03", vel=0.2, yaw=UP),
              _task("T01", "S1", "S3", robot="A", status="IN_PROGRESS"),
              _task("T02", "S3", "S2", robot="B", status="IN_PROGRESS"),
              _task("T03", "S4", "S1", robot="C", status="IN_PROGRESS"),
              ),

        # ── Moving to dropoffs ──
        _step(1.5, "Heading to dropoffs",
              _robot("A", 4.0, 1.5, bat=92, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 8.0, 3.0, bat=85, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 8.0, 6.5, bat=89, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(1.5, "Continuing to dropoffs",
              _robot("A", 6.5, 1.5, bat=91, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 6.0, 4.5, bat=84, status="MOVING", task="T02", vel=0.8, yaw=LEFT),
              _robot("C", 5.0, 6.5, bat=88, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(1.5, "Approaching destinations",
              _robot("A", 8.5, 1.5, bat=90, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 3.5, 5.5, bat=83, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 3.0, 4.0, bat=87, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(1.5, "Arriving at dropoffs",
              _robot("A", 10.0, 1.5, bat=89, status="IDLE", vel=0.0),
              _robot("B", 2.0, 6.5, bat=82, status="IDLE", vel=0.0),
              _robot("C", 2.0, 1.5, bat=86, status="IDLE", vel=0.0),
              _task("T01", "S1", "S3", robot="A", status="COMPLETED"),
              _task("T02", "S3", "S2", robot="B", status="COMPLETED"),
              _task("T03", "S4", "S1", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", "A", task="T01", msg="A completed T01"),
              _event("TASK_COMPLETED", "B", task="T02", msg="B completed T02"),
              _event("TASK_COMPLETED", "C", task="T03", msg="C completed T03"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 2 — INTERSECTION CONFLICT
# ═══════════════════════════════════════════════════════════════════════════

def _conflict_scenario() -> list[dict]:
    """A and B both approach I1; A wins priority, B waits, then proceeds."""
    return [
        _step(0.0, "Robots online",
              _robot("A", 2.0, 4.0, bat=90, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=85, status="IDLE"),
              _robot("C", 10.0, 4.0, bat=88, status="IDLE"),
              _network("NORMAL", latency=10, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _task("T01", "S1", "S3", robot="A", status="ASSIGNED"),
              _task("T02", "S2", "S4", robot="B", status="ASSIGNED"),
              ),

        _step(1.0, "A and B start moving",
              _robot("A", 3.0, 4.0, bat=90, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 5.5, 2.5, bat=85, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _task("T01", "S1", "S3", robot="A", status="IN_PROGRESS"),
              _task("T02", "S2", "S4", robot="B", status="IN_PROGRESS"),
              ),

        _step(1.5, "Both approaching I1 — intents declared",
              _robot("A", 4.0, 4.0, bat=89, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 5.0, 3.0, bat=84, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _intent("A", "I1", eta=2.0),
              _intent("B", "I1", eta=2.3),
              _event("INFO", "A", resource="I1", msg="A declares intent for I1 (ETA 2.0s)"),
              _event("INFO", "B", resource="I1", msg="B declares intent for I1 (ETA 2.3s)"),
              ),

        _step(1.5, "Conflict detected at I1",
              _robot("A", 4.5, 4.0, bat=89, status="MOVING", task="T01", vel=0.5, yaw=RIGHT),
              _robot("B", 5.0, 3.5, bat=84, status="MOVING", task="T02", vel=0.5, yaw=UP),
              _event("CONFLICT", "A", related="B", resource="I1",
                     msg="Conflict detected at I1 between A and B"),
              ),

        _step(0.5, "A wins priority — deterministic resolution",
              _event("WINNER", "A", related="B", resource="I1",
                     msg="A wins priority at I1 (lower ETA)"),
              _reserve("I1", "A", "ACTIVE"),
              _event("RESERVATION", "A", resource="I1",
                     msg="I1 reserved by A"),
              _robot("B", 5.0, 3.5, bat=84, status="WAITING", task="T02", vel=0.0, yaw=UP),
              _event("WAIT", "B", resource="I1",
                     msg="B waiting for I1 (held by A)"),
              ),

        _step(2.0, "A passes through I1",
              _robot("A", 5.5, 4.0, bat=88, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              ),

        _step(1.5, "A clears I1 — reservation released",
              _robot("A", 7.0, 4.0, bat=87, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _clear_intent("A"),
              _release("I1"),
              _event("RELEASE", "A", resource="I1",
                     msg="A cleared I1 — reservation released"),
              ),

        _step(0.5, "B proceeds through I1",
              _robot("B", 5.0, 4.0, bat=83, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _clear_intent("B"),
              _event("INFO", "B", resource="I1", msg="B proceeds through I1"),
              ),

        _step(2.0, "B past I1, both heading to destinations",
              _robot("A", 9.0, 4.0, bat=86, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 5.0, 5.5, bat=82, status="MOVING", task="T02", vel=0.8, yaw=UP),
              ),

        _step(2.0, "Tasks completed",
              _robot("A", 10.0, 1.5, bat=85, status="IDLE", vel=0.0),
              _robot("B", 10.0, 6.5, bat=81, status="IDLE", vel=0.0),
              _task("T01", "S1", "S3", robot="A", status="COMPLETED"),
              _task("T02", "S2", "S4", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", "A", task="T01", msg="A completed T01"),
              _event("TASK_COMPLETED", "B", task="T02", msg="B completed T02"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 3 — BLOCKED AISLE / REROUTE
# ═══════════════════════════════════════════════════════════════════════════

def _reroute_scenario() -> list[dict]:
    """C encounters an obstacle and reroutes to an alternate aisle."""
    return [
        _step(0.0, "Robots online",
              _robot("A", 2.0, 4.0, bat=90, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=85, status="IDLE"),
              _robot("C", 10.0, 6.5, bat=88, status="IDLE"),
              _network("NORMAL", latency=11, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _task("T03", "S4", "S1", robot="C", status="ASSIGNED"),
              ),

        _step(1.0, "C moving toward S1",
              _robot("C", 9.0, 6.5, bat=87, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              _task("T03", "S4", "S1", robot="C", status="IN_PROGRESS"),
              ),

        _step(1.5, "C moving through upper aisle",
              _robot("C", 7.0, 6.5, bat=86, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(1.5, "Obstacle detected ahead of C",
              _robot("C", 6.0, 6.5, bat=85, status="MOVING", task="T03", vel=0.1, yaw=LEFT),
              _event("OBSTACLE", "C", msg="Obstacle detected in upper aisle at (5.0, 6.5)"),
              ),

        _step(0.5, "C rerouting via lower aisle",
              _robot("C", 6.0, 6.5, bat=85, status="REROUTING", task="T03", vel=0.0, yaw=DOWN),
              _event("REROUTE", "C", msg="C rerouting via lower aisle to avoid obstacle"),
              ),

        _step(2.0, "C taking alternate path",
              _robot("C", 6.0, 4.0, bat=84, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(2.0, "C on lower aisle heading to S1",
              _robot("C", 4.0, 4.0, bat=83, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(2.0, "C approaching S1",
              _robot("C", 2.5, 2.5, bat=82, status="MOVING", task="T03", vel=0.5, yaw=DOWN),
              ),

        _step(1.5, "C arrived at S1 — task complete",
              _robot("C", 2.0, 1.5, bat=81, status="IDLE", task=None, vel=0.0),
              _task("T03", "S4", "S1", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", "C", task="T03",
                     msg="C completed T03 (rerouted around obstacle)"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 4 — ROBOT FAILURE + TASK REASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════

def _failure_scenario() -> list[dict]:
    """A fails mid-task; its task is reassigned to C."""
    return [
        _step(0.0, "Robots online",
              _robot("A", 2.0, 1.5, bat=30, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=85, status="IDLE"),
              _robot("C", 10.0, 4.0, bat=90, status="IDLE"),
              _network("NORMAL", latency=10, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _task("T01", "S1", "S3", robot="A", status="ASSIGNED"),
              _task("T02", "S3", "S2", robot="B", status="ASSIGNED"),
              ),

        _step(1.0, "A and B start tasks",
              _robot("A", 3.0, 1.5, bat=28, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 8.0, 1.5, bat=84, status="MOVING", task="T02", vel=0.8, yaw=RIGHT),
              _task("T01", "S1", "S3", robot="A", status="IN_PROGRESS"),
              _task("T02", "S3", "S2", robot="B", status="IN_PROGRESS"),
              ),

        _step(2.0, "A moving — battery low",
              _robot("A", 5.0, 1.5, bat=22, status="MOVING", task="T01", vel=0.6, yaw=RIGHT),
              _robot("B", 10.0, 1.5, bat=83, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _event("INFO", "A", msg="A battery low (22%)"),
              ),

        _step(2.0, "A stops — heartbeat timeout",
              _robot("A", 5.5, 1.5, bat=18, status="MOVING", task="T01", vel=0.1, yaw=RIGHT),
              ),

        _step(1.0, "A failure detected",
              _robot("A", 5.5, 1.5, bat=15, status="FAILED", task="T01", vel=0.0),
              _event("HEARTBEAT_TIMEOUT", "A",
                     msg="No heartbeat from A for 3 seconds"),
              _event("FAILURE", "A", task="T01",
                     msg="A marked FAILED — task T01 needs reassignment"),
              _network("NORMAL", latency=10, loss=0, peers=2),
              ),

        _step(1.5, "T01 reassigned to C",
              _task("T01", "S1", "S3", robot="A", status="FAILED"),
              _task("T01", "S1", "S3", robot="C", status="REASSIGNED"),
              _robot("C", 10.0, 4.0, bat=89, status="MOVING", task="T01", vel=0.8, yaw=LEFT),
              _event("REASSIGNMENT", "C", related="A", task="T01",
                     msg="T01 reassigned from A to C"),
              ),

        _step(2.0, "C heading to continue T01",
              _robot("C", 7.0, 4.0, bat=88, status="MOVING", task="T01", vel=0.8, yaw=LEFT),
              _robot("B", 8.0, 4.0, bat=82, status="MOVING", task="T02", vel=0.8, yaw=LEFT),
              ),

        _step(2.0, "B arriving at S2",
              _robot("B", 4.0, 5.5, bat=81, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 5.0, 2.5, bat=87, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              ),

        _step(2.0, "B completes T02, C continuing T01",
              _robot("B", 2.0, 6.5, bat=80, status="IDLE", vel=0.0),
              _task("T02", "S3", "S2", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", "B", task="T02", msg="B completed T02"),
              _robot("C", 8.0, 1.5, bat=86, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              ),

        _step(2.0, "C completes T01",
              _robot("C", 10.0, 1.5, bat=85, status="IDLE", task=None, vel=0.0),
              _task("T01", "S1", "S3", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", "C", task="T01",
                     msg="C completed T01 (reassigned from failed A)"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 5 — NETWORK DEGRADATION (optional)
# ═══════════════════════════════════════════════════════════════════════════

def _network_scenario() -> list[dict]:
    """Simulated network degradation and recovery."""
    return [
        _step(0.0, "Robots online — network normal",
              _robot("A", 2.0, 4.0, bat=95, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=88, status="IDLE"),
              _robot("C", 10.0, 4.0, bat=92, status="IDLE"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              ),

        _step(2.0, "Robots moving normally",
              _robot("A", 3.5, 4.0, bat=94, status="MOVING", vel=0.8, yaw=RIGHT),
              _robot("B", 7.0, 1.5, bat=87, status="MOVING", vel=0.8, yaw=RIGHT),
              ),

        _step(2.0, "Network degradation begins",
              _network("DEGRADED", latency=150, loss=8.5, peers=3),
              _event("NETWORK_DEGRADED", msg="Network latency spike: 150ms, 8.5% loss"),
              ),

        _step(2.0, "Degradation worsening",
              _network("DEGRADED", latency=320, loss=15.0, peers=2),
              _event("NETWORK_DEGRADED",
                     msg="Network worsening: 320ms latency, 15% loss, 1 peer unreachable"),
              _robot("A", 5.0, 4.0, bat=93, status="MOVING", vel=0.4, yaw=RIGHT),
              ),

        _step(3.0, "Network recovering",
              _network("DEGRADED", latency=80, loss=3.0, peers=3),
              _event("INFO", msg="Network recovering: 80ms latency, all peers visible"),
              ),

        _step(2.0, "Network fully recovered",
              _network("NORMAL", latency=14, loss=0, peers=3),
              _event("NETWORK_RECOVERED", msg="Network returned to NORMAL"),
              _robot("A", 7.0, 4.0, bat=92, status="MOVING", vel=0.8, yaw=RIGHT),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO 6 — FULL DEMO (sequential combination)
# ═══════════════════════════════════════════════════════════════════════════

def _full_demo_scenario() -> list[dict]:
    """
    End-to-end demonstration combining all key events:
    1. Robots come online
    2. Tasks assigned, normal movement
    3. Intersection conflict at I1 (A wins, B waits)
    4. Reservation release, B proceeds
    5. Obstacle → C reroutes
    6. Robot A failure → task reassignment
    7. Final task completions
    """
    return [
        # ── 1. INITIALISATION ───────────────────────────────────────────
        _step(0.0, "All robots online",
              _robot("A", 2.0, 4.0, bat=95, status="IDLE"),
              _robot("B", 6.0, 1.5, bat=88, status="IDLE"),
              _robot("C", 10.0, 4.0, bat=92, status="IDLE"),
              _network("NORMAL", latency=12, loss=0, peers=3),
              _reserve("I1", None, "FREE"),
              _reserve("I2", None, "FREE"),
              _event("INFO", msg="Dashboard started — 3 robots online"),
              ),

        # ── 2. TASKS ANNOUNCED + ASSIGNED ───────────────────────────────
        _step(2.0, "Tasks announced and assigned",
              _task("T01", "S1", "S3", robot="A", status="ASSIGNED"),
              _task("T02", "S3", "S2", robot="B", status="ASSIGNED"),
              _task("T03", "S4", "S1", robot="C", status="ASSIGNED"),
              _robot("A", 2.0, 4.0, bat=95, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _robot("B", 6.0, 1.5, bat=88, status="MOVING", task="T02", vel=0.8, yaw=RIGHT),
              _robot("C", 10.0, 4.0, bat=92, status="MOVING", task="T03", vel=0.8, yaw=UP),
              _event("INFO", "A", task="T01", msg="A assigned T01: S1→S3"),
              _event("INFO", "B", task="T02", msg="B assigned T02: S3→S2"),
              _event("INFO", "C", task="T03", msg="C assigned T03: S4→S1"),
              ),

        # ── 3. MOVEMENT TOWARD PICKUPS ──────────────────────────────────
        _step(1.5, "Moving to pickups",
              _robot("A", 2.0, 2.8, bat=94, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _robot("B", 8.0, 1.5, bat=87, status="MOVING", task="T02", vel=0.8, yaw=RIGHT),
              _robot("C", 10.0, 5.5, bat=91, status="MOVING", task="T03", vel=0.8, yaw=UP),
              ),

        _step(1.5, "At pickups — tasks in progress",
              _robot("A", 2.0, 1.5, bat=93, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 10.0, 1.5, bat=86, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 10.0, 6.5, bat=90, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              _task("T01", "S1", "S3", robot="A", status="IN_PROGRESS"),
              _task("T02", "S3", "S2", robot="B", status="IN_PROGRESS"),
              _task("T03", "S4", "S1", robot="C", status="IN_PROGRESS"),
              ),

        # ── 4. INTERSECTION CONFLICT ────────────────────────────────────
        _step(1.5, "A and B approaching I1 — intents declared",
              _robot("A", 3.5, 3.0, bat=92, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("B", 5.5, 2.5, bat=85, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 8.5, 6.5, bat=89, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              _intent("A", "I1", eta=2.5),
              _intent("B", "I1", eta=2.8),
              _event("INFO", "A", resource="I1", msg="A declares intent for I1 (ETA 2.5s)"),
              _event("INFO", "B", resource="I1", msg="B declares intent for I1 (ETA 2.8s)"),
              ),

        _step(1.5, "CONFLICT at I1",
              _robot("A", 4.5, 3.5, bat=91, status="MOVING", task="T01", vel=0.5, yaw=RIGHT),
              _robot("B", 5.0, 3.2, bat=84, status="MOVING", task="T02", vel=0.5, yaw=UP),
              _event("CONFLICT", "A", related="B", resource="I1",
                     msg="Conflict detected at I1 between A and B"),
              ),

        _step(0.5, "A wins priority — B must wait",
              _event("WINNER", "A", related="B", resource="I1",
                     msg="A wins priority at I1 (lower ETA: 2.5s vs 2.8s)"),
              _reserve("I1", "A", "ACTIVE"),
              _event("RESERVATION", "A", resource="I1",
                     msg="I1 reserved by A"),
              _robot("B", 5.0, 3.2, bat=84, status="WAITING", task="T02", vel=0.0),
              _event("WAIT", "B", resource="I1",
                     msg="B waiting for I1 (held by A)"),
              ),

        _step(2.0, "A passes through I1",
              _robot("A", 5.5, 4.0, bat=90, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _robot("C", 7.0, 6.5, bat=88, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        _step(1.5, "A clears I1 — reservation released — B proceeds",
              _robot("A", 7.0, 4.0, bat=89, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              _clear_intent("A"),
              _release("I1"),
              _event("RELEASE", "A", resource="I1", msg="A cleared I1 — reservation released"),
              _robot("B", 5.0, 4.0, bat=83, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _clear_intent("B"),
              _event("INFO", "B", resource="I1", msg="B proceeds through I1"),
              ),

        # ── 5. OBSTACLE + REROUTE ──────────────────────────────────────
        _step(1.5, "Obstacle detected ahead of C",
              _robot("C", 6.0, 6.5, bat=87, status="MOVING", task="T03", vel=0.1, yaw=LEFT),
              _event("OBSTACLE", "C",
                     msg="Obstacle detected in upper aisle at (5.0, 6.5)"),
              ),

        _step(0.5, "C rerouting via I2",
              _robot("C", 6.0, 6.5, bat=87, status="REROUTING", task="T03", vel=0.0, yaw=DOWN),
              _event("REROUTE", "C",
                     msg="C rerouting via lower aisle to avoid obstacle"),
              ),

        _step(2.0, "C on alternate route, A continuing",
              _robot("A", 8.5, 3.0, bat=88, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _robot("B", 4.0, 5.5, bat=82, status="MOVING", task="T02", vel=0.8, yaw=UP),
              _robot("C", 6.0, 4.0, bat=86, status="MOVING", task="T03", vel=0.8, yaw=LEFT),
              ),

        # ── 6. ROBOT A FAILURE ─────────────────────────────────────────
        _step(2.0, "A slowing — battery critical",
              _robot("A", 9.5, 2.0, bat=12, status="MOVING", task="T01", vel=0.3, yaw=DOWN),
              _robot("C", 4.0, 3.0, bat=85, status="MOVING", task="T03", vel=0.8, yaw=DOWN),
              _event("INFO", "A", msg="A battery critical (12%)"),
              ),

        _step(1.5, "A failure — heartbeat lost",
              _robot("A", 9.5, 2.0, bat=8, status="FAILED", task="T01", vel=0.0),
              _event("HEARTBEAT_TIMEOUT", "A",
                     msg="No heartbeat from A for 3 seconds"),
              _event("FAILURE", "A", task="T01",
                     msg="A marked FAILED — task T01 needs reassignment"),
              _network("NORMAL", latency=12, loss=0, peers=2),
              ),

        _step(1.5, "T01 reassigned to B",
              _task("T01", "S1", "S3", robot="B", status="REASSIGNED"),
              _event("REASSIGNMENT", "B", related="A", task="T01",
                     msg="T01 reassigned from A (FAILED) to B"),
              _robot("B", 2.5, 6.0, bat=81, status="MOVING", task="T02", vel=0.8, yaw=DOWN),
              ),

        # ── 7. TASK COMPLETIONS ────────────────────────────────────────
        _step(2.0, "B completes T02",
              _robot("B", 2.0, 6.5, bat=80, status="IDLE", vel=0.0),
              _task("T02", "S3", "S2", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", "B", task="T02", msg="B completed T02"),
              _robot("C", 3.0, 1.5, bat=84, status="MOVING", task="T03", vel=0.5, yaw=DOWN),
              ),

        _step(1.5, "C completes T03",
              _robot("C", 2.0, 1.5, bat=83, status="IDLE", task=None, vel=0.0),
              _task("T03", "S4", "S1", robot="C", status="COMPLETED"),
              _event("TASK_COMPLETED", "C", task="T03",
                     msg="C completed T03 (rerouted around obstacle)"),
              ),

        _step(1.0, "B picks up reassigned T01",
              _robot("B", 2.0, 4.0, bat=79, status="MOVING", task="T01", vel=0.8, yaw=DOWN),
              _task("T01", "S1", "S3", robot="B", status="IN_PROGRESS"),
              ),

        _step(2.0, "B heading to S3 with T01",
              _robot("B", 5.0, 2.0, bat=78, status="MOVING", task="T01", vel=0.8, yaw=RIGHT),
              ),

        _step(2.0, "B arriving at S3",
              _robot("B", 8.5, 1.5, bat=77, status="MOVING", task="T01", vel=0.5, yaw=RIGHT),
              ),

        _step(1.5, "B completes T01 — all tasks done",
              _robot("B", 10.0, 1.5, bat=76, status="IDLE", task=None, vel=0.0),
              _task("T01", "S1", "S3", robot="B", status="COMPLETED"),
              _event("TASK_COMPLETED", "B", task="T01",
                     msg="B completed T01 (reassigned from failed A)"),
              _event("INFO", msg="All 3 tasks completed — demo scenario finished"),
              ),
    ]


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════

AVAILABLE_SCENARIOS = [
    "normal", "conflict", "reroute", "failure", "network", "full_demo",
]


def get_scenario(name: str) -> list[dict]:
    """Return the step list for the named scenario.

    Falls back to ``normal`` if the name is unrecognised.
    """
    _scenarios = {
        "normal":    _normal_scenario,
        "conflict":  _conflict_scenario,
        "reroute":   _reroute_scenario,
        "failure":   _failure_scenario,
        "network":   _network_scenario,
        "full_demo": _full_demo_scenario,
    }
    builder = _scenarios.get(name, _normal_scenario)
    return builder()
