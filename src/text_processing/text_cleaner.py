"""Text cleaning and normalization."""
import re
from typing import str
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TextCleaner:
    """Clean and normalize WhatsApp message text."""
    
    def __init__(self):
        """Initialize text cleaner."""
        # Common patterns to remove
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{4,6}')
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
    
    def clean(self, text: str) -> str:
        """Clean message text.
        
        Args:
            text: Raw message text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove emails
        text = self.email_pattern.sub('', text)
        
        # Remove phone numbers
        text = self.phone_pattern.sub('', text)
        
        # Remove emojis
        text = self.emoji_pattern.sub('', text)
        
        # Remove WhatsApp system messages
        if text.startswith('‎') or 'Messages and calls are end-to-end encrypted' in text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def normalize(self, text: str) -> str:
        """Normalize text for matching.
        
        Args:
            text: Cleaned text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove common articles
        text = re.sub(r'\b(the|a|an)\b', '', text)
        
        # Remove punctuation except hyphens and apostrophes
        text = re.sub(r'[^\w\s\-\']', '', text)
        
        # Collapse multiple spaces
        text = ' '.join(text.split())
        
        return text.strip()

# SINGLETON INSTANCE
text_cleaner = TextCleaner()
