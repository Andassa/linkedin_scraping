from __future__ import annotations

import logging
import re
from typing import Optional
from urllib.parse import unquote

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper import selectors as S
from linkedin_scraper.human import human_pause, scroll_random

logger = logging.getLogger("linkedin_scraper.profile")


def _first_match(driver_or_el, xpaths: list[str], timeout: int = 12) -> WebElement:
    last_err: Exception | None = None
    root_is_driver = hasattr(driver_or_el, "execute_script")
    for xp in xpaths:
        try:
            if root_is_driver and timeout:
                return WebDriverWait(driver_or_el, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xp))
                )
            return driver_or_el.find_element(By.XPATH, xp)
        except (TimeoutException, NoSuchElementException) as exc:
            last_err = exc
            continue
    raise TimeoutException(f"No selector matched: {xpaths}") from last_err


def open_experience_section(driver: WebDriver, profile_url: str, timeout: int = 15) -> WebElement:
    driver.get(profile_url)
    human_pause(1.5, 3.0)
    scroll_random(driver, 0.45)
    human_pause(0.8, 1.5)
    return _first_match(driver, S.PROFILE_EXPERIENCE_SECTION, timeout=timeout)


def collect_company_links(section: WebElement) -> list[str]:
    links: list[str] = []
    items: list[WebElement] = []
    for xp in S.EXPERIENCE_ITEMS:
        found = section.find_elements(By.XPATH, xp)
        if found:
            items = found
            break

    for item in items:
        href: Optional[str] = None
        for xp in S.COMPANY_LOGO_LINKS:
            els = item.find_elements(By.XPATH, xp)
            if els:
                href = els[0].get_attribute("href")
                if href:
                    break
        if href and href not in links:
            links.append(href)
    return links


def keyword_from_search_url(url: str) -> Optional[str]:
    match = re.search(r"keywords=([^&]+)", url)
    if not match:
        return None
    return unquote(match.group(1).replace("+", " ")).strip() or None


def normalize_first_company_link(links: list[str]) -> tuple[Optional[str], bool]:
    """
    Returns (value, is_independent).
    Independent = LinkedIn search URL instead of /company/.
    """
    if not links:
        return None, False
    first = links[0]
    if "search" in first:
        keyword = keyword_from_search_url(first) or "unknown"
        return f"indépendant-{keyword}", True
    return first, False