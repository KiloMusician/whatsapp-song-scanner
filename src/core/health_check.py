"""Health check endpoints."""

from typing import Dict
from src.core.state_manager import state_manager
from src.radiodj_integration.radiodj_client import radiodj_client
from src.utils.cache import cache_manager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class HealthCheck:
    """Health check service."""

    def __init__(self):
        """Initialize health check."""
        self.state = state_manager
        self.radiodj = radiodj_client
        self.cache = cache_manager

    def get_health(self) -> Dict:
        """Get health status.

        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "timestamp": state_manager.state["started_at"].isoformat(),
            "uptime_seconds": state_manager.get_uptime_seconds(),
            "components": {},
        }

        # Check cache
        health["components"]["cache"] = {
            "status": "healthy" if self.cache.redis_client else "unhealthy",
            "connected": bool(self.cache.redis_client),
        }

        # Check RadioDJ
        radiodj_status = self.radiodj.validate_connection()
        health["components"]["radiodj"] = {
            "status": "healthy" if any(radiodj_status.values()) else "unhealthy",
            "api_available": radiodj_status["api_available"],
            "database_available": radiodj_status["database_available"],
        }

        # Overall status
        unhealthy_components = [
            name for name, comp in health["components"].items() if comp["status"] == "unhealthy"
        ]

        if unhealthy_components:
            health["status"] = "degraded"
            health["unhealthy_components"] = unhealthy_components

        return health

    def get_metrics(self) -> Dict:
        """Get application metrics.

        Returns:
            Metrics dictionary
        """
        state = self.state.get_state()

        metrics = {
            "uptime_seconds": self.state.get_uptime_seconds(),
            "status": state["status"],
            "last_scan": state["last_scan"].isoformat() if state["last_scan"] else None,
            "last_sync": state["last_sync"].isoformat() if state["last_sync"] else None,
            "statistics": state["stats"],
        }

        return metrics


# SINGLETON INSTANCE
health_check = HealthCheck()
