"""imperator add — add extension rules to the project and recompile."""

from __future__ import annotations

import sys

from .. import engine
from ..config import load_config, save_config


def cmd_add(args):
    config = load_config()
    if not config:
        print("✗ No .imperator.json found. Run 'imperator init' first.")
        sys.exit(1)

    unknown = [e for e in args.extensions if e not in engine.EXTENSIONS_AVAILABLE]
    if unknown:
        print(f"✗ Unknown extension(s): {', '.join(unknown)}")
        print(f"  Available: {', '.join(engine.EXTENSIONS_AVAILABLE)}")
        sys.exit(1)

    extensions = list(config.get("extensions", []))
    for ext in args.extensions:
        if ext not in extensions:
            extensions.append(ext)

    agent = config.get("agent", "claude-code")
    style = config.get("style", "compact")

    path = engine.compile_to_agent(extensions, agent, style=style)
    save_config(agent, extensions, style)

    print(f"✓ Extensions now active: {', '.join(extensions)}")
    print(f"✓ Regenerated {path} ({style} style)")
