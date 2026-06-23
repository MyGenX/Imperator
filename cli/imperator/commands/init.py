"""imperator init — interactive project setup."""

from __future__ import annotations

from .. import engine
from ..config import save_config


def cmd_init(args):
    print("\n👑 Imperator — Project Setup\n" + "─" * 40)

    if getattr(args, "profile", None):
        selected = engine.resolve_profile(args.profile)
        print(f"✓ Using profile: {args.profile}")
    else:
        selected = _interactive_extensions()

    agent = getattr(args, "agent", None) or _select_agent()
    style = getattr(args, "style", None) or _select_style()

    path = engine.compile_to_agent(selected, agent, style=style)
    save_config(agent, selected, style)

    print("\n✓ Imperator setup complete!\n")
    print(f"  Agent file: {path} ({style} style)")
    print(f"  Extensions: {', '.join(selected) if selected else 'core only'}")
    print("\n  Run 'imperator compile' anytime to regenerate.\n")


def _interactive_extensions() -> list[str]:
    print("\nAvailable extensions:\n")
    for i, ext in enumerate(engine.EXTENSIONS_AVAILABLE, 1):
        print(f"  [{i}] {ext}")
    print("\nEnter numbers separated by commas (Enter for core only):\n")

    raw = input("  → ").strip()
    if not raw:
        return []

    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(engine.EXTENSIONS_AVAILABLE):
                selected.append(engine.EXTENSIONS_AVAILABLE[idx])
    return selected


def _select_agent() -> str:
    agents = list(engine.AGENTS)
    print("\nSelect your AI agent:\n")
    for i, agent in enumerate(agents, 1):
        print(f"  [{i}] {agent}")
    raw = input("\n  → ").strip()
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(agents):
            return agents[idx]
    return "claude-code"


def _select_style() -> str:
    print("\nRule output style:\n")
    print("  [1] compact   (## ID · name · severity — lean)")
    print("  [2] full      (per-rule YAML frontmatter — verbose, machine-readable)")
    raw = input("\n  → ").strip()
    return "full" if raw == "2" else "compact"
