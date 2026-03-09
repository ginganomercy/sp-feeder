"""
Logging configuration for Smart Pet Feeder application.

Provides centralized logging setup with different handlers for development and production.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """
    Configure application logging with console and file handlers.

    Falls back to stdout-only logging if log file is not writable
    (e.g., running in Docker with restricted volume mounts).

    Args:
        app: Flask application instance
    """
    # Set log level based on environment
    log_level = logging.DEBUG if app.config.get("DEBUG", False) else logging.INFO

    # Create formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler — always active (Docker captures stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # File handler with rotation — optional, graceful fallback on PermissionError
    try:
        log_dir = os.environ.get("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, "petfeeder.log")

        file_handler = RotatingFileHandler(
            log_path, maxBytes=10 * 1024 * 1024, backupCount=10  # 10MB
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        app.logger.debug(f"File logging enabled: {log_path}")
    except (PermissionError, OSError) as e:
        # Typical in Docker with restricted volumes — stdout-only is fine,
        # Docker captures all stdout via `docker logs` or log drivers
        logging.warning(f"File logging disabled (stdout only): {e}")

    # Configure Flask app logger
    app.logger.setLevel(log_level)

    # Silence werkzeug request logs in production
    if not app.config.get("DEBUG", False):
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.logger.info("=" * 60)
    app.logger.info("Smart Pet Feeder Application Starting")
    app.logger.info(f"Environment: {'Development' if app.debug else 'Production'}")
    app.logger.info(f"Log Level: {logging.getLevelName(log_level)}")
    app.logger.info("=" * 60)


def get_logger(name):
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
