from __future__ import annotations

import logging
import time

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchWindowException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_scraper import selectors as S
from linkedin_scraper.config import Settings
from linkedin_scraper.human import human_pause

logger = logging.getLogger("linkedin_scraper.auth")

PLACEHOLDER_EMAILS = {"your.email@example.com", "example@example.com", "test@example.com"}
PLACEHOLDER_PASSWORDS = {"your-password", "password", "changeme"}


def credentials_look_placeholder(email: str | None, password: str | None) -> bool:
    if not email or not password:
        return True
    return email.strip().lower() in PLACEHOLDER_EMAILS or password.strip() in PLACEHOLDER_PASSWORDS


def _find_login_field(driver: WebDriver, *, ids: list[str], names: list[str], css: list[str]):
    for element_id in ids:
        els = driver.find_elements(By.ID, element_id)
        if els:
            return els[0]
    for name in names:
        els = driver.find_elements(By.NAME, name)
        if els:
            return els[0]
    for selector in css:
        els = driver.find_elements(By.CSS_SELECTOR, selector)
        if els:
            return els[0]
    return None


def _click_first(driver: WebDriver, xpaths: list[str]) -> bool:
    for xp in xpaths:
        els = driver.find_elements(By.XPATH, xp)
        if els:
            try:
                els[0].click()
                return True
            except WebDriverException:
                driver.execute_script("arguments[0].click();", els[0])
                return True
    return False


def _browser_alive(driver: WebDriver) -> bool:
    try:
        _ = driver.current_url
        return True
    except (NoSuchWindowException, InvalidSessionIdException, WebDriverException):
        return False


def is_logged_in(driver: WebDriver, timeout: int = 5) -> bool:
    if not _browser_alive(driver):
        return False

    try:
        cookies = {c["name"] for c in driver.get_cookies()}
        if "li_at" in cookies:
            return True
    except WebDriverException:
        return False

    for xp in S.FEED_READY:
        try:
            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xp)))
            return True
        except (TimeoutException, NoSuchWindowException, InvalidSessionIdException):
            continue
        except WebDriverException:
            return False

    try:
        url = driver.current_url or ""
        if "/feed" in url or "/mynetwork" in url:
            return True
    except WebDriverException:
        return False
    return False


def login(
    driver: WebDriver,
    settings: Settings,
    *,
    manual_fallback: bool = True,
) -> None:
    """
    Attempt form login. If LinkedIn shows a challenge/CAPTCHA/2FA,
    wait for the user to finish manually when manual_fallback is True.
    Do not close the Chrome window during this wait.
    """
    email = settings.linkedin_email
    password = (
        settings.linkedin_password.get_secret_value()
        if settings.linkedin_password
        else None
    )

    if credentials_look_placeholder(email, password):
        raise RuntimeError(
            "Ton fichier .env contient encore les valeurs d'exemple "
            "(your.email@example.com / your-password).\n"
            "Ouvre linkeDIn_scraping/.env et mets ton vrai email + mot de passe LinkedIn, "
            "puis relance: python main.py run --limit 3"
        )

    driver.get("https://www.linkedin.com/login")
    human_pause(1.5, 2.5)

    if is_logged_in(driver, timeout=3):
        logger.info("Already authenticated (session / profile).")
        return

    logger.info("Signing in as %s", email)
    user = _find_login_field(
        driver,
        ids=S.LOGIN_EMAIL,
        names=["session_key", "username", "email"],
        css=['input[autocomplete="username"]', 'input[type="text"]'],
    )
    pwd = _find_login_field(
        driver,
        ids=S.LOGIN_PASSWORD,
        names=["session_password", "password"],
        css=['input[autocomplete="current-password"]', 'input[type="password"]'],
    )

    if user and pwd:
        user.clear()
        user.send_keys(email)
        human_pause(0.6, 1.4)
        pwd.clear()
        pwd.send_keys(password)
        human_pause(0.6, 1.4)
        if not _click_first(driver, S.LOGIN_SUBMIT):
            pwd.submit()
        human_pause(2.0, 3.0)
    else:
        logger.warning(
            "Login form fields not found (page may have changed or shown a challenge). "
            "Connecte-toi manuellement dans la fenêtre Chrome — ne la ferme pas."
        )

    wait_s = settings.manual_login_wait if manual_fallback else 25
    logger.info(
        "Waiting up to %ss for login / CAPTCHA / 2FA. Keep Chrome open.",
        wait_s,
    )

    deadline = time.time() + wait_s
    while time.time() < deadline:
        if not _browser_alive(driver):
            raise RuntimeError(
                "La fenêtre Chrome a été fermée pendant le login. "
                "Relance et laisse le navigateur ouvert jusqu'à 'Login confirmed'."
            )
        if is_logged_in(driver, timeout=2):
            logger.info("Login confirmed.")
            return
        time.sleep(2)

    if not _browser_alive(driver):
        raise RuntimeError("Chrome closed before login completed.")

    if is_logged_in(driver, timeout=3):
        logger.info("Login confirmed.")
        return

    raise RuntimeError(
        "Login failed or timed out. Complete any CAPTCHA/2FA in the browser, "
        "or increase MANUAL_LOGIN_WAIT / use CHROME_PROFILE_DIR for a warm session."
    )


def warm_session_home(driver: WebDriver, settings: Settings) -> None:
    driver.get("https://www.linkedin.com/feed/")
    human_pause(settings.min_delay, settings.max_delay)
