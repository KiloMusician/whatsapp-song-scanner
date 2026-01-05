"""General helper functions."""

import re
from typing import Optional
from datetime import datetime


def clean_text(text: str) -> str:
    """Clean and normalize text.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = " ".join(text.split())

    # Remove special characters but keep basic punctuation
    text = re.sub(r"[^\w\s\-\'\".,!?]", "", text)

    return text.strip()


def normalize_string(s: str) -> str:
    """Normalize string for comparison.

    Args:
        s: Input string

    Returns:
        Normalized string
    """
    if not s:
        return ""

    # Convert to lowercase
    s = s.lower()

    # Remove articles
    s = re.sub(r"\b(the|a|an)\b", "", s)

    # Remove extra whitespace
    s = " ".join(s.split())

    # Remove special characters
    s = re.sub(r"[^\w\s]", "", s)

    return s.strip()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse timestamp string to datetime.

    Args:
        timestamp_str: Timestamp string

    Returns:
        Datetime object or None
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue

    return None


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length.

    Args:
        s: Input string
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if not s or len(s) <= max_length:
        return s

    return s[: max_length - len(suffix)] + suffix
