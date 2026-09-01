"""
SYNERGY Dashboard — Standalone Mock Telemetry Adapter
=====================================================

Wraps FleetSimulator to provide a standard adapter interface identical
to the ROS 2 adapter.
"""

import logging
from data_store import DataStore
from simulator.fleet_simulator import FleetSimulator

logger = logging.getLogger("synergy.adapters.mock")


class MockAdapter:
    """Mock telemetry adapter for standalone demonstration mode."""

    def __init__(self, data_store: DataStore, scenario: str = "full_demo", speed: float = 1.0):
        self.data_store = data_store
        self.simulator = FleetSimulator(
            data_store=self.data_store,
            speed_multiplier=speed,
            loop=True,
        )
        self.simulator.load_scenario(scenario)

    def start(self) -> None:
        """Start mock scenario playback thread."""
        self.simulator.start()
        logger.info("MockAdapter started")

    def stop(self) -> None:
        """Stop mock scenario playback."""
        self.simulator.stop()
        logger.info("MockAdapter stopped")

    def is_active(self) -> bool:
        return self.simulator.is_running()

    def set_scenario(self, scenario_name: str) -> None:
        self.simulator.load_scenario(scenario_name)
        self.simulator.start()
