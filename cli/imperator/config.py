"""Read/write helpers for the project's `.imperator.json`."""

from __future__ import annotations

import json
from pathlib import Path

from .engine import VERSION

CONFIG_FILE = ".imperator.json"


def load_config(directory: str = ".") -> dict:
    path = Path(directory) / CONFIG_FILE
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(agent: str, extensions: list[str], style: str,
                directory: str = ".") -> Path:
    config = {
        "agent": agent,
        "extensions": extensions,
        "style": style,
        "version": VERSION,
    }
    path = Path(directory) / CONFIG_FILE
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return path
