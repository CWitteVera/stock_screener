"""
Logging configuration
"""

import logging
import sys
from pathlib import Path
import os

def setup_logger(name: str = 'stock_screener', level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # Optional: File handler
    try:
        base_dir = Path(__file__).parent.parent
        log_file = os.path.join(base_dir, 'screener.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not setup file logging: {str(e)}")
    
    return logger

# Default logger
logger = setup_logger()
