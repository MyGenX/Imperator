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
    layout = config.get("layout", "modular" if agent == "claude-code" else "flat")
    return engine.compile_project(
        domains, roles, style=style, out_dir=directory, agent=agent, layout=layout,
    )


def print_written(paths: list[Path]) -> None:
    for p in paths:
        print(f"  ✓ {p}")


def cmd_compile(args):
    config = load_config()
    config.setdefault("style", "compact")
    config.setdefault("layout", "modular")
    config.setdefault("domains", [])
    config.setdefault("roles", [])

    if getattr(args, "style", None):
        config["style"] = args.style
    if getattr(args, "layout", None):
        config["layout"] = args.layout

    agent = getattr(args, "agent", None) or config.get("agent", "claude-code")

    if agent == "all":
        # Flat single file for every supported agent (legacy multi-agent output).
        style = config.get("style", "compact")
        domains = config.get("domains", [])
        for ag in engine.AGENTS:
            path = engine.compile_to_agent(domains, ag, style=style)
            print(f"  ✓ {ag:<12} → {path}  ({style}, flat)")
        return

    config["agent"] = agent
    written = recompile(config)
    print(f"✓ Compiled ({config.get('layout')}, {config.get('style')} style):")
    print_written(written)
