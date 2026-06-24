"""imperator init — interactive project setup."""

from __future__ import annotations

from .. import engine
from ..config import save_config
from .compile import print_written, recompile


def cmd_init(args):
    print("\n👑 Imperator — Project Setup\n" + "─" * 40)

    if getattr(args, "profile", None):
        domains = engine.resolve_profile(args.profile)
        print(f"✓ Using profile: {args.profile} ({', '.join(domains) or 'core only'})")
    else:
        domains = _interactive_pick("domains (tech stacks)", engine.DOMAINS_AVAILABLE)

    roles = getattr(args, "roles", None)
    if roles is None:
        # Scripted run (profile given) → no roles unless --role is passed.
        roles = [] if getattr(args, "profile", None) else \
            _interactive_pick("roles (specialist subagents)", engine.ROLES_AVAILABLE)

    agent = getattr(args, "agent", None) or _select_agent()
    style = getattr(args, "style", None) or _select_style()
    layout = getattr(args, "layout", None) or (
        "modular" if agent == "claude-code" else "flat"
    )

    config = {"agent": agent, "domains": domains, "roles": roles,
              "style": style, "layout": layout}
    written = recompile(config)
    save_config(agent, domains, roles, style, layout)

    print("\n✓ Imperator setup complete!\n")
    print(f"  Agent   : {agent}  ({layout} layout, {style} style)")
    print(f"  Domains : {', '.join(domains) if domains else 'none'}")
    print(f"  Roles   : {', '.join(roles) if roles else 'none'}")
    print("\n  Written:")
    print_written(written)
    print("\n  Run 'imperator compile' anytime to regenerate.\n")


def _interactive_pick(label: str, choices: list[str]) -> list[str]:
    print(f"\nSelect {label}:\n")
    for i, c in enumerate(choices, 1):
        print(f"  [{i}] {c}")
    print("\nEnter numbers separated by commas (Enter to skip):\n")
    raw = input("  → ").strip()
    if not raw:
        return []
    selected: list[str] = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(choices) and choices[idx] not in selected:
                selected.append(choices[idx])
    return selected


def _select_agent() -> str:
    agents = list(engine.AGENTS)
    print("\nSelect your AI agent:\n")
    for i, agent in enumerate(agents, 1):
        marker = "  (modular .claude/ layout)" if agent == "claude-code" else ""
        print(f"  [{i}] {agent}{marker}")
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
