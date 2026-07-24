"""On-disk configuration and project persistence (``~/.dorkgen``)."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import yaml

from .constants import APP_DIR, CONFIG_FILE, DEFAULT_CONFIG, PROJECTS_DIR
from .models import Project

logger = logging.getLogger(__name__)


def get_default_config() -> dict:
    return dict(DEFAULT_CONFIG)


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    except (yaml.YAMLError, OSError) as exc:
        # The original code used a bare `except:` here, silently swallowing
        # *everything* including corrupt-file signals. We log instead so a
        # broken config file is discoverable rather than silently reset.
        logger.warning("Could not read config file %s: %s", CONFIG_FILE, exc)
        return {}


def save_config(config: dict) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(yaml.dump(config, default_flow_style=False), encoding="utf-8")


def list_projects() -> list[str]:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(f.stem for f in PROJECTS_DIR.glob("*.json"))


def load_project(name: str) -> Optional[Project]:
    path = PROJECTS_DIR / f"{name}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return Project.from_dict(data)


def save_project(project: Project) -> None:
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    path = PROJECTS_DIR / f"{project.name}.json"
    path.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")


def delete_project(name: str) -> bool:
    path = PROJECTS_DIR / f"{name}.json"
    if path.exists():
        path.unlink()
        return True
    return False
