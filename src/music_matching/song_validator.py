"""Song match validation logic."""

from typing import Dict, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SongValidator:
    """Validate matched songs."""

    def __init__(self):
        """Initialize song validator."""
        self.min_title_length = 2
        self.max_title_length = 200
        self.min_confidence = 70.0

    def validate(self, match: Dict, confidence: float) -> Tuple[bool, str]:
        """Validate a song match.

        Args:
            match: Matched song dictionary
            confidence: Match confidence score

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check confidence threshold
        if confidence < self.min_confidence:
            return False, f"Confidence too low: {confidence:.2f}"

        # Check if we have required fields
        if not match.get("title"):
            return False, "Missing title"

        # Check title length
        title_len = len(match["title"])
        if title_len < self.min_title_length:
            return False, f"Title too short: {title_len} chars"

        if title_len > self.max_title_length:
            return False, f"Title too long: {title_len} chars"

        # Check if we have artist info
        has_artist = bool(match.get("artist_credits"))
        if not has_artist:
            logger.warning("Match has no artist info: %s", match["title"])

        # Check if we have MusicBrainz ID
        if not match.get("musicbrainz_id"):
            return False, "Missing MusicBrainz ID"

        # All checks passed
        return True, "Valid"

    def should_auto_approve(self, match: Dict, confidence: float) -> bool:
        """Determine if match should be auto-approved.

        Args:
            match: Matched song dictionary
            confidence: Match confidence score

        Returns:
            True if should auto-approve
        """
        # High confidence threshold for auto-approval
        AUTO_APPROVE_THRESHOLD = 90.0

        is_valid, _ = self.validate(match, confidence)
        if not is_valid:
            return False

        # Must have artist info for auto-approval
        if not match.get("artist_credits"):
            return False

        # Must meet confidence threshold
        if confidence < AUTO_APPROVE_THRESHOLD:
            return False

        logger.info("Auto-approving: %s (confidence=%.2f)", match["title"], confidence)
        return True


# SINGLETON INSTANCE
song_validator = SongValidator()
