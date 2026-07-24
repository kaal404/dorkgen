"""Rich-powered terminal UI building blocks.

Screens in ``cli.py`` compose these primitives; nothing in here knows about
application flow, so it can be reused (or swapped for a different frontend)
without touching business logic.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Optional

from rich.box import HEAVY_HEAD, ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .constants import BANNER_ASCII, THEMES, Theme, VERSION
from .models import Keyword, QuerySet, ScoredQuery
from .utils import paginate

try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False

console = Console()
err_console = Console(stderr=True)

current_theme = Theme.DARK


def set_theme(theme: Theme) -> None:
    global current_theme
    current_theme = theme


def theme(key: str) -> str:
    return THEMES[current_theme].get(key, "white")


def clear_screen() -> None:
    console.clear()


def show_banner() -> None:
    clear_screen()
    if PYFIGLET_AVAILABLE:
        banner = pyfiglet.figlet_format("DorkGEN", font="slant")
        console.print(f"[bold {theme('primary')}]{banner}[/]", highlight=False)
    else:
        console.print(f"[bold {theme('primary')}]{BANNER_ASCII}[/]")
    console.print(f"[bold {theme('accent')}]╔══════════════════════════════════════════════════════════╗[/]")
    console.print(f"[bold {theme('accent')}]║[/]  [bold {theme('primary')}]The Ultimate Google Dork Intelligence Framework[/]     [bold {theme('accent')}]║[/]")
    console.print(f"[bold {theme('accent')}]║[/]  Version [bold {theme('success')}]{VERSION}[/]                                          [bold {theme('accent')}]║[/]")
    console.print(f"[bold {theme('accent')}]╚══════════════════════════════════════════════════════════╝[/]")
    console.print()


def show_breadcrumb(path: str) -> None:
    console.print(f"[dim {theme('muted')}]{path}[/]")
    console.print()


@contextmanager
def show_loading(message: str = "Generating queries...") -> Iterator[None]:
    with Progress(SpinnerColumn(), TextColumn(f"[{theme('primary')}]{{task.description}}[/]"),
                  transient=True, console=console) as progress:
        progress.add_task(message, total=None)
        yield


def show_stats(queryset: QuerySet) -> None:
    table = Table(title=f"[{theme('header')}]📊 Generation Statistics[/]", box=HEAVY_HEAD,
                  border_style=theme('border'), header_style=theme('header'))
    table.add_column("Metric", style=theme('primary'))
    table.add_column("Value", style=theme('success'))
    table.add_row("Queries Generated", str(queryset.total))
    table.add_row("Duplicates Removed", str(queryset.duplicates_removed))
    table.add_row("Generation Time", f"{queryset.generation_time_ms}ms")
    table.add_row("Target Domain", queryset.domain or "N/A")
    table.add_row("Profile", queryset.profile or "N/A")

    if queryset.queries:
        risks = [q.risk_score for q in queryset.queries]
        avg_risk = sum(risks) / len(risks)
        high_risk = sum(1 for r in risks if r >= 7)
        med_risk = sum(1 for r in risks if 4 <= r < 7)
        low_risk = sum(1 for r in risks if r < 4)
        table.add_row("Average Risk", f"{avg_risk:.2f}")
        table.add_row("High Risk (7+)", f"[red]{high_risk}[/]")
        table.add_row("Medium Risk (4-7)", f"[yellow]{med_risk}[/]")
        table.add_row("Low Risk (<4)", f"[green]{low_risk}[/]")

    console.print(Panel(table, border_style=theme('border')))


def show_queries_table(queries: list[ScoredQuery], title: str = "Generated Queries",
                        page: int = 1, page_size: int = 20) -> int:
    """Render one page of ``queries`` and return the total page count."""
    page_items, total_pages = paginate(queries, page, page_size)
    table = Table(title=f"[{theme('header')}]🔍 {title} (page {page}/{total_pages})[/]",
                  box=HEAVY_HEAD, border_style=theme('border'), header_style=theme('header'))
    table.add_column("#", width=4)
    table.add_column("Google Dork", ratio=1)
    table.add_column("Risk", width=6, justify="center")
    start_index = (page - 1) * page_size
    for i, q in enumerate(page_items, start_index + 1):
        risk_color = "red" if q.risk_score >= 7 else ("yellow" if q.risk_score >= 4 else "green")
        table.add_row(str(i), f"[{theme('primary')}]{q.query}[/]", f"[{risk_color}]{q.risk_score}[/]")
    console.print(Panel(table, border_style=theme('border')))
    return total_pages


def show_keywords_table(keywords: list[Keyword], title: str = "Keywords") -> None:
    table = Table(title=f"[{theme('header')}]{title}[/]", box=HEAVY_HEAD,
                  border_style=theme('border'), header_style=theme('header'))
    table.add_column("#", width=4)
    table.add_column("Keyword", style=theme('primary'))
    table.add_column("Category")
    table.add_column("Risk", justify="center", width=6)
    table.add_column("Technology")
    table.add_column("Tags")
    for i, kw in enumerate(keywords, 1):
        risk_color = "red" if kw.risk >= 7 else ("yellow" if kw.risk >= 5 else "green")
        table.add_row(str(i), kw.keyword, kw.category, f"[{risk_color}]{kw.risk}[/]",
                      kw.technology or "-", ", ".join(kw.tags))
    console.print(Panel(table, border_style=theme('border')))


def show_menu(title: str, items: list[tuple[str, str]], show_back: bool = True) -> str:
    console.print(f"\n[bold {theme('header')}]═══ {title} ═══[/]\n")
    table = Table(box=ROUNDED, border_style=theme('border'), show_header=False,
                  header_style=theme('header'), pad_edge=False)
    table.add_column("Key", style=theme('primary'), width=4)
    table.add_column("Option", style=theme('secondary'))

    for key, display in items:
        table.add_row(f"[{theme('accent')}]{key}[/]", display)

    if show_back:
        table.add_row(f"[{theme('warning')}]b[/]", "Back / Previous Menu")
        table.add_row(f"[{theme('danger')}]q[/]", "Quit")

    console.print(Panel(table, border_style=theme('border')))

    choices = [k for k, _ in items]
    if show_back:
        choices.extend(["b", "q"])

    while True:
        choice = Prompt.ask(f"[{theme('primary')}]Select option[/]", choices=choices, default=items[0][0])
        if choice in choices:
            return choice


def show_input_dialog(title: str, fields: list[dict[str, Any]]) -> dict[str, Any]:
    console.print(f"\n[bold {theme('header')}]═══ {title} ═══[/]\n")
    results: dict[str, Any] = {}
    for spec in fields:
        name = spec.get("name", "")
        label = spec.get("label", name)
        default = spec.get("default", "")
        required = spec.get("required", True)
        choices = spec.get("choices")

        if choices:
            value = Prompt.ask(f"[{theme('primary')}]{label}[/]", choices=choices, default=default)
        else:
            prompt_text = f"[{theme('primary')}]{label}[/]"
            if default:
                prompt_text += f" [{theme('muted')}]({default})[/]"
            value = Prompt.ask(prompt_text, default=default)

        if not value and required:
            console.print(f"[{theme('danger')}]{label} is required![/]")
            return show_input_dialog(title, fields)

        results[name] = value
    return results


def prompt_pagination_action(total_pages: int) -> str:
    """Prompt for next/prev/search/back when browsing a paginated list."""
    items = []
    if total_pages > 1:
        items.append(("n", "Next page"))
        items.append(("p", "Previous page"))
    items.append(("f", "🔎 Search / Filter"))
    return show_menu("BROWSE", items)
