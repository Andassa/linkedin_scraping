from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from linkedin_scraper.config import Settings

logger = logging.getLogger("linkedin_scraper.browser")


def build_chrome_options(settings: Settings) -> Options:
    options = Options()
    if settings.headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,1000")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    profile = settings.chrome_profile_dir
    if profile:
        path = Path(profile).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={path}")
        logger.info("Using Chrome profile: %s", path)

    return options


def create_driver(settings: Settings) -> WebDriver:
    options = build_chrome_options(settings)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(settings.page_timeout + 30)
    driver.implicitly_wait(0)

    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                """
            },
        )
    except Exception as exc:  # noqa: BLE001 — CDP optional
        logger.debug("CDP stealth tweak skipped: %s", exc)

    return driver


def quit_driver(driver: Optional[WebDriver]) -> None:
    if driver is None:
        return
    try:
        driver.quit()
    except Exception as exc:  # noqa: BLE001
        logger.debug("Driver quit error: %s", exc)