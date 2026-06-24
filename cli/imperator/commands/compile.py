"""imperator compile — generate agent rule files from config."""

from __future__ import annotations

from pathlib import Path

from .. import engine
from ..config import load_config


def recompile(config: dict, directory: str = ".") -> list[Path]:
    """Compile the project's ruleset per its config. Returns written paths."""
    domains = config.get("domains", [])
    roles = config.get("roles", [])
    style = config.get("style", "compact")
    agent = config.get("agent", "claude-code")
    return engine.compile_project(
        domains, roles, style=style, out_dir=directory, agent=agent,
    )


def print_written(paths: list[Path]) -> None:
    for p in paths:
        print(f"  ✓ {p}")


def cmd_compile(args):
    config = load_config()
    config.setdefault("style", "compact")
    config.setdefault("domains", [])
    config.setdefault("roles", [])

    if getattr(args, "style", None):
        config["style"] = args.style

    agent = getattr(args, "agent", None) or config.get("agent", "claude-code")

    if agent == "all":
        style = config.get("style", "compact")
        domains = config.get("domains", [])
        roles = config.get("roles", [])
        for ag in engine.AGENTS:
            written = engine.compile_project(domains, roles, style=style, agent=ag)
            print(f"  ✓ {ag:<12} → {len(written)} files  ({style}, modular)")
        return

    config["agent"] = agent
    written = recompile(config)
    print(f"✓ Compiled (modular, {config.get('style')} style):")
    print_written(written)
