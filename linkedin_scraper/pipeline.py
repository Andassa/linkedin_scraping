from __future__ import annotations

import logging
import random
import signal
from dataclasses import dataclass
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from linkedin_scraper.auth import login, warm_session_home
from linkedin_scraper.browser import create_driver, quit_driver
from linkedin_scraper.company import get_company_information
from linkedin_scraper.config import Settings
from linkedin_scraper.excel_store import ExcelStore
from linkedin_scraper.human import human_pause, scroll_random
from linkedin_scraper.profile import (
    collect_company_links,
    normalize_first_company_link,
    open_experience_section,
)

logger = logging.getLogger("linkedin_scraper.pipeline")


@dataclass
class RunStats:
    processed: int = 0
    enriched: int = 0
    independent: int = 0
    failed: int = 0
    skipped: int = 0


class Pipeline:
    def __init__(self, settings: Settings, store: ExcelStore):
        self.settings = settings
        self.store = store
        self.driver: Optional[WebDriver] = None
        self._stop = False
        self.stats = RunStats()

    def request_stop(self, *_args) -> None:
        logger.warning("Stop requested — finishing current row then saving…")
        self._stop = True

    def _browse_noise(self) -> None:
        """Light navigation to look less robotic between batches."""
        destinations = [
            "https://www.linkedin.com/feed/",
            "https://www.linkedin.com/mynetwork/",
            "https://www.linkedin.com/notifications/?filter=all",
            "https://www.linkedin.com/messaging/",
        ]
        url = random.choice(destinations)
        try:
            logger.debug("Noise browse → %s", url)
            assert self.driver is not None
            self.driver.get(url)
            human_pause(2.0, 5.0)
            scroll_random(self.driver)
            human_pause(1.0, 3.0)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Noise browse failed: %s", exc)

    def process_row(self, index: int) -> None:
        assert self.driver is not None
        profile_url = self.store.row_linkedin(index)
        logger.info("[%s] Profile %s", index, profile_url)

        try:
            section = open_experience_section(
                self.driver, profile_url, timeout=self.settings.page_timeout
            )
            links = collect_company_links(section)
            company_ref, is_indep = normalize_first_company_link(links)

            payload: dict = {self.settings.company_link_col: company_ref}
            if is_indep:
                self.stats.independent += 1
                logger.info("[%s] Independent / no company page: %s", index, company_ref)
            elif company_ref:
                human_pause(self.settings.min_delay, self.settings.max_delay)
                info = get_company_information(self.driver, company_ref, self.settings)
                payload.update(info)
                self.stats.enriched += 1
                logger.info("[%s] Enriched → %s", index, info.get("company_name"))
            else:
                logger.warning("[%s] No company links found", index)
                self.stats.failed += 1

            self.store.update_row(index, payload)
            self.stats.processed += 1
        except Exception as exc:  # noqa: BLE001 — keep batch running
            self.stats.failed += 1
            logger.exception("[%s] Failed: %s", index, exc)

        human_pause(self.settings.min_delay, self.settings.max_delay + 2)

    def run(
        self,
        *,
        start: int = 0,
        end: int | None = None,
        limit: int | None = None,
        only_missing: bool = True,
        dry_run: bool = False,
    ) -> RunStats:
        indices = self.store.pending_indices(start=start, end=end, only_missing=only_missing)
        if limit is not None:
            indices = indices[:limit]

        logger.info(
            "Queue: %s rows (start=%s end=%s only_missing=%s dry_run=%s)",
            len(indices),
            start,
            end,
            only_missing,
            dry_run,
        )
        if dry_run:
            for i in indices[:20]:
                logger.info("DRY would process [%s] %s", i, self.store.row_linkedin(i))
            if len(indices) > 20:
                logger.info("… and %s more", len(indices) - 20)
            return self.stats

        signal.signal(signal.SIGINT, self.request_stop)

        self.driver = create_driver(self.settings)
        try:
            login(self.driver, self.settings)
            warm_session_home(self.driver, self.settings)

            for n, index in enumerate(indices, start=1):
                if self._stop:
                    break
                self.process_row(index)

                if n % self.settings.save_every == 0:
                    self.store.save()
                    self._browse_noise()

            self.store.save()
        finally:
            quit_driver(self.driver)
            self.driver = None

        logger.info(
            "Done — processed=%s enriched=%s independent=%s failed=%s",
            self.stats.processed,
            self.stats.enriched,
            self.stats.independent,
            self.stats.failed,
        )
        return self.stats