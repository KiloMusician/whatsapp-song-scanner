"""Unit tests for music matching modules."""
import pytest
from src.music_matching.fuzzy_matcher import fuzzy_matcher
from src.music_matching.song_validator import song_validator


class TestFuzzyMatcher:
    """Test fuzzy matching functionality."""
    
    def test_match_title_exact(self):
        """Test exact title match."""
        score = fuzzy_matcher.match_title("Bohemian Rhapsody", "Bohemian Rhapsody")
        assert score >= 95
    
    def test_match_title_partial(self):
        """Test partial title match."""
        score = fuzzy_matcher.match_title("Bohemian Rhapsody", "Bohemian Rhapsody - Remastered")
        assert score >= 70
    
    def test_match_artist(self):
        """Test artist matching."""
        score = fuzzy_matcher.match_artist("Queen", "Queen")
        assert score >= 95
    
    def test_rank_candidates(self):
        """Test candidate ranking."""
        candidates = [
            {'title': 'Bohemian Rhapsody', 'artist': 'Queen', 'musicbrainz_id': '1'},
            {'title': 'Bohemian', 'artist': 'Other', 'musicbrainz_id': '2'},
        ]
        
        ranked = fuzzy_matcher.rank_candidates("Bohemian Rhapsody", "Queen", candidates)
        
        assert len(ranked) > 0
        assert ranked[0][0]['title'] == 'Bohemian Rhapsody'


class TestSongValidator:
    """Test song validation."""
    
    def test_validate_good_match(self):
        """Test validation of good match."""
        match = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'musicbrainz_id': 'test-123'
        }
        
        is_valid, reason = song_validator.validate(match, 90.0)
        assert is_valid
        assert reason == "Valid"
    
    def test_validate_low_confidence(self):
        """Test rejection of low confidence match."""
        match = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'musicbrainz_id': 'test-123'
        }
        
        is_valid, reason = song_validator.validate(match, 50.0)
        assert not is_valid
        assert "Confidence too low" in reason
    
    def test_auto_approve_high_confidence(self):
        """Test auto-approval logic."""
        match = {
            'title': 'Test Song',
            'artist_credits': [{'name': 'Test Artist'}],
            'musicbrainz_id': 'test-123'
        }
        
        should_approve = song_validator.should_auto_approve(match, 95.0)
        assert should_approve
    
    def test_no_auto_approve_missing_artist(self):
        """Test no auto-approval without artist."""
        match = {
            'title': 'Test Song',
            'musicbrainz_id': 'test-123'
        }
        
        should_approve = song_validator.should_auto_approve(match, 95.0)
        assert not should_approve
