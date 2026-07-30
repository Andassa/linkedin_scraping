#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from linkedin_scraper.config import ROOT_DIR, Settings, get_settings
from linkedin_scraper.excel_store import ExcelStore, ensure_data_file
from linkedin_scraper.logging_setup import setup_logging
from linkedin_scraper.pipeline import Pipeline

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="LinkedIn company enrichment from profile URLs in Excel.",
)
console = Console()


def _resolve_excel(path: Optional[Path]) -> Path:
    if path:
        return path.expanduser().resolve()
    data = ROOT_DIR / "data" / "scalezia.xlsx"
    legacy = ROOT_DIR / "scalezia.xlsx"
    return ensure_data_file(legacy, data)


@app.command("status")
def status(
    excel: Optional[Path] = typer.Option(None, "--excel", "-e", help="Path to workbook"),
) -> None:
    """Show enrichment coverage."""
    settings = get_settings()
    path = _resolve_excel(excel)
    store = ExcelStore(path, settings)
    total = len(store)
    pending = store.pending_indices(only_missing=True)
    done = total - len(pending)

    table = Table(title=f"Workbook · {path.name}")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Rows", str(total))
    table.add_row("Enriched / with company link", str(done))
    table.add_row("Pending", str(len(pending)))
    console.print(table)


@app.command("run")
def run(
    excel: Optional[Path] = typer.Option(None, "--excel", "-e"),
    start: int = typer.Option(0, "--start", help="0-based start index"),
    end: Optional[int] = typer.Option(None, "--end", help="Exclusive end index"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Max rows this run"),
    all_rows: bool = typer.Option(
        False, "--all", help="Reprocess even if already enriched"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="List work without browser"),
    headless: bool = typer.Option(False, "--headless"),
    save_every: Optional[int] = typer.Option(None, "--save-every"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """
    Login to LinkedIn and enrich company fields for pending profile rows.
    """
    overrides = {}
    if headless:
        overrides["headless"] = True
    if save_every is not None:
        overrides["save_every"] = save_every

    settings = get_settings(**overrides)
    setup_logging(settings.log_dir, verbose=verbose)

    path = _resolve_excel(excel)
    store = ExcelStore(path, settings)
    pipeline = Pipeline(settings, store)
    stats = pipeline.run(
        start=start,
        end=end,
        limit=limit,
        only_missing=not all_rows,
        dry_run=dry_run,
    )

    if not dry_run:
        console.print(
            f"[bold green]Done[/] processed={stats.processed} "
            f"enriched={stats.enriched} independent={stats.independent} "
            f"failed={stats.failed}"
        )


@app.command("doctor")
def doctor() -> None:
    """Quick environment check."""
    from linkedin_scraper.auth import credentials_look_placeholder

    settings = get_settings()
    setup_logging(settings.log_dir, verbose=False)
    password = (
        settings.linkedin_password.get_secret_value()
        if settings.linkedin_password
        else None
    )
    real_creds = bool(settings.linkedin_email and password) and not credentials_look_placeholder(
        settings.linkedin_email, password
    )
    checks = [
        ("Python package imports", True),
        (".env real credentials (not placeholders)", real_creds),
        ("Excel (data/ or root)", (ROOT_DIR / "data" / "scalezia.xlsx").exists() or (ROOT_DIR / "scalezia.xlsx").exists()),
    ]
    table = Table(title="Doctor")
    table.add_column("Check")
    table.add_column("OK")
    for name, ok in checks:
        table.add_row(name, "[green]yes[/]" if ok else "[red]no[/]")
    console.print(table)
    if not real_creds:
        console.print(
            "[yellow]Édite[/] [cyan].env[/] : remplace "
            "[red]your.email@example.com[/] / [red]your-password[/] "
            "par ton vrai compte LinkedIn."
        )
    else:
        console.print("OK — lance: [cyan]python main.py run --limit 3[/]")


if __name__ == "__main__":
    app()