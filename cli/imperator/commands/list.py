"""imperator list — show available domains and roles."""

from __future__ import annotations

from .. import engine


def cmd_list(args):
    print("\n👑 Imperator — Available\n" + "─" * 40)

    print("\nProfiles (domain bundles):\n")
    for name, doms in engine.PROFILES.items():
        print(f"  {name:<16} {', '.join(doms) if doms else 'core only'}")

    print("\nDomains (tech stacks — `imperator add <name>`):\n")
    for g in engine.load_domains(engine.DOMAINS_AVAILABLE):
        globs = ", ".join(g.paths) if g.paths else "(always)"
        print(f"  {g.source:<14} {globs}")

    print("\nRoles (subagents — `imperator role add <name>`):\n")
    for r in engine.load_roles(engine.ROLES_AVAILABLE):
        doms = ", ".join(r.domains) if r.domains else "—"
        print(f"  {r.name:<20} domains: {doms}")
    print()
