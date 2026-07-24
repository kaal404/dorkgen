"""Application-wide constants: metadata, filesystem paths, and themes.

Nothing in this module has behavior — it is pure configuration data so that
every other module can depend on it without creating import cycles.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path

VERSION = "3.0.0"
AUTHOR = "HackerAI"
APP_NAME = "DorkGEN"

APP_DIR = Path.home() / ".dorkgen"
PROJECTS_DIR = APP_DIR / "projects"
CONFIG_FILE = APP_DIR / "config.yaml"

BANNER_ASCII = r"""
██████╗  ██████╗ ██████╗ ██╗  ██╗ ██████╗ ███████╗███╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝ ██╔════╝████╗  ██║
██║  ██║██║   ██║██████╔╝█████╔╝ ██║  ███╗█████╗  ██╔██╗ ██║
██║  ██║██║   ██║██╔══██╗██╔═██╗ ██║   ██║██╔══╝  ██║╚██╗██║
██████╔╝╚██████╔╝██║  ██║██║  ██╗╚██████╔╝███████╗██║ ╚████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝
"""


class Theme(str, Enum):
    DARK = "dark"
    CYBER = "cyber"
    MATRIX = "matrix"
    BLOOD = "blood"
    LIGHT = "light"


class ExportFormat(str, Enum):
    TXT = "txt"
    MD = "md"
    CSV = "csv"
    JSON = "json"
    HTML = "html"


THEMES: dict[Theme, dict[str, str]] = {
    Theme.DARK: {
        "primary": "cyan", "secondary": "blue", "accent": "magenta",
        "success": "green", "warning": "yellow", "danger": "red",
        "info": "blue", "muted": "bright_black", "header": "bold cyan",
        "border": "blue", "highlight": "bold white on blue",
    },
    Theme.CYBER: {
        "primary": "bright_green", "secondary": "bright_cyan",
        "accent": "bright_magenta", "success": "green",
        "warning": "bright_yellow", "danger": "bright_red",
        "info": "bright_blue", "muted": "bright_black",
        "header": "bold bright_green", "border": "bright_green",
        "highlight": "bold black on bright_green",
    },
    Theme.MATRIX: {
        "primary": "green", "secondary": "bright_green", "accent": "yellow",
        "success": "green", "warning": "yellow", "danger": "red",
        "info": "cyan", "muted": "dark_green", "header": "bold bright_green",
        "border": "green", "highlight": "bold black on green",
    },
    Theme.BLOOD: {
        "primary": "red", "secondary": "dark_red", "accent": "bright_red",
        "success": "green", "warning": "yellow", "danger": "bright_red",
        "info": "cyan", "muted": "grey50", "header": "bold bright_red",
        "border": "red", "highlight": "bold white on red",
    },
    Theme.LIGHT: {
        "primary": "blue", "secondary": "blue_violet", "accent": "magenta",
        "success": "green", "warning": "dark_goldenrod", "danger": "red",
        "info": "blue", "muted": "grey50", "header": "bold blue",
        "border": "blue", "highlight": "bold white on blue",
    },
}

DEFAULT_CONFIG: dict[str, object] = {
    "theme": Theme.DARK.value,
    "default_profile": "bug_bounty",
    "default_min_risk": 3,
    "default_max_results": 50,
    "export_format": ExportFormat.TXT.value,
    "default_domain": "example.com",
}
