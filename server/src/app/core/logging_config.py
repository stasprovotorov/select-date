import logging

from src.app.core.config import settings


def logging_config() -> None:
    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        format="%(asctime)s %(module)14s %(lineno)3s %(levelname)7s - %(message)s",
    )

    logger = logging.getLogger(__name__)
    
    logger.info("Configuring logging")
    level = logging.getLevelName(settings.LOGGING_LEVEL)
    logger.info("Logging level: %s", level)
