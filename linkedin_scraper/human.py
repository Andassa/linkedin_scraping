from __future__ import annotations

import random
import time
from typing import Callable

from selenium.webdriver.remote.webdriver import WebDriver


def human_pause(min_s: float, max_s: float) -> None:
    lo, hi = sorted((min_s, max_s))
    time.sleep(random.uniform(lo, hi))


def scroll_random(driver: WebDriver, fraction: float | None = None) -> None:
    height = driver.execute_script("return document.body.scrollHeight") or 800
    if fraction is None:
        target = random.randint(0, max(int(height), 1))
    else:
        target = int(height * max(0.0, min(1.0, fraction)))
    driver.execute_script(f"window.scrollTo(0, {target});")


def with_retries(
    fn: Callable[[], object],
    *,
    attempts: int = 3,
    delay: float = 1.5,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> object:
    last: BaseException | None = None
    for i in range(attempts):
        try:
            return fn()
        except exceptions as exc:
            last = exc
            if i < attempts - 1:
                time.sleep(delay * (i + 1))
    assert last is not None
    raise last