"""XPath / CSS fallbacks. Prepend new selectors when LinkedIn changes the DOM."""

from __future__ import annotations

PROFILE_EXPERIENCE_SECTION = [
    "//main//section[.//div[@id='experience']]",
    "//main//section[.//*[@id='experience']]",
    "//section[.//div[@id='experience']]",
    "//*[@id='experience']/ancestor::section[1]",
]

EXPERIENCE_ITEMS = [
    ".//div[contains(@class,'pvs-list__outer-container')]//ul/li",
    ".//ul[contains(@class,'pvs-list')]/li",
    ".//li[contains(@class,'artdeco-list__item')]",
]

COMPANY_LOGO_LINKS = [
    ".//a[@data-field='experience_company_logo']",
    ".//a[contains(@href,'/company/')]",
    ".//a[contains(@href,'/search/results/all/')]",
]

ORG_TOP_CARD = [
    "//main//section[contains(@class,'org-top-card')]",
    "//main//section[contains(@class,'artdeco-card')][.//h1]",
    "//main//div[contains(@class,'org-top-card')]",
]

ABOUT_TAB = [
    "//a[normalize-space()='About']",
    "//a[contains(@href,'/about/')]",
    "//nav//a[contains(.,'About')]",
]

OVERVIEW_DL = [
    "//section[.//h2[normalize-space()='Overview']]//dl",
    "//section[.//h2[contains(.,'Overview')]]//dl",
    "//dl[contains(@class,'overflow-hidden')]",
]

COMPANY_NAME = [
    "//main//section[contains(@class,'org-top-card')]//h1//span[@dir='ltr']",
    "//main//h1//span[@dir='ltr']",
    "//main//h1",
]

FEED_READY = [
    "//div[contains(@class,'share-box-feed-entry')]",
    "//div[contains(@class,'feed-identity-module')]",
    "//global-nav",
]

LOGIN_EMAIL = ["session_key", "username"]
LOGIN_PASSWORD = ["session_password", "password"]
LOGIN_SUBMIT = [
    '//button[@type="submit"]',
    '//*[@type="submit"]',
    '//button[contains(@class,"sign-in-form")]',
]
