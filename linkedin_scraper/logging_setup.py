from __future__ import annotations

import logging
from pathlib import Path

from rich.logging import RichHandler


def setup_logging(log_dir: Path, verbose: bool = False) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger("linkedin_scraper")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    console = RichHandler(rich_tracebacks=True, show_path=False, markup=True)
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    file_handler = logging.FileHandler(log_dir / "scraper.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    logger.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("WDM").setLevel(logging.WARNING)

    return logger
