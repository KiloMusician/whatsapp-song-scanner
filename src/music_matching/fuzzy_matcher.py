"""Fuzzy string matching for song titles and artists."""
from thefuzz import fuzz
from typing import List, Dict, Tuple
from config.settings import MUSIC_MATCHING_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FuzzyMatcher:
    """Fuzzy string matching for songs."""
    
    def __init__(self):
        """Initialize fuzzy matcher."""
        self.min_score = MUSIC_MATCHING_CONFIG['fuzzy_matching']['min_match_score']
        logger.info(f"Fuzzy matcher initialized with min_score={self.min_score}")
    
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
        
        return score
    
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
        
        return score
    
    def rank_candidates(
        self,
        query_title: str,
        query_artist: str,
        candidates: List[Dict]
    ) -> List[Dict]:
        """Rank candidates by match quality.
        
        Args:
            query_title: Query song title
            query_artist: Query artist name (optional)
            candidates: List of candidate songs from MusicBrainz
            
        Returns:
            Ranked list of candidates with scores
        """
        scored_candidates = []
        
        for candidate in candidates:
            candidate_title = candidate.get('title', '')
            
            # Get primary artist name
            candidate_artist = ''
            if candidate.get('artist_credits'):
                candidate_artist = candidate['artist_credits'][0].get('name', '')
            
            # Calculate title match score
            title_score = self.match_title(query_title, candidate_title)
            
            # Calculate artist match score if we have artist info
            artist_score = 0
            if query_artist and candidate_artist:
                artist_score = self.match_artist(query_artist, candidate_artist)
            
            # Calculate combined score
            # Title is weighted more heavily (70%) than artist (30%)
            if query_artist:
                combined_score = (title_score * 0.7) + (artist_score * 0.3)
            else:
                combined_score = title_score
            
            # Add MusicBrainz search score as a bonus
            mb_score = candidate.get('score', 0)
            final_score = (combined_score * 0.8) + (mb_score * 0.2)
            
            scored_candidates.append({
                **candidate,
                'title_match_score': title_score,
                'artist_match_score': artist_score,
                'combined_match_score': combined_score,
                'final_score': final_score
            })
        
        # Sort by final score (descending)
        scored_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Filter by minimum score
        filtered = [c for c in scored_candidates if c['final_score'] >= self.min_score]
        
        # Limit to max candidates
        max_candidates = MUSIC_MATCHING_CONFIG['fuzzy_matching']['max_candidates']
        return filtered[:max_candidates]
    
    def get_best_match(
        self,
        query_title: str,
        query_artist: str,
        candidates: List[Dict]
    ) -> Tuple[Optional[Dict], float]:
        """Get the best matching candidate.
        
        Args:
            query_title: Query song title
            query_artist: Query artist name (optional)
            candidates: List of candidate songs
            
        Returns:
            Tuple of (best_match, confidence_score)
        """
        ranked = self.rank_candidates(query_title, query_artist, candidates)
        
        if not ranked:
            return None, 0.0
        
        best = ranked[0]
        confidence = best['final_score']
        
        logger.info(
            f"Best match: {best['title']} "
            f"(score={confidence:.2f})"
        )
        
        return best, confidence

# SINGLETON INSTANCE
fuzzy_matcher = FuzzyMatcher()
