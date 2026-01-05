"""Unit tests for text processing modules."""
from src.text_processing.text_cleaner import text_cleaner
from src.text_processing.message_parser import message_parser
from src.text_processing.keyword_extractor import keyword_extractor


class TestTextCleaner:
    """Test text cleaning functionality."""

    def test_clean_basic_text(self):
        """Test basic text cleaning."""
        text = "Hello  World   with  extra   spaces"
        cleaned = text_cleaner.clean(text)
        assert "  " not in cleaned
        assert cleaned == "Hello World with extra spaces"

    def test_remove_urls(self):
        """Test URL removal."""
        text = "Check this out http://example.com and this https://test.com"
        cleaned = text_cleaner.clean(text)
        assert "http://" not in cleaned
        assert "https://" not in cleaned

    def test_remove_emojis(self):
        """Test emoji removal."""
        text = "Great song! 🎵🎶 Love it! ❤️"
        cleaned = text_cleaner.clean(text)
        assert "🎵" not in cleaned
        assert "❤️" not in cleaned

    def test_normalize(self):
        """Test text normalization."""
        text = "The SONG by the ARTIST"
        normalized = text_cleaner.normalize(text)
        assert normalized == "song by artist"


class TestMessageParser:
    """Test message parsing functionality."""

    def test_parse_play_command(self):
        """Test parsing 'play' command."""
        message = "play Bohemian Rhapsody by Queen"
        candidates = message_parser.parse(message)

        assert len(candidates) > 0
        assert candidates[0]["title"] is not None
        assert "bohemian" in candidates[0]["title"].lower()

    def test_parse_with_confidence(self):
        """Test confidence scoring."""
        message = "play Song Title by Artist Name"
        candidates = message_parser.parse(message)

        if candidates:
            assert "confidence" in candidates[0]
            assert 0 <= candidates[0]["confidence"] <= 100

    def test_no_match(self):
        """Test message with no song request."""
        message = "Hello, how are you?"
        candidates = message_parser.parse(message)

        assert len(candidates) == 0


class TestKeywordExtractor:
    """Test keyword extraction."""

    def test_extract_basic_keywords(self):
        """Test basic keyword extraction."""
        text = "play the song called Wonderwall"
        keywords = keyword_extractor.extract(text)

        assert "wonderwall" in keywords
        assert "the" not in keywords  # Stop word
        assert "play" not in keywords  # Stop word

    def test_extract_unique(self):
        """Test unique keyword extraction."""
        text = "song song play play test"
        unique = keyword_extractor.extract_unique(text)

        assert len(unique) == 1  # Only 'test' after filtering
        assert "test" in unique
