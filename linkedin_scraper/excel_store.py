from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from linkedin_scraper.config import Settings

logger = logging.getLogger("linkedin_scraper.excel")


class ExcelStore:
    def __init__(self, path: Path, settings: Settings):
        self.path = Path(path)
        self.settings = settings
        self.df = self._load()

    def _load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise FileNotFoundError(f"Excel not found: {self.path}")
        df = pd.read_excel(self.path)
        if self.settings.linkedin_col not in df.columns:
            raise ValueError(
                f"Required column '{self.settings.linkedin_col}' missing in {self.path}"
            )

        for col in (*self.settings.company_fields, self.settings.company_link_col):
            if col not in df.columns:
                df[col] = pd.NA
                logger.info("Added column: %s", col)
        return df

    def __len__(self) -> int:
        return len(self.df)

    def pending_indices(
        self,
        *,
        start: int = 0,
        end: int | None = None,
        only_missing: bool = True,
    ) -> list[int]:
        end_i = len(self.df) if end is None else min(end, len(self.df))
        start_i = max(0, start)
        indices: list[int] = []
        link_col = self.settings.company_link_col
        name_col = "company_name"

        for idx in range(start_i, end_i):
            row = self.df.iloc[idx]
            url = row.get(self.settings.linkedin_col)
            if pd.isna(url) or not str(url).strip():
                continue
            if only_missing:
                has_company = (
                    not pd.isna(row.get(name_col))
                    and str(row.get(name_col)).strip() not in ("", "nan")
                ) or (
                    not pd.isna(row.get(link_col))
                    and str(row.get(link_col)).strip() not in ("", "nan")
                )
                if has_company:
                    continue
            indices.append(idx)
        return indices

    def update_row(self, index: int, values: dict) -> None:
        for key, value in values.items():
            self.df.loc[index, key] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        self.df.to_excel(tmp, index=False)
        tmp.replace(self.path)
        logger.info("Saved %s", self.path)

    def row_linkedin(self, index: int) -> str:
        return str(self.df.iloc[index][self.settings.linkedin_col]).strip()


def ensure_data_file(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return dest
    if src.exists():
        dest.write_bytes(src.read_bytes())
        logger.info("Copied %s -> %s", src, dest)
        return dest
    raise FileNotFoundError(f"Neither {dest} nor {src} found")
