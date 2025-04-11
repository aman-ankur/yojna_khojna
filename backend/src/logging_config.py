import logging
import logging.config
import sys

# Basic logging configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # Keep existing loggers like uvicorn
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "brief": {
            "format": "%(levelname)s: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "INFO", # Default level for console
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": sys.stdout,
        },
        # Example file handler (can be added later if needed)
        # "file": {
        #     "level": "DEBUG",
        #     "class": "logging.FileHandler",
        #     "formatter": "standard",
        #     "filename": "backend_app.log",
        #     "mode": "a",
        # },
    },
    "loggers": {
        "": { # Root logger
            "handlers": ["console"], # Use console handler by default
            "level": "INFO", # Default level for all loggers
            "propagate": True,
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False, # Don't propagate uvicorn errors to root
        },
        "uvicorn.access": {
            "level": "WARNING", # Reduce noise from access logs
            "handlers": ["console"],
            "propagate": False,
        },
        # Example of setting a different level for a specific module
        # "backend.src.vector_db": {
        #     "level": "DEBUG",
        #     "handlers": ["console"],
        #     "propagate": False,
        # },
    }
}

def setup_logging():
    """Applies the logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info("Logging configured successfully.")

if __name__ == '__main__':
    # Example of how to use it
    setup_logging()
    logger = logging.getLogger("my_test_logger")
    logger.debug("This is a debug message (should not appear by default)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message") 