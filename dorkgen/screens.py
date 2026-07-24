"""Individual interactive TUI screens.

Split out of ``cli.py`` (which would otherwise exceed ~500 lines) so each
file stays focused: ``cli.py`` owns menu dispatch, boot, and the
non-interactive argparse mode; this module owns what each menu choice
actually does.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional

from rich.box import HEAVY_HEAD
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from . import ui
from .config import (delete_project, get_default_config, list_projects, load_config,
                      load_project, save_config, save_project)
from .constants import ExportFormat, Theme, VERSION
from .exporters import export_queries
from .generator import generate_custom, generate_queries, search_keywords, search_templates
from .keywordpacks import KEYWORD_PACKS
from .models import Project, QuerySet
from .profiles import CATEGORIES, PROFILES
from .scoring import score_query
from .templates import TEMPLATES
from .utils import paginate
from .validators import ValidationError, validate_domain


@dataclass
class AppState:
    """Session state for the interactive TUI (replaces bare module globals)."""

    current_project: Optional[Project] = None
    last_queryset: Optional[QuerySet] = None


STATE = AppState()

CATEGORY_MENU = {str(i): key for i, key in enumerate(CATEGORIES.keys(), start=4)}


# ─────────────────────────────────────────────────────────────────────────
# Shared helpers
# ─────────────────────────────────────────────────────────────────────────

def _ask_domain(default: str = "example.com") -> str:
    while True:
        domain = Prompt.ask(f"[{ui.theme('primary')}]🌐 Target domain[/]", default=default)
        try:
            return validate_domain(domain)
        except ValidationError as exc:
            ui.console.print(f"[{ui.theme('danger')}]{exc}[/]")


def _post_generation_actions(qs: QuerySet, regenerate_fn=None) -> None:
    STATE.last_queryset = qs
    ui.show_stats(qs)
    ui.show_queries_table(qs.queries)

    actions = [("e", "📤 Export Queries"), ("s", "💾 Save to Project")]
    if regenerate_fn:
        actions.append(("r", "🔄 Regenerate"))
    actions.append(("b", "Back to Menu"))
    action = ui.show_menu("ACTIONS", actions)

    if action == "e":
        screen_export(qs)
    elif action == "s":
        screen_save_project(qs)
    elif action == "r" and regenerate_fn:
        regenerate_fn()


# ─────────────────────────────────────────────────────────────────────────
# Generation screens
# ─────────────────────────────────────────────────────────────────────────

def screen_quick_generate() -> None:
    ui.show_breadcrumb("Main > Quick Generate")
    fields = [
        {"name": "domain", "label": "Target Domain", "default": "example.com"},
        {"name": "profile", "label": "Profile", "default": "bug_bounty", "choices": list(PROFILES.keys())},
        {"name": "min_risk", "label": "Min Risk (0-10)", "default": "3"},
        {"name": "max_results", "label": "Max Results", "default": "50"},
    ]
    data = ui.show_input_dialog("⚡ QUICK GENERATE", fields)
    try:
        domain = validate_domain(data["domain"])
    except ValidationError as exc:
        ui.console.print(f"[{ui.theme('danger')}]{exc}[/]")
        return

    profile_name = data["profile"]
    profile = PROFILES.get(profile_name, PROFILES["bug_bounty"])

    with ui.show_loading(f"Generating dorks for {domain}..."):
        qs = generate_queries(domain, categories=list(profile["cats"]), keyword_packs=list(profile["packs"]),
                               min_risk=int(data["min_risk"]), max_results=int(data["max_results"]),
                               profile=profile_name)
    _post_generation_actions(qs, screen_quick_generate)


def screen_guided_wizard() -> None:
    ui.show_breadcrumb("Main > Guided Wizard")
    ui.console.print(Panel(
        f"[{ui.theme('header')}]🎯 Guided Wizard[/]\n"
        f"[{ui.theme('secondary')}]A few questions to build the right query set.[/]",
        border_style=ui.theme('border'),
    ))

    steps = [
        {"name": "domain", "label": "🌐 Target domain?", "default": "example.com"},
        {"name": "cloud", "label": "☁️  Cloud provider?", "default": "any",
         "choices": ["any", "aws", "azure", "gcp", "firebase", "none"]},
        {"name": "framework", "label": "📚 Framework?", "default": "any",
         "choices": ["any", "laravel", "django", "spring", "nodejs", "react", "angular", "nextjs", "none"]},
        {"name": "focus", "label": "🎯 Focus area?", "default": "secrets",
         "choices": ["secrets", "cloud_configs", "api_endpoints", "source_code", "credentials", "all"]},
        {"name": "risk_level", "label": "⚡ Risk threshold (0-10)?", "default": "5"},
    ]
    data = ui.show_input_dialog("🎯 GUIDED WIZARD", steps)

    try:
        domain = validate_domain(data["domain"])
    except ValidationError as exc:
        ui.console.print(f"[{ui.theme('danger')}]{exc}[/]")
        return

    cats = ["secrets", "authentication", "config_files"]
    packs = ["secrets", "passwords", "api", "auth", "config_files"]

    cloud = data["cloud"]
    cloud_map = {"aws": ["aws"], "azure": ["azure"], "gcp": ["gcp"], "firebase": ["firebase"],
                 "any": ["aws", "azure", "gcp"]}
    if cloud in cloud_map:
        packs.extend(cloud_map[cloud])
        cats.append("cloud")

    framework = data["framework"]
    if framework not in ("any", "none") and framework in KEYWORD_PACKS:
        packs.append(framework)
        cats.append("frameworks")

    focus_map = {
        "secrets": (["secrets"], ["secrets", "passwords", "api"]),
        "cloud_configs": (["cloud", "config_files"], ["aws", "azure", "gcp", "config_files"]),
        "api_endpoints": (["apis", "authentication"], ["api", "auth", "jwt"]),
        "source_code": (["source_code", "secrets"], ["git", "secrets", "api"]),
        "credentials": (["secrets", "authentication"], ["secrets", "passwords", "jwt", "auth"]),
    }
    if data["focus"] in focus_map:
        cats, packs = focus_map[data["focus"]]

    min_risk = int(data["risk_level"])
    with ui.show_loading(f"Building query set for {domain}..."):
        qs = generate_queries(domain, categories=cats, keyword_packs=packs, min_risk=min_risk, max_results=60)
    _post_generation_actions(qs, screen_guided_wizard)


def screen_category_browse(choice_num: str) -> None:
    cat_key = CATEGORY_MENU.get(choice_num)
    if not cat_key:
        return
    cat = CATEGORIES[cat_key]
    ui.show_breadcrumb(f"Main > {cat['name']}")
    ui.console.print(f"[{ui.theme('header')}]{cat['name']}[/] — [{ui.theme('secondary')}]{cat['desc']}[/]\n")

    domain = _ask_domain()
    subs = cat["subs"]  # type: ignore[index]
    sub_items = [(k, v) for k, v in subs.items()]
    sub_items.append(("all", "📦 All subcategories"))
    choice = ui.show_menu(f"{cat['name']} — SUBCATEGORIES", sub_items)
    if choice in ("b", "q"):
        return

    with ui.show_loading("Generating..."):
        qs = generate_queries(domain, categories=[cat_key], min_risk=3, max_results=60)
    _post_generation_actions(qs)


def screen_bug_bounty() -> None:
    ui.show_breadcrumb("Main > Bug Bounty Packs")
    domain = _ask_domain()
    cats = ["secrets", "cloud", "authentication", "apis", "source_code", "devops", "config_files", "ai_services"]
    packs = ["secrets", "passwords", "api", "auth", "jwt", "aws", "azure", "gcp", "docker",
             "kubernetes", "git", "terraform", "config_files", "ai_services"]

    with ui.show_loading(f"Generating bug bounty dorks for {domain}..."):
        qs = generate_queries(domain, categories=cats, keyword_packs=packs, min_risk=4, max_results=80)
    _post_generation_actions(qs, screen_bug_bounty)


def screen_query_builder() -> None:
    ui.show_breadcrumb("Main > Query Builder")
    domain = _ask_domain()
    keyword = Prompt.ask(f"[{ui.theme('primary')}]🔑 Keyword / search term[/]", default="password")
    filetype_choice = Prompt.ask(f"[{ui.theme('primary')}]📄 File type (optional)[/]", default="")
    operator_choice = Prompt.ask(
        f"[{ui.theme('primary')}]🔧 Operator[/]", default="inurl",
        choices=["inurl", "intitle", "intext", "allinurl", "allintitle", "allintext"],
    )
    exact = Confirm.ask(f"[{ui.theme('primary')}]Use exact match (quotes)?[/]", default=True)

    query = generate_custom(domain, operator_choice, keyword, filetype_choice, exact=exact)
    ui.console.print(f"\n[{ui.theme('header')}]Live Preview:[/]")
    ui.console.print(f"[bold {ui.theme('primary')}]{query}[/]\n")

    scored = score_query(query, "custom", "builder", keyword_risk=7)
    qs = QuerySet(queries=[scored], domain=domain, total=1)
    _post_generation_actions(qs, screen_query_builder)


def screen_combination_generator() -> None:
    ui.show_breadcrumb("Main > Combination Generator")
    domain = _ask_domain()

    pack_items = [(k, v["name"]) for k, v in KEYWORD_PACKS.items()]  # type: ignore[misc]
    pack_items.append(("all", "📦 All Packs"))
    pack_choice = ui.show_menu("KEYWORD PACKS", pack_items)
    if pack_choice in ("b", "q"):
        return
    selected_packs = list(KEYWORD_PACKS.keys()) if pack_choice == "all" else [pack_choice]

    min_risk = int(Prompt.ask(f"[{ui.theme('primary')}]Min risk (0-10)[/]", default="3"))
    max_results = int(Prompt.ask(f"[{ui.theme('primary')}]Max results[/]", default="100"))

    with ui.show_loading("Running combination engine..."):
        qs = generate_queries(domain, keyword_packs=selected_packs, min_risk=min_risk, max_results=max_results)
    _post_generation_actions(qs, screen_combination_generator)


# ─────────────────────────────────────────────────────────────────────────
# Browse / search screens
# ─────────────────────────────────────────────────────────────────────────

def screen_template_manager() -> None:
    ui.show_breadcrumb("Main > Template Manager")
    query, category, page = "", "", 1
    while True:
        results = search_templates(query=query, category=category)
        page_items, total_pages = paginate(results, page, 15)

        table = Table(title=f"[{ui.theme('header')}]🧩 Templates ({len(results)} match, page {page}/{total_pages})[/]",
                      box=HEAVY_HEAD, border_style=ui.theme('border'), header_style=ui.theme('header'))
        table.add_column("Name", style=ui.theme('primary'))
        table.add_column("Category")
        table.add_column("Operators")
        table.add_column("Risk", justify="center")
        table.add_column("Description")
        for t in page_items:
            risk_color = "red" if t.risk_base >= 7 else ("yellow" if t.risk_base >= 5 else "green")
            table.add_row(t.name, t.category, "+".join(t.operators),
                          f"[{risk_color}]{t.risk_base}[/]", t.description[:50])
        ui.console.print(Panel(table, border_style=ui.theme('border')))

        items = [("f", "🔎 Search"), ("c", "📁 Filter by category"), ("n", "Next page"), ("p", "Prev page")]
        choice = ui.show_menu("TEMPLATE MANAGER", items)
        if choice in ("b", "q"):
            return
        if choice == "f":
            query = Prompt.ask(f"[{ui.theme('primary')}]Search term[/]", default="")
            page = 1
        elif choice == "c":
            category = Prompt.ask(f"[{ui.theme('primary')}]Category[/]", default="", choices=[""] + list(CATEGORIES.keys()))
            page = 1
        elif choice == "n":
            page = min(page + 1, total_pages)
        elif choice == "p":
            page = max(page - 1, 1)


def screen_keyword_manager() -> None:
    ui.show_breadcrumb("Main > Keyword Manager")
    query, category, page = "", "", 1
    while True:
        results = search_keywords(query=query, category=category)
        page_items, total_pages = paginate(results, page, 20)
        ui.show_keywords_table(page_items, f"Keywords ({len(results)} match, page {page}/{total_pages})")

        items = [("f", "🔎 Search"), ("c", "📁 Filter by category"), ("n", "Next page"), ("p", "Prev page")]
        choice = ui.show_menu("KEYWORD MANAGER", items)
        if choice in ("b", "q"):
            return
        if choice == "f":
            query = Prompt.ask(f"[{ui.theme('primary')}]Search term[/]", default="")
            page = 1
        elif choice == "c":
            categories = sorted({k.category for pack in KEYWORD_PACKS.values() for k in pack["keywords"]})  # type: ignore[index]
            category = Prompt.ask(f"[{ui.theme('primary')}]Category[/]", default="", choices=[""] + categories)
            page = 1
        elif choice == "n":
            page = min(page + 1, total_pages)
        elif choice == "p":
            page = max(page - 1, 1)


def screen_statistics() -> None:
    ui.show_breadcrumb("Main > Statistics")
    projects = list_projects()
    total_queries_generated = sum(len(load_project(p).queries) for p in projects if load_project(p))
    total_keywords = sum(len(v["keywords"]) for v in KEYWORD_PACKS.values())  # type: ignore[arg-type]

    table = Table(title=f"[{ui.theme('header')}]📊 DorkGEN Statistics[/]", box=HEAVY_HEAD,
                  border_style=ui.theme('border'), header_style=ui.theme('header'))
    table.add_column("Metric", style=ui.theme('primary'))
    table.add_column("Value", style=ui.theme('success'))
    table.add_row("Version", VERSION)
    table.add_row("Keyword Packs", str(len(KEYWORD_PACKS)))
    table.add_row("Total Keywords", str(total_keywords))
    table.add_row("Templates", str(len(TEMPLATES)))
    table.add_row("Categories", str(len(CATEGORIES)))
    table.add_row("Profiles Available", str(len(PROFILES)))
    table.add_row("Projects Saved", str(len(projects)))
    table.add_row("Total Queries Generated (saved projects)", str(total_queries_generated))
    ui.console.print(Panel(table, border_style=ui.theme('border')))
    Prompt.ask(f"[{ui.theme('muted')}]Press Enter to return[/]")


# ─────────────────────────────────────────────────────────────────────────
# Project / export / settings / about screens
# ─────────────────────────────────────────────────────────────────────────

def screen_projects() -> None:
    ui.show_breadcrumb("Main > Projects")
    while True:
        projects = list_projects()
        table = Table(title=f"[{ui.theme('header')}]💾 Projects[/]", box=HEAVY_HEAD,
                      border_style=ui.theme('border'), header_style=ui.theme('header'))
        table.add_column("Name", style=ui.theme('primary'))
        table.add_column("Domain")
        table.add_column("Queries", justify="center")
        table.add_column("Profile")
        table.add_column("Updated")
        for pname in projects:
            proj = load_project(pname)
            if proj:
                table.add_row(proj.name, proj.target_domain or "-", str(len(proj.queries)),
                              proj.profile or "-", proj.updated_at[:10] if proj.updated_at else "-")
        ui.console.print(Panel(table, border_style=ui.theme('border')))

        items = [("new", "🆕 New Project"), ("open", "📂 Open Project"), ("del", "🗑 Delete Project")]
        if STATE.current_project:
            items.insert(1, ("save", "💾 Save Current"))
            items.insert(2, ("view", "👁 View Current"))
        choice = ui.show_menu("PROJECTS", items)
        if choice in ("b", "q"):
            return

        if choice == "new":
            name = Prompt.ask(f"[{ui.theme('primary')}]Project name[/]")
            domain = _ask_domain()
            profile = Prompt.ask(f"[{ui.theme('primary')}]Profile[/]", default="bug_bounty", choices=list(PROFILES.keys()))
            now = datetime.datetime.now().isoformat()
            project = Project(name=name, target_domain=domain, created_at=now, updated_at=now, profile=profile)
            save_project(project)
            STATE.current_project = project
            ui.console.print(f"[{ui.theme('success')}]✓ Project '{name}' created[/]")
        elif choice == "open" and projects:
            pname = Prompt.ask(f"[{ui.theme('primary')}]Project name to open[/]", choices=projects)
            proj = load_project(pname)
            if proj:
                STATE.current_project = proj
                STATE.last_queryset = QuerySet(queries=proj.queries, domain=proj.target_domain,
                                                profile=proj.profile, total=len(proj.queries))
                ui.console.print(f"[{ui.theme('success')}]✓ Loaded '{pname}' ({len(proj.queries)} queries)[/]")
        elif choice == "save" and STATE.current_project:
            if STATE.last_queryset:
                STATE.current_project.queries = STATE.last_queryset.queries
                STATE.current_project.target_domain = STATE.last_queryset.domain
            STATE.current_project.updated_at = datetime.datetime.now().isoformat()
            save_project(STATE.current_project)
            ui.console.print(f"[{ui.theme('success')}]✓ Saved[/]")
        elif choice == "view" and STATE.current_project:
            ui.show_queries_table(STATE.current_project.queries, f"Project: {STATE.current_project.name}")
        elif choice == "del" and projects:
            pname = Prompt.ask(f"[{ui.theme('danger')}]Project to delete[/]", choices=projects)
            if Confirm.ask(f"[{ui.theme('warning')}]Delete '{pname}' permanently?[/]"):
                delete_project(pname)
                ui.console.print(f"[{ui.theme('success')}]✓ Deleted '{pname}'[/]")


def screen_save_project(qs: Optional[QuerySet] = None) -> None:
    qs = qs or STATE.last_queryset
    if not qs:
        return
    name = Prompt.ask(f"[{ui.theme('primary')}]Project name[/]",
                       default=f"scan_{qs.domain}_{datetime.date.today().isoformat()}")
    project = load_project(name) or Project(name=name)
    project.target_domain = qs.domain or project.target_domain
    project.profile = qs.profile or project.profile
    project.queries = qs.queries
    project.updated_at = datetime.datetime.now().isoformat()
    project.created_at = project.created_at or project.updated_at
    save_project(project)
    STATE.current_project = project
    ui.console.print(f"[{ui.theme('success')}]✓ Saved {len(qs.queries)} queries to '{name}'[/]")


def screen_export(qs: Optional[QuerySet] = None) -> None:
    qs = qs or STATE.last_queryset
    if not qs or not qs.queries:
        ui.console.print(f"[{ui.theme('warning')}]No queries to export. Generate some first![/]")
        return

    ui.show_breadcrumb("Main > Export Center")
    formats = [(f.value, f.value.upper()) for f in ExportFormat]
    fmt = ui.show_menu("SELECT FORMAT", formats)
    if fmt in ("b", "q"):
        return

    min_priority = 7.0 if Confirm.ask(f"[{ui.theme('primary')}]High priority only (risk >= 7)?[/]", default=False) else 0
    by_cat = Confirm.ask(f"[{ui.theme('primary')}]Group by category?[/]", default=True)
    filepath = Prompt.ask(f"[{ui.theme('primary')}]Save to file (empty = console preview)[/]", default="")
    if filepath and not filepath.endswith(f".{fmt}"):
        filepath += f".{fmt}"

    content = export_queries(qs.queries, fmt, filepath or None, min_priority, by_cat)
    if filepath:
        ui.console.print(f"[{ui.theme('success')}]✓ Exported {len(qs.queries)} queries to {filepath}[/]")
    else:
        preview = content[:400] + ("..." if len(content) > 400 else "")
        ui.console.print(Panel(preview, border_style=ui.theme('success'), title=f"{fmt.upper()} Preview"))

    if STATE.current_project:
        STATE.current_project.export_history.append({
            "format": fmt, "count": len(qs.queries), "filepath": filepath or "console",
            "timestamp": datetime.datetime.now().isoformat(),
        })
        save_project(STATE.current_project)


def screen_settings() -> None:
    config = load_config() or get_default_config()
    items = [
        ("theme", f"🎨 Theme: {config.get('theme', 'dark')}"),
        ("profile", f"📋 Default Profile: {config.get('default_profile', 'bug_bounty')}"),
        ("risk", f"⚡ Default Min Risk: {config.get('default_min_risk', 3)}"),
        ("save", "💾 Save & Return"),
    ]
    choice = ui.show_menu("⚙️  SETTINGS", items)
    if choice == "theme":
        t = ui.show_menu("SELECT THEME", [(t.value, t.value.capitalize()) for t in Theme])
        if t not in ("b", "q"):
            ui.set_theme(Theme(t))
            config["theme"] = t
    elif choice == "profile":
        p = ui.show_menu("DEFAULT PROFILE", [(k, v["name"]) for k, v in PROFILES.items()])  # type: ignore[index]
        if p not in ("b", "q"):
            config["default_profile"] = p
    elif choice == "risk":
        config["default_min_risk"] = int(Prompt.ask("Min risk (0-10)", default=str(config.get("default_min_risk", 3))))
    elif choice == "save":
        save_config(config)
        ui.console.print(f"[{ui.theme('success')}]✓ Settings saved[/]")
        return
    screen_settings()


def screen_about() -> None:
    total_keywords = sum(len(v["keywords"]) for v in KEYWORD_PACKS.values())  # type: ignore[arg-type]
    info = (
        f"[bold {ui.theme('primary')}]DorkGEN — The Ultimate Google Dork Intelligence Framework[/]\n"
        f"Version: {VERSION}\n\n"
        f"{len(KEYWORD_PACKS)} keyword packs ({total_keywords} keywords), "
        f"{len(TEMPLATES)} templates, {len(CATEGORIES)} categories, {len(PROFILES)} profiles.\n\n"
        "For authorized security testing, bug bounty programs, penetration "
        "testing engagements, and defensive research only."
    )
    ui.console.print(Panel(info, border_style=ui.theme('border'), title="ℹ️  About DorkGEN"))
    Prompt.ask(f"[{ui.theme('muted')}]Press Enter to return[/]")
