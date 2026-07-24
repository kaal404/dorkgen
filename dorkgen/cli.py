"""The DorkGEN command-line interface.

Two entry points live here:

- ``run_interactive()`` — boots and runs the Rich-powered menu-driven TUI
  (screen implementations live in ``screens.py``; this module only owns
  menu structure and dispatch).
- ``run_noninteractive(argv)`` — a scriptable ``dorkgen generate ...``
  mode for CI/automation, built on the same ``generator`` API.
"""
from __future__ import annotations

import argparse
import sys

from rich.prompt import Confirm

from . import screens, ui
from .config import get_default_config, load_config, save_config
from .constants import ExportFormat, Theme
from .exporters import export_queries
from .profiles import CATEGORIES, PROFILES
from .validators import ValidationError, validate_domain

_MAIN_MENU_ITEMS = [
    ("1", "⚡ Quick Generate"), ("2", "🎯 Guided Wizard"), ("3", "📦 Bug Bounty Packs"),
    *[(str(i), CATEGORIES[key]["name"]) for i, key in enumerate(CATEGORIES.keys(), start=4)],  # type: ignore[index]
    ("16", "🔨 Query Builder"), ("17", "🔄 Combination Generator"),
    ("18", "🧩 Template Manager"), ("19", "📋 Keyword Manager"), ("20", "📊 Statistics"),
    ("21", "💾 Projects"), ("22", "📤 Export Center"), ("23", "⚙️  Settings"), ("24", "ℹ️  About"),
]

_DISPATCH = {
    "1": screens.screen_quick_generate, "2": screens.screen_guided_wizard,
    "3": screens.screen_bug_bounty, "16": screens.screen_query_builder,
    "17": screens.screen_combination_generator, "18": screens.screen_template_manager,
    "19": screens.screen_keyword_manager, "20": screens.screen_statistics,
    "21": screens.screen_projects, "22": screens.screen_export,
    "23": screens.screen_settings, "24": screens.screen_about,
}


def main_menu() -> None:
    while True:
        ui.show_banner()
        choice = ui.show_menu("MAIN MENU", _MAIN_MENU_ITEMS, show_back=False)

        if choice == "q":
            if Confirm.ask(f"[{ui.theme('warning')}]Exit DorkGEN?[/]"):
                ui.console.print(f"[{ui.theme('success')}]Goodbye![/]")
                sys.exit(0)
            continue

        if choice in _DISPATCH:
            _DISPATCH[choice]()
        elif choice in screens.CATEGORY_MENU:
            screens.screen_category_browse(choice)


def boot() -> None:
    from .constants import APP_DIR, PROJECTS_DIR
    APP_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    existing = load_config()
    config = existing or get_default_config()
    if not existing:
        save_config(config)
    try:
        ui.set_theme(Theme(config.get("theme", "dark")))
    except ValueError:
        ui.set_theme(Theme.DARK)


def run_interactive() -> None:
    try:
        boot()
        main_menu()
    except KeyboardInterrupt:
        ui.console.print(f"\n[{ui.theme('warning')}]Interrupted. Goodbye![/]")
        sys.exit(0)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dorkgen", description="DorkGEN — Google Dork Intelligence Framework")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Non-interactively generate dorks and print/export them")
    gen.add_argument("--domain", required=True)
    gen.add_argument("--profile", default="bug_bounty", choices=list(PROFILES.keys()))
    gen.add_argument("--min-risk", type=int, default=3)
    gen.add_argument("--max-results", type=int, default=50)
    gen.add_argument("--export", choices=[f.value for f in ExportFormat], default=None)
    gen.add_argument("--out", default=None, help="File path to write the export to")
    return parser


def run_noninteractive(argv: list[str]) -> int:
    from .generator import generate_for_profile

    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.command != "generate":
        parser.print_help()
        return 1

    try:
        domain = validate_domain(args.domain)
    except ValidationError as exc:
        ui.err_console.print(f"[red]{exc}[/]")
        return 2

    qs = generate_for_profile(domain, args.profile, min_risk=args.min_risk, max_results=args.max_results)
    if args.export:
        content = export_queries(qs.queries, args.export, args.out)
        if args.out:
            print(f"Wrote {len(qs.queries)} queries to {args.out}")
        else:
            print(content)
    else:
        for q in qs.queries:
            print(q.query)
    return 0
