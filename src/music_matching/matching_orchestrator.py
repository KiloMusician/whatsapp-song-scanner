"""Orchestrate the matching process."""

from typing import Dict, Optional, cast
from sqlalchemy.orm import Session
from src.music_matching.musicbrainz_client import musicbrainz_client
from src.music_matching.fuzzy_matcher import fuzzy_matcher
from src.music_matching.song_validator import song_validator
from src.database.operations import SongOperations, RequestOperations
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MatchingOrchestrator:
    """Orchestrate the complete matching process."""

    def __init__(self):
        """Initialize matching orchestrator."""
        self.musicbrainz = musicbrainz_client
        self.fuzzy = fuzzy_matcher
        self.validator = song_validator

    def match_song(
        self, db: Session, extraction_id: int, title: str, artist: Optional[str] = None
    ) -> Optional[Dict]:
        """Match a song through the complete pipeline.

        Args:
            db: Database session
            extraction_id: Extracted song ID
            title: Song title
            artist: Artist name (optional)

        Returns:
            Matched song dictionary or None
        """
        logger.info("Matching song: %s by %s", title, artist or "unknown")

        # STEP 1: Search MusicBrainz
        candidates = self.musicbrainz.search_song(title, artist)

        if not candidates:
            logger.warning("No candidates found for: %s", title)
            return None

        logger.info("Found %s candidates", len(candidates))

        # STEP 2: Rank and get best match
        best_match, confidence = self.fuzzy.get_best_match(title, artist, candidates)

        if not best_match:
            logger.warning("No suitable match found for: %s", title)
            return None

        # STEP 3: Validate match
        is_valid, reason = self.validator.validate(best_match, confidence)

        if not is_valid:
            logger.warning("Match validation failed: %s", reason)
            return None

        # STEP 4: Store match in database
        artist_name = None
        if best_match.get("artist_credits"):
            artist_name = best_match["artist_credits"][0].get("name")

        matched_song = SongOperations.create_match(
            db=db,
            extraction_id=extraction_id,
            song_title=best_match["title"],
            artist_name=artist_name,
            musicbrainz_id=best_match.get("musicbrainz_id"),
            match_confidence=confidence,
            match_source="musicbrainz",
            match_metadata=best_match,
        )

        # STEP 5: Check if should auto-approve
        if self.validator.should_auto_approve(best_match, confidence):
            SongOperations.verify_match(db, cast(int, matched_song.id), "auto_approve")
            logger.info("Match auto-approved: %s", best_match['title'])

        logger.info(
            "Successfully matched: %s (confidence=%.2f)", best_match['title'], confidence
        )

        return {
            "matched_song_id": matched_song.id,
            "title": best_match["title"],
            "artist": artist_name,
            "confidence": confidence,
            "is_verified": self.validator.should_auto_approve(best_match, confidence),
        }

    def process_extraction(
        self,
        db: Session,
        extraction_id: int,
        title: str,
        artist: str,
        chat_id: str,
        requested_by: str,
    ) -> Optional[int]:
        """Process an extraction and create request if match is good.

        Args:
            db: Database session
            extraction_id: Extracted song ID
            title: Song title
            artist: Artist name
            chat_id: WhatsApp chat ID
            requested_by: Requester identifier

        Returns:
            Request ID if created, None otherwise
        """
        # Match the song
        match_result = self.match_song(db, extraction_id, title, artist)

        if not match_result:
            return None

        # Create song request
        request = RequestOperations.create_request(
            db=db,
            chat_id=chat_id,
            matched_song_id=match_result["matched_song_id"],
            requested_by=requested_by,
            priority=1,
        )

        request_id_int = int(request.id)

        # Auto-approve if match is verified
        if match_result["is_verified"]:
            RequestOperations.approve_request(db, request_id_int)

        logger.info("Created request %s for: %s", request_id_int, match_result['title'])

        return request_id_int


# SINGLETON INSTANCE
matching_orchestrator = MatchingOrchestrator()
