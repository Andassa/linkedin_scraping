#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from linkedin_scraper.config import ROOT_DIR, get_settings
from linkedin_scraper.excel_store import ExcelStore, ensure_data_file
from linkedin_scraper.logging_setup import setup_logging
from linkedin_scraper.pipeline import Pipeline

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Enrich Excel rows with LinkedIn company data.",
)
console = Console()


def _resolve_excel(path: Optional[Path]) -> Path:
    if path:
        return path.expanduser().resolve()
    return ensure_data_file(ROOT_DIR / "scalezia.xlsx", ROOT_DIR / "data" / "scalezia.xlsx")


@app.command("status")
def status(
    excel: Optional[Path] = typer.Option(None, "--excel", "-e", help="Workbook path"),
) -> None:
    """Coverage summary for the workbook."""
    settings = get_settings()
    path = _resolve_excel(excel)
    store = ExcelStore(path, settings)
    total = len(store)
    pending = len(store.pending_indices(only_missing=True))

    table = Table(title=path.name)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Rows", str(total))
    table.add_row("Done", str(total - pending))
    table.add_row("Pending", str(pending))
    console.print(table)


@app.command("run")
def run(
    excel: Optional[Path] = typer.Option(None, "--excel", "-e"),
    start: int = typer.Option(0, "--start", help="Start index (0-based)"),
    end: Optional[int] = typer.Option(None, "--end", help="End index (exclusive)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Max rows"),
    all_rows: bool = typer.Option(False, "--all", help="Include already enriched rows"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print queue, no browser"),
    headless: bool = typer.Option(False, "--headless"),
    save_every: Optional[int] = typer.Option(None, "--save-every"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Log in and enrich pending profile rows."""
    overrides: dict = {}
    if headless:
        overrides["headless"] = True
    if save_every is not None:
        overrides["save_every"] = save_every

    settings = get_settings(**overrides)
    setup_logging(settings.log_dir, verbose=verbose)

    path = _resolve_excel(excel)
    store = ExcelStore(path, settings)
    stats = Pipeline(settings, store).run(
        start=start,
        end=end,
        limit=limit,
        only_missing=not all_rows,
        dry_run=dry_run,
    )

    if not dry_run:
        console.print(
            f"processed={stats.processed} enriched={stats.enriched} "
            f"independent={stats.independent} failed={stats.failed}"
        )


@app.command("doctor")
def doctor() -> None:
    """Validate local setup."""
    from linkedin_scraper.auth import credentials_look_placeholder

    settings = get_settings()
    password = (
        settings.linkedin_password.get_secret_value()
        if settings.linkedin_password
        else None
    )
    has_creds = bool(settings.linkedin_email and password) and not credentials_look_placeholder(
        settings.linkedin_email, password
    )
    has_excel = (ROOT_DIR / "data" / "scalezia.xlsx").exists() or (
        ROOT_DIR / "scalezia.xlsx"
    ).exists()

    table = Table(title="doctor")
    table.add_column("Check")
    table.add_column("OK")
    for name, ok in (
        ("Imports", True),
        ("Credentials in .env", has_creds),
        ("Excel workbook", has_excel),
    ):
        table.add_row(name, "[green]yes[/]" if ok else "[red]no[/]")
    console.print(table)

    if not has_creds:
        console.print("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env, then retry.")
    else:
        console.print("Ready. Example: python main.py run --limit 3")


if __name__ == "__main__":
    app()
