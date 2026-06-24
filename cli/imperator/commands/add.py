"""imperator add — add domain (tech-stack) rules and recompile."""

from __future__ import annotations

import sys

from .. import engine
from ..config import load_config, save_config
from .compile import print_written, recompile


def cmd_add(args):
    config = load_config()
    if not config:
        print("✗ No .imperator.json found. Run 'imperator init' first.")
        sys.exit(1)

    unknown = [d for d in args.domains if d not in engine.DOMAINS_AVAILABLE]
    if unknown:
        print(f"✗ Unknown domain(s): {', '.join(unknown)}")
        print(f"  Available: {', '.join(engine.DOMAINS_AVAILABLE)}")
        sys.exit(1)

    domains = list(config.get("domains", []))
    for d in args.domains:
        if d not in domains:
            domains.append(d)
    config["domains"] = domains

    written = recompile(config)
    save_config(config["agent"], domains, config.get("roles", []),
                config["style"], config.get("layout", "modular"))

    print(f"✓ Domains now active: {', '.join(domains) if domains else 'none'}")
    print_written(written)
