"""imperator stats — estimate compiled size and token impact."""

from __future__ import annotations

from .. import engine
from ..config import load_config


def cmd_stats(args):
    config = load_config()
    extensions = config.get("extensions", [])
    agent = config.get("agent", "claude-code")
    style = config.get("style", "compact")

    groups = engine.filter_by_agent(engine.load_groups(extensions), agent)
    rule_count = sum(len(g.rules) for g in groups)

    compact = engine.render(groups, agent, "compact")
    full = engine.render(groups, agent, "full")

    print("\n👑 Imperator — Stats\n" + "─" * 40)
    print(f"  Agent        : {agent}")
    print(f"  Style        : {style}")
    print(f"  Extensions   : {', '.join(extensions) if extensions else 'core only'}")
    print(f"  Rules active : {rule_count}")
    print()
    print(f"  Compiled size (compact) : {len(compact):>6} chars  "
          f"≈ {engine.estimate_tokens(compact):>5} tokens")
    print(f"  Compiled size (full)    : {len(full):>6} chars  "
          f"≈ {engine.estimate_tokens(full):>5} tokens")
    print()
    print("  Note: token figures are a ~4-chars/token heuristic. Real savings come")
    print("  from the *behavior* these rules enforce (no preamble, no full-file")
    print("  rewrites, targeted reads) across every session — not the file size.\n")
