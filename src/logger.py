"""Centralized logging configuration for LG GeoView."""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "lg_geoview.log")


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # File handler with rotation
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s")
    file_handler.setFormatter(file_fmt)
    logger.addHandler(file_handler)

    return logger
