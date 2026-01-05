"""Fuzzy string matching for song titles and artists."""

from thefuzz import fuzz
from typing import List, Dict, Tuple, Optional, Any, cast
from config.settings import MUSIC_MATCHING_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FuzzyMatcher:
    """Fuzzy string matching for songs."""

    def __init__(self):
        """Initialize fuzzy matcher."""
        self.config: Dict[str, Any] = cast(
            Dict[str, Any], MUSIC_MATCHING_CONFIG.get("fuzzy_matching", {})
        )
        self.min_score: int = int(self.config.get("min_match_score", 80))
        logger.info(
            "Fuzzy matcher initialized with min_score=%s",
            self.min_score,
        )

    def match_title(self, query: str, candidate: str) -> int:
        """Match song titles using fuzzy matching.

        Args:
            query: Query title
            candidate: Candidate title

        Returns:
            Match score (0-100)
        """
        if not query or not candidate:
            return 0

        # Normalize both strings
        query = query.lower().strip()
        candidate = candidate.lower().strip()

        # Use token sort ratio for best results
        score = fuzz.token_sort_ratio(query, candidate)

        return int(score)

    def match_artist(self, query: str, candidate: str) -> int:
        """Match artist names using fuzzy matching.

        Args:
            query: Query artist
            candidate: Candidate artist

        Returns:
            Match score (0-100)
        """
        if not query or not candidate:
            return 0

        # Normalize both strings
        query = query.lower().strip()
        candidate = candidate.lower().strip()

        # Use token set ratio for artist names
        score = fuzz.token_set_ratio(query, candidate)

        return int(score)

    def rank_candidates(
        self, query_title: str, query_artist: str, candidates: List[Dict]
    ) -> List[Tuple[Dict, float]]:
        """Rank candidates by match quality.

        Returns (candidate, final_score) tuples sorted by score.
        """
        scored_candidates: List[Tuple[Dict, float]] = []

        for candidate in candidates:
            candidate_title = candidate.get("title", "")

            # Primary artist name (supports MusicBrainz and simple dicts)
            candidate_artist = ""
            if candidate.get("artist_credits"):
                candidate_artist = candidate["artist_credits"][0].get("name", "")
            elif candidate.get("artist"):
                candidate_artist = candidate.get("artist", "")

            # Scores
            title_score = self.match_title(query_title, candidate_title)

            artist_score = 0
            if query_artist and candidate_artist:
                artist_score = self.match_artist(query_artist, candidate_artist)

            combined_score = (
                (title_score * 0.7) + (artist_score * 0.3) if query_artist else title_score
            )

            # MusicBrainz search score bonus
            mb_score = candidate.get("score", 50)
            final_score = (combined_score * 0.8) + (mb_score * 0.2)

            scored_candidates.append(
                (
                    {
                        **candidate,
                        "title_match_score": title_score,
                        "artist_match_score": artist_score,
                        "combined_match_score": combined_score,
                        "final_score": final_score,
                    },
                    final_score,
                )
            )

        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        filtered = [c for c in scored_candidates if c[1] >= self.min_score]

        max_candidates: int = int(self.config.get("max_candidates", 5))
        return filtered[:max_candidates]

    def get_best_match(
        self, query_title: str, query_artist: str, candidates: List[Dict]
    ) -> Tuple[Optional[Dict], float]:
        """Get the best matching candidate."""
        ranked = self.rank_candidates(query_title, query_artist, candidates)

        if not ranked:
            return None, 0.0

        best_candidate, confidence = ranked[0]

        logger.info(
            "Best match: %s (score=%.2f)",
            best_candidate["title"],
            confidence,
        )

        return best_candidate, confidence


# SINGLETON INSTANCE


fuzzy_matcher = FuzzyMatcher()
