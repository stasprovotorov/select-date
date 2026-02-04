import logging


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(module)12s %(lineno)3s %(levelname)7s - %(message)s"
    )
