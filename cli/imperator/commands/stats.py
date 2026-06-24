"""imperator stats — estimate compiled size and token impact by tier."""

from __future__ import annotations

from .. import engine
from ..config import load_config


def cmd_stats(args):
    config = load_config()
    domains = config.get("domains", [])
    roles = config.get("roles", [])
    style = config.get("style", "compact")

    global_groups = engine.filter_by_agent(engine.load_global(), "claude-code")
    domain_groups = engine.filter_by_agent(engine.load_domains(domains), "claude-code")
    role_defs = engine.load_roles(roles)

    global_text = engine.render_global_file(global_groups, style)
    g_tok = engine.estimate_tokens(global_text)

    print("\n👑 Imperator — Stats\n" + "─" * 48)
    print(f"  Style   : {style}")
    print(f"  Domains : {', '.join(domains) if domains else 'none'}")
    print(f"  Roles   : {', '.join(roles) if roles else 'none'}")
    print()
    print("  Always-on context (loaded every session):")
    print(f"    global.md          {len(global_text):>6} chars  ≈ {g_tok:>5} tokens")
    print()

    if domain_groups:
        print("  Path-scoped (load only when editing matching files):")
        total_scoped = 0
        for g in domain_groups:
            text = engine.render_domain_file(g, style)
            total_scoped += len(text)
            globs = ", ".join(g.paths) if g.paths else "(always)"
            print(f"    {g.source:<16} {len(text):>6} chars  ≈ "
                  f"{engine.estimate_tokens(text):>5} tokens   {globs}")
        print(f"    {'(sum, not all at once)':<16} {total_scoped:>6} chars")
        print()

    if role_defs:
        print("  Role subagents (separate context windows):")
        for role in role_defs:
            text = engine.render_role_agent(role, global_groups, domain_groups, style)
            print(f"    {role.name:<20} {len(text):>6} chars  ≈ "
                  f"{engine.estimate_tokens(text):>5} tokens")
        print()

    print("  The win: only global.md is always in context. Domain rules load on demand,")
    print("  and role rules live in their own subagent windows — not your main session.\n")
