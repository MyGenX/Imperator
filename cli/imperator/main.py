#!/usr/bin/env python3
"""Imperator CLI — Command your AI agent."""

from __future__ import annotations

import argparse
import sys

from . import engine
from .commands.add import cmd_add
from .commands.compile import cmd_compile
from .commands.init import cmd_init
from .commands.stats import cmd_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="imperator",
        description="👑 Imperator — Reusable rules for AI coding agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  imperator init                         Interactive project setup
  imperator init --profile fullstack-js  Use a pre-built profile
  imperator add nextjs postgres          Add extension rules
  imperator compile --agent all          Generate files for every agent
  imperator stats                        Show compiled size / token estimate
        """,
    )
    parser.add_argument("--version", "-v", action="version",
                        version=f"Imperator {engine.VERSION}")

    sub = parser.add_subparsers(dest="command", metavar="command")

    p_init = sub.add_parser("init", help="Interactive setup for your project")
    p_init.add_argument("--profile", choices=list(engine.PROFILES))
    p_init.add_argument("--agent", choices=list(engine.AGENTS))
    p_init.add_argument("--style", choices=engine.STYLES)

    p_add = sub.add_parser("add", help="Add extension rules to your project")
    p_add.add_argument("extensions", nargs="+",
                       help="Extensions to add (e.g. nextjs react postgres)")

    p_compile = sub.add_parser("compile", help="Compile rules into agent files")
    p_compile.add_argument("--agent", choices=list(engine.AGENTS) + ["all"])
    p_compile.add_argument("--style", choices=engine.STYLES)

    sub.add_parser("stats", help="Show estimated token impact")

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
        "compile": cmd_compile,
        "stats": cmd_stats,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
