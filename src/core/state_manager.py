"""Application state management."""

from datetime import datetime, timezone
from typing import Dict, Any, cast
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StateManager:
    """Manage application state."""

    def __init__(self):
        """Initialize state manager."""
        self.state = {
            "started_at": datetime.now(timezone.utc),
            "status": "initializing",
            "last_scan": None,
            "last_sync": None,
            "stats": {
                "messages_processed": 0,
                "songs_matched": 0,
                "requests_created": 0,
                "requests_synced": 0,
            },
        }
        logger.info("State manager initialized")

    def set_status(self, status: str):
        """Set application status."""
        self.state["status"] = status
        logger.info(f"Application status: {status}")

    def update_last_scan(self):
        """Update last scan timestamp."""
        self.state["last_scan"] = datetime.now(timezone.utc)

    def update_last_sync(self):
        """Update last sync timestamp."""
        self.state["last_sync"] = datetime.now(timezone.utc)

    def increment_stat(self, stat_name: str, amount: int = 1):
        """Increment a statistic."""
        if stat_name in self.state["stats"]:
            self.state["stats"][stat_name] += amount

    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        return cast(Dict[str, Any], self.state.copy())

    def get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        delta = datetime.now(timezone.utc) - cast(datetime, self.state["started_at"])
        return delta.total_seconds()


# SINGLETON INSTANCE
state_manager = StateManager()
