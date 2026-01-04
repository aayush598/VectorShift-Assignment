# app/core/logging.py

import logging

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
    )

    # Reduce noise from third-party libs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
