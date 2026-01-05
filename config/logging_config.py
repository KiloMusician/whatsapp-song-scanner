"""Logging configuration."""
import logging
import logging.handlers
import sys
from pathlib import Path
from config.settings import APP_CONFIG

# CREATE LOGS DIRECTORY
log_dir = APP_CONFIG['data_dir'] / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

# LOGGING FORMAT
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(name: str = None, level: str = None):
    """Setup logging configuration.
    
    Args:
        name: Logger name (defaults to root logger)
        level: Log level (defaults to APP_CONFIG['log_level'])
    
    Returns:
        Configured logger instance
    """
    log_level = level or APP_CONFIG['log_level']
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # CONSOLE HANDLER
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if APP_CONFIG['debug'] else logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # FILE HANDLER (ALL LOGS)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # ERROR HANDLER (ERROR LOGS ONLY)
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    # SCAN HISTORY HANDLER (CUSTOM)
    scan_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'scan_history.log',
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5
    )
    scan_handler.setLevel(logging.INFO)
    scan_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    scan_handler.setFormatter(scan_formatter)
    
    # Create separate logger for scan history
    scan_logger = logging.getLogger('scan_history')
    scan_logger.addHandler(scan_handler)
    
    return logger

# CREATE DEFAULT LOGGER
app_logger = setup_logging('whatsapp_song_scanner')
