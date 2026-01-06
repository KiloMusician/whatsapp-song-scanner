"""RadioDJ client for API and database integration."""

import sqlite3
from pathlib import Path
from typing import Dict, Optional, cast

import requests

from config.settings import DATABASE_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RadioDJClient:
    """Client for RadioDJ integration."""

    def __init__(self):
        """Initialize RadioDJ client."""
        self.config = DATABASE_CONFIG["radiodj"]
        self.api_url = self.config["api_url"]
        self.api_key = self.config["api_key"]
        self.db_path = self.config["db_path"]
        self.default_playlist_id = self.config["default_playlist_id"]

        logger.info("RadioDJ client initialized")

    def add_track_via_api(self, artist: str, title: str, playlist_id: Optional[int] = None) -> bool:
        """Add track to RadioDJ queue via API.

        Args:
            artist: Artist name
            title: Song title
            playlist_id: Playlist ID (optional)

        Returns:
            True if successful
        """
        if not self.api_url or not self.api_key:
            logger.warning("RadioDJ API not configured")
            return False

        try:
            endpoint = f"{self.api_url}/addtrack"  # cspell:ignore addtrack
            payload = {
                "artist": artist,
                "title": title,
                "playlist_id": playlist_id or self.default_playlist_id,
                "api_key": self.api_key,
            }

            response = requests.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Added track via API: %s - %s", artist, title)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to add track via API: %s", exc)
            return False

    def find_track_in_library(self, artist: str, title: str) -> Optional[int]:
        """Find track ID in RadioDJ library database.

        Args:
            artist: Artist name
            title: Song title

        Returns:
            Track ID if found, None otherwise
        """
        if not self.db_path or not Path(self.db_path).exists():
            logger.warning("RadioDJ database not configured or not found")
            return None

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Query for track (adjust table/column names based on actual RadioDJ schema)
            query = """
                SELECT ID FROM songs
                WHERE LOWER(artist) = LOWER(?)
                AND LOWER(title) = LOWER(?)
                LIMIT 1
            """

            cursor.execute(query, (artist, title))
            result = cursor.fetchone()
            conn.close()

            if result:
                track_id = cast(int, result[0])
                logger.info("Found track in library: ID=%s", track_id)
                return track_id
            else:
                logger.warning("Track not found in library: %s - %s", artist, title)
                return None

        except sqlite3.DatabaseError as exc:
            logger.error("Error searching RadioDJ database: %s", exc)
            return None

    def add_track_to_queue_db(self, track_id: int) -> bool:
        """Add track to RadioDJ queue via direct database access.

        CAUTION: Direct database access. Backup database before using!

        Args:
            track_id: Track ID from RadioDJ library

        Returns:
            True if successful
        """
        if not self.db_path or not Path(self.db_path).exists():
            logger.warning("RadioDJ database not configured or not found")
            return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert into queue (adjust table/column names based on actual RadioDJ schema)
            # This is a simplified example - actual schema may differ
            query = """
                INSERT INTO queue (songID, queueType, dateAdded)
                VALUES (?, 0, datetime('now'))
            """

            cursor.execute(query, (track_id,))
            conn.commit()
            conn.close()

            logger.info("Added track %s to queue via database", track_id)
            return True

        except sqlite3.DatabaseError as exc:
            logger.error("Error adding track to queue via database: %s", exc)
            return False

    def validate_connection(self) -> Dict[str, bool]:
        """Validate RadioDJ connections.

        Returns:
            Dictionary with connection status
        """
        status = {"api_available": False, "database_available": False}

        # Check API
        if self.api_url:
            try:
                response = requests.get(f"{self.api_url}/health", timeout=5)
                status["api_available"] = response.status_code == 200
            except requests.RequestException:
                status["api_available"] = False

        # Check database
        if self.db_path:
            status["database_available"] = Path(self.db_path).exists()

        logger.info("RadioDJ connection status: %s", status)
        return status


# SINGLETON INSTANCE
radiodj_client = RadioDJClient()
