from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT_DIR / "data" / "scalezia.xlsx"
DEFAULT_LOG_DIR = ROOT_DIR / "logs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    linkedin_email: Optional[str] = Field(default=None, alias="LINKEDIN_EMAIL")
    linkedin_password: Optional[SecretStr] = Field(
        default=None, alias="LINKEDIN_PASSWORD"
    )

    headless: bool = Field(default=False, alias="HEADLESS")
    save_every: int = Field(default=5, alias="SAVE_EVERY", ge=1)
    min_delay: float = Field(default=2.0, alias="MIN_DELAY", ge=0)
    max_delay: float = Field(default=5.0, alias="MAX_DELAY", ge=0)
    page_timeout: int = Field(default=20, alias="PAGE_TIMEOUT", ge=5)
    manual_login_wait: int = Field(default=90, alias="MANUAL_LOGIN_WAIT", ge=0)
    chrome_profile_dir: Optional[str] = Field(default=None, alias="CHROME_PROFILE_DIR")

    excel_path: Path = Field(default=DEFAULT_DATA)
    log_dir: Path = Field(default=DEFAULT_LOG_DIR)

    linkedin_col: str = "linkedIn"
    company_link_col: str = "Link_Linkdin_company"
    company_fields: tuple[str, ...] = (
        "company_name",
        "Phone",
        "Website",
        "Industry",
        "Company size",
        "Headquarters",
        "Founded",
        "Specialties",
    )


def get_settings(**overrides) -> Settings:
    return Settings(**overrides)
