# P5 — Distributed Task Allocation & Failure Recovery

**End-to-End MVP: COMPLETE**

This is the standalone P5 subsystem for the SYNERGY decentralised
multi-AMR warehouse project.

---

## What This Module Does

| Responsibility | Status |
|---|---|
| Distributed task allocation | ✅ MVP COMPLETE |
| Robot failure detection | ✅ MVP COMPLETE |
| Task recovery after failure | ✅ MVP COMPLETE |
| Blocked-aisle resilience | ⏳ Phase 15 |
| **Phase 1 foundation** | ✅ COMPLETE |

---

## Quick Start

### Run the standalone demo

```bash
cd p5_task_failure
python simulation/standalone_demo.py
```

Expected output:
```
P5 STANDALONE DEMO  —  END-TO-END MVP
...
END-TO-END MVP  ✓  COMPLETE
```

### Run the test suite

```bash
cd p5_task_failure
python -m pytest tests/ -v
```

---

## Project Structure

```
p5_task_failure/
├── README.md                  This file
├── pyproject.toml             Package configuration
├── p5/
│   ├── models/                Core data models (Robot, Task, Bid, Heartbeat, Events)
│   ├── allocation/            Bid calculation stubs (Phase 3–5)
│   ├── failure/               Failure detection stubs (Phase 9–10)
│   ├── recovery/              Task recovery stubs (Phase 11–14)
│   ├── manager/               Task manager stub (Phase 6)
│   └── adapters/              Pure-Python Protocol interfaces
├── tests/                     pytest unit tests (no external deps)
├── simulation/                Terminal-only standalone demo
└── docs/
    ├── p5_architecture.md     Architecture + diagrams
    └── p5_interface_contract.md  Internal + external interface contract
```

---

## Independence

| External System | Core Dependency |
|---|---|
| ROS 2 | ❌ NONE in core |
| Gazebo | ❌ NONE |
| Nav2 | ❌ NONE in core |
| UI / Dashboard | ❌ NONE |
| Other team's code | ❌ NONE |
| Python stdlib | ✅ only dependency |

External systems connect through the adapter layer in `p5/adapters/`.

---

## Documentation

- [Architecture](docs/p5_architecture.md)
- [Interface Contract](docs/p5_interface_contract.md)
