"""imperator role — manage specialist role subagents."""

from __future__ import annotations

import sys

from .. import engine
from ..config import load_config, save_config
from .compile import print_written, recompile


def cmd_role(args):
    action = args.action

    if action == "list":
        _list_roles()
        return

    config = load_config()
    if not config:
        print("✗ No .imperator.json found. Run 'imperator init' first.")
        sys.exit(1)

    requested = args.roles or []
    unknown = [r for r in requested if r not in engine.ROLES_AVAILABLE]
    if unknown:
        print(f"✗ Unknown role(s): {', '.join(unknown)}")
        print(f"  Available: {', '.join(engine.ROLES_AVAILABLE)}")
        sys.exit(1)

    roles = list(config.get("roles", []))
    if action == "add":
        for r in requested:
            if r not in roles:
                roles.append(r)
    elif action == "remove":
        roles = [r for r in roles if r not in requested]

    config["roles"] = roles
    written = recompile(config)
    save_config(config["agent"], config.get("domains", []), roles,
                config["style"], config.get("layout", "modular"))

    print(f"✓ Roles now active: {', '.join(roles) if roles else 'none'}")
    if config.get("agent") != "claude-code" or config.get("layout") == "flat":
        print("  Note: roles compile to subagents only for claude-code modular layout.")
    print_written(written)


def _list_roles():
    print("\nAvailable roles:\n")
    for r in engine.load_roles(engine.ROLES_AVAILABLE):
        doms = ", ".join(r.domains) if r.domains else "—"
        print(f"  {r.name:<20} domains: {doms}")
        print(f"  {'':<20} {r.description}\n")
