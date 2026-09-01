"""
SYNERGY Dashboard — Event Audit & JSON Log Exporter
===================================================

Saves recorded fleet coordination event logs to JSON / JSONL files
under `data/events/` so experiment runs can be audited, replayed, or inspected.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

import config
from models import Event

logger = logging.getLogger("synergy.event_logger")


class EventAuditLogger:
    """Exports event logs to JSON and JSONL format."""

    def __init__(self, events_dir: str = config.EVENTS_DIR):
        self.events_dir = events_dir
        os.makedirs(self.events_dir, exist_ok=True)

    def export_json(self, events: List[Dict[str, Any]], run_id: str) -> str:
        """Export event log to JSON format."""
        file_path = os.path.join(self.events_dir, f"events_{run_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"run_id": run_id, "events": events}, f, indent=2)
        logger.info(f"Exported JSON events to {file_path}")
        return file_path

    def export_jsonl(self, events: List[Dict[str, Any]], run_id: str) -> str:
        """Export event log to JSON Lines (JSONL) format."""
        file_path = os.path.join(self.events_dir, f"events_{run_id}.jsonl")
        with open(file_path, "w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev) + "\n")
        logger.info(f"Exported JSONL events to {file_path}")
        return file_path
