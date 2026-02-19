import logging
import re

from src.app.core.config import settings


class MaskSIDFormatter(logging.Formatter):
    SID_REGEX = re.compile(r"\b(?P<key>sid)\s*=\s*(?P<val>[^,\s;]+)", re.IGNORECASE)
    
    def _mask(self, value: str, keep: int = 4) -> str:
        if len(value) <= keep * 2:
            return "*" * len(value)
        return value[:keep] + "*" * (len(value) - keep * 2) + value[-keep:]

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return self.SID_REGEX.sub(lambda m: f'{m.group("key")}={self._mask(m.group("val"))}', message)


def logging_config() -> None:
    handler = logging.StreamHandler()

    format = "%(asctime)s %(module)14s %(lineno)3s %(levelname)7s - %(message)s"
    handler.setFormatter(MaskSIDFormatter(format))

    logging.basicConfig(
        level=settings.LOGGING_LEVEL,
        handlers=[handler],
    )

    logger = logging.getLogger(__name__)
    
    logger.info("Configuring logging")
    level = logging.getLevelName(settings.LOGGING_LEVEL)
    logger.info("Logging level: %s", level)
