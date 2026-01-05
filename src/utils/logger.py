"""Unified logging utilities."""
from config.logging_config import setup_logging, app_logger

__all__ = ['setup_logging', 'app_logger', 'get_logger']

def get_logger(name: str):
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return setup_logging(name)
