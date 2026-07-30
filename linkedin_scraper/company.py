from __future__ import annotations

import logging
from typing import Any

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper import selectors as S
from linkedin_scraper.config import Settings
from linkedin_scraper.human import human_pause, scroll_random

logger = logging.getLogger("linkedin_scraper.company")

NOT_FOUND = "Not found"


def _empty_info(settings: Settings) -> dict[str, str]:
    return {field: "" for field in settings.company_fields}


def _first_xpath(driver: WebDriver, xpaths: list[str], timeout: int = 12):
    last: Exception | None = None
    for xp in xpaths:
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xp))
            )
        except TimeoutException as exc:
            last = exc
    raise TimeoutException(f"No match among {xpaths}") from last


def _click_about(driver: WebDriver) -> None:
    for xp in S.ABOUT_TAB:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            driver.execute_script("arguments[0].click();", els[0])
            return
    if "/about" not in (driver.current_url or ""):
        raise NoSuchElementException("About tab not found")


def _read_dt(section, label: str) -> str:
    if label == "Phone":
        candidates = (
            './/dt[normalize-space()="Phone"]/following-sibling::dd[1]//span[@dir="ltr"]',
            './/dt[normalize-space()="Phone"]/following-sibling::dd[1]',
        )
        for xp in candidates:
            els = section.find_elements(By.XPATH, xp)
            if els and els[0].text.strip():
                return els[0].text.strip()
        raise NoSuchElementException(label)

    for xp in (
        f'.//dt[normalize-space()="{label}"]/following-sibling::dd[1]',
        f'//dt[normalize-space()="{label}"]/following-sibling::dd[1]',
    ):
        els = section.find_elements(By.XPATH, xp)
        if els and els[0].text.strip():
            return els[0].text.strip()
    raise NoSuchElementException(label)


def get_company_information(
    driver: WebDriver, company_url: str, settings: Settings
) -> dict[str, Any]:
    info = _empty_info(settings)
    if not company_url or company_url.startswith("indépendant-"):
        return info

    about_url = company_url.rstrip("/")
    if "/about" not in about_url:
        about_url = f"{about_url}/about/"

    driver.get(about_url)
    human_pause(settings.min_delay, settings.max_delay)

    try:
        _first_xpath(driver, S.ORG_TOP_CARD, timeout=settings.page_timeout)
    except TimeoutException:
        driver.get(company_url)
        human_pause(settings.min_delay, settings.max_delay)
        _first_xpath(driver, S.ORG_TOP_CARD, timeout=settings.page_timeout)
        _click_about(driver)
        human_pause(1.0, 2.0)

    scroll_random(driver, 0.35)
    human_pause(0.8, 1.6)

    try:
        overview = _first_xpath(driver, S.OVERVIEW_DL, timeout=settings.page_timeout)
    except TimeoutException:
        logger.warning("Overview missing: %s", company_url)
        overview = None

    for key in settings.company_fields:
        if key == "company_name":
            continue
        if overview is None:
            info[key] = NOT_FOUND
            continue
        try:
            info[key] = _read_dt(overview, key)
        except NoSuchElementException:
            info[key] = NOT_FOUND

    try:
        name_el = _first_xpath(driver, S.COMPANY_NAME, timeout=8)
        info["company_name"] = name_el.text.strip()
    except TimeoutException:
        info["company_name"] = NOT_FOUND

    return info
