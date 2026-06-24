#!/usr/bin/env python3
"""Regenerate the committed `agents/` example outputs from the full ruleset.

This is a maintainer tool. End users use the `imperator` CLI instead.

  - claude-code: modular `.claude/` layout (rules/ + agents/) under agents/claude-code/
  - cursor / codex / gemini: legacy flat single file

Usage:
    python compiler/compile.py            # write examples
    python compiler/compile.py --check    # exit 1 if any output is stale (CI)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "cli"))

from imperator import engine  # noqa: E402

# The committed examples showcase the full ruleset in compact style.
ALL_DOMAINS = list(engine.DOMAINS_AVAILABLE)
ALL_ROLES = list(engine.ROLES_AVAILABLE)
STYLE = "compact"

CLAUDE_DIR = REPO_ROOT / "agents" / "claude-code"
FLAT_AGENTS = ["cursor", "codex", "gemini"]


def build_outputs() -> dict[Path, str]:
    """Return {absolute path: content} for every committed example file."""
    out: dict[Path, str] = {}

    # claude-code modular layout
    global_groups = engine.filter_by_agent(engine.load_global(REPO_ROOT), "claude-code")
    domain_groups = engine.filter_by_agent(
        engine.load_domains(ALL_DOMAINS, REPO_ROOT), "claude-code"
    )
    roles = engine.load_roles(ALL_ROLES, REPO_ROOT)

    base = CLAUDE_DIR / ".claude"
    out[base / "CLAUDE.md"] = engine.render_claude_md(ALL_DOMAINS, ALL_ROLES)
    out[base / "rules" / "global.md"] = engine.render_global_file(global_groups, STYLE)
    for g in domain_groups:
        out[base / "rules" / f"{g.source}.md"] = engine.render_domain_file(g, STYLE)
    for role in roles:
        out[base / "agents" / f"{role.name}.md"] = engine.render_role_agent(
            role, global_groups, domain_groups, STYLE
        )

    # flat single-file agents
    for agent in FLAT_AGENTS:
        groups = engine.filter_by_agent(
            engine.load_groups(ALL_DOMAINS, root=REPO_ROOT), agent
        )
        filename, _ = engine.AGENTS[agent]
        out[REPO_ROOT / "agents" / agent / filename] = engine.render(groups, agent, STYLE)

    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate committed agent examples")
    parser.add_argument("--check", action="store_true",
                        help="Verify committed outputs are current (no writes)")
    args = parser.parse_args(argv)

    outputs = build_outputs()
    expected = set(outputs)

    if args.check:
        stale: list[str] = []
        for path, content in outputs.items():
            current = path.read_text(encoding="utf-8") if path.is_file() else None
            if current != content:
                stale.append(str(path.relative_to(REPO_ROOT)))
        # Flag committed files under .claude/ that are no longer generated.
        committed = {p for p in (CLAUDE_DIR / ".claude").rglob("*.md")} if (CLAUDE_DIR / ".claude").is_dir() else set()
        for extra in sorted(committed - expected):
            stale.append(f"{extra.relative_to(REPO_ROOT)} (no longer generated)")
        if stale:
            print("✗ Stale committed outputs (run: python compiler/compile.py):")
            for s in stale:
                print(f"  - {s}")
            return 1
        print("✓ All committed agent outputs are up to date.")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"✓ wrote {path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
