"""Extract keywords for searching."""

import re
from typing import List, Set
from src.utils.logger import get_logger

logger = get_logger(__name__)


class KeywordExtractor:
    """Extract search keywords from text."""

    def __init__(self):
        """Initialize keyword extractor."""
        # Stop words to remove
        self.stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "been",
            "be",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "play",
            "song",
            "music",
            "request",
            "please",
            "want",
            "like",
            "hear",
            "listen",
        }

    def extract(self, text: str) -> List[str]:
        """Extract keywords from text.

        Args:
            text: Input text

        Returns:
            List of keywords
        """
        if not text:
            return []

        # Convert to lowercase
        text = text.lower()

        # Remove punctuation except hyphens
        text = re.sub(r"[^\w\s\-]", "", text)

        # Split into words
        words = text.split()

        # Filter stop words and short words
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]

        return keywords

    def extract_unique(self, text: str) -> Set[str]:
        """Extract unique keywords from text.

        Args:
            text: Input text

        Returns:
            Set of unique keywords
        """
        return set(self.extract(text))


# SINGLETON INSTANCE
keyword_extractor = KeywordExtractor()
