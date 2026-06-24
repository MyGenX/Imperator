"""Read/write helpers for the project's `.imperator.json`."""

from __future__ import annotations

import json
from pathlib import Path

from .engine import VERSION

CONFIG_FILE = ".imperator.json"


def load_config(directory: str = ".") -> dict:
    """Load config, migrating legacy fields (extensions -> domains)."""
    path = Path(directory) / CONFIG_FILE
    if not path.is_file():
        return {}
    config = json.loads(path.read_text(encoding="utf-8"))

    # Migrate v0.1 schema.
    if "domains" not in config and "extensions" in config:
        config["domains"] = config.pop("extensions")
    config.setdefault("domains", [])
    config.setdefault("roles", [])
    config.setdefault("agent", "claude-code")
    config.setdefault("style", "compact")
    config.pop("layout", None)
    return config


def save_config(agent: str, domains: list[str], roles: list[str],
                style: str, directory: str = ".") -> Path:
    config = {
        "agent": agent,
        "domains": domains,
        "roles": roles,
        "style": style,
        "version": VERSION,
    }
    path = Path(directory) / CONFIG_FILE
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return path
