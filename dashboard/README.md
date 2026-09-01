# SYNERGY Dashboard — Monitoring & Evaluation Module

## What Is This?

A **read-only** monitoring dashboard for the SYNERGY decentralized AMR (Autonomous
Mobile Robot) warehouse prototype.  It visualises fleet state, coordination events,
intersection reservations, and experiment metrics — but it **never** controls the
robots.

## Architecture

```
SYNERGY Fleet  (Gazebo / ROS 2 / Mock Simulator)
        │
        ▼
┌──────────────────┐
│ Telemetry Adapter │  ←  mock_adapter  OR  ros2_adapter
└──────────────────┘
        │
        ▼
┌──────────────────┐
│ Normalized Models │  ←  models.py  (RobotState, Event, Task, …)
└──────────────────┘
        │
        ▼
┌──────────────────┐
│   Data Store      │  ←  data_store.py  (thread-safe in-memory state)
└──────────────────┘
      /        \
     ▼          ▼
 Flask API   Metrics / CSV Logging
     │
     ▼
 HTML / CSS / JS  (browser)
```

## Tech Stack

| Layer     | Technology                 |
|-----------|----------------------------|
| Backend   | Python 3, Flask            |
| Frontend  | HTML5, CSS3, Vanilla JS    |
| Map       | HTML Canvas                |
| Data      | JSON (API), CSV (results)  |
| Testing   | pytest                     |

## Quick Start (Standalone / Mock Mode)

```bash
cd dashboard
pip install -r requirements.txt
python run_dashboard.py --mode mock --scenario full_demo
```

Then open **http://localhost:5000** in your browser.

## Project Status

- [x] Phase 0 — Repository inspection, skeleton, README
- [x] Phase 1 — Normalized data models (`models.py`)
- [ ] Phase 2 — Central data store
- [ ] Phase 3 — Mock telemetry simulator
- [ ] Phase 4 — Flask backend / API
- [ ] Phase 5–11 — Frontend (map, cards, events, tasks, network)
- [ ] Phase 12–15 — Metrics engine, experiment logging, comparison UI
- [ ] Phase 16–17 — ROS 2 adapter, integration config
- [ ] Phase 18 — Tests
- [ ] Phase 19 — Failure-safe behaviour
- [ ] Phase 20 — Full documentation

## Important Rule

> **The dashboard is monitoring-only.**
> It must never become the central decision-maker or controller for the robots.
> The decentralized Fleet Coordination Agents remain responsible for all
> coordination decisions.

## License

Internal SYNERGY project — not for public distribution.
