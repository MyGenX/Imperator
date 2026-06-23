"""imperator compile — generate agent-specific rule files."""

from __future__ import annotations

from .. import engine
from ..config import load_config


def cmd_compile(args):
    config = load_config()

    extensions = config.get("extensions", [])
    style = getattr(args, "style", None) or config.get("style", "compact")
    agent = getattr(args, "agent", None) or config.get("agent", "claude-code")

    agents = list(engine.AGENTS) if agent == "all" else [agent]

    for ag in agents:
        path = engine.compile_to_agent(extensions, ag, style=style)
        print(f"✓ {ag:<12} → {path}  ({style})")
