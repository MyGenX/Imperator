#!/usr/bin/env python3
"""Imperator CLI — Command your AI agent."""

from __future__ import annotations

import argparse
import sys

from . import engine
from .commands.add import cmd_add
from .commands.compile import cmd_compile
from .commands.init import cmd_init
from .commands.list import cmd_list
from .commands.role import cmd_role
from .commands.stats import cmd_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imperator",
        description="👑 Imperator — Reusable rules for AI coding agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  imperator init                          Interactive project setup
  imperator init --profile python-api     Use a pre-built domain bundle
  imperator add python typescript         Add tech-stack (domain) rules
  imperator role add backend-developer qa-engineer   Add specialist subagents
  imperator role list                     Show available roles
  imperator list                          Show all domains and roles
  imperator compile                       Regenerate .claude/ from config
  imperator compile --layout flat         Single-file output instead
  imperator stats                         Token impact by tier
        """,
    )
    parser.add_argument("--version", "-v", action="version",
                        version=f"Imperator {engine.VERSION}")

    sub = parser.add_subparsers(dest="command", metavar="command")

    p_init = sub.add_parser("init", help="Interactive setup for your project")
    p_init.add_argument("--profile", choices=list(engine.PROFILES))
    p_init.add_argument("--agent", choices=list(engine.AGENTS))
    p_init.add_argument("--style", choices=engine.STYLES)
    p_init.add_argument("--layout", choices=engine.LAYOUTS)
    p_init.add_argument("--role", dest="roles", action="append", default=None,
                        choices=engine.ROLES_AVAILABLE,
                        help="Add a role (repeatable); skips the interactive role prompt")

    p_add = sub.add_parser("add", help="Add domain (tech-stack) rules")
    p_add.add_argument("domains", nargs="+",
                       help="Domains to add (e.g. python typescript postgres)")

    p_role = sub.add_parser("role", help="Manage specialist role subagents")
    p_role.add_argument("action", choices=["add", "remove", "list"])
    p_role.add_argument("roles", nargs="*",
                        help="Role names (e.g. backend-developer qa-engineer)")

    p_compile = sub.add_parser("compile", help="Compile rules into agent files")
    p_compile.add_argument("--agent", choices=list(engine.AGENTS) + ["all"])
    p_compile.add_argument("--style", choices=engine.STYLES)
    p_compile.add_argument("--layout", choices=engine.LAYOUTS)

    sub.add_parser("stats", help="Show estimated token impact by tier")
    sub.add_parser("list", help="Show available domains and roles")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "role": cmd_role,
        "compile": cmd_compile,
        "stats": cmd_stats,
        "list": cmd_list,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
