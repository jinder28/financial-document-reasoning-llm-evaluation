"""Logging setup keeps console and file evidence aligned for the main run."""
from __future__ import annotations

import logging
from pathlib import Path


def configure_dissertation_logger(output_log_file_path: Path | None = None) -> logging.Logger:
    """Creates a logger for validation, dry-run, live-run, and scoring commands."""
    logger = logging.getLogger("sec10k_dissertation_apparatus")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    log_format = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    if output_log_file_path is not None:
        output_log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(output_log_file_path, encoding="utf-8")
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger
