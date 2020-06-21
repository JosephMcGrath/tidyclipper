import logging.config


def configure_logging(log_name: str) -> None:
    """
    Configures a logger.
    """

    config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            "file": {"format": "%(asctime)s %(levelname)s\t %(name)s - %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "rotating": {
                "level": "DEBUG",
                "formatter": "file",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "TidyClipper.log",
                "mode": "a",
                "maxBytes": 10485760,
                "backupCount": 5,
            },
        },
        "loggers": {
            log_name: {
                "handlers": ["default", "rotating"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(config)


LOG_NAME = __name__
configure_logging(LOG_NAME)
