#!/usr/bin/env python3
"""Regenerate the committed `agents/` example outputs from the full ruleset.

This is a maintainer tool. End users use the `imperator` CLI instead.

Usage:
    python compiler/compile.py            # write agents/<agent>/<file>
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
EXAMPLE_EXTENSIONS = list(engine.EXTENSIONS_AVAILABLE)
EXAMPLE_STYLE = "compact"


def render_for(agent: str) -> tuple[Path, str]:
    groups = engine.filter_by_agent(
        engine.load_groups(EXAMPLE_EXTENSIONS, root=REPO_ROOT), agent
    )
    content = engine.render(groups, agent, EXAMPLE_STYLE)
    filename, _ = engine.AGENTS[agent]
    out_path = REPO_ROOT / "agents" / agent / filename
    return out_path, content


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate committed agent examples")
    parser.add_argument("--check", action="store_true",
                        help="Verify committed outputs are current (no writes)")
    args = parser.parse_args(argv)

    stale: list[str] = []
    for agent in engine.AGENTS:
        out_path, content = render_for(agent)
        if args.check:
            current = out_path.read_text(encoding="utf-8") if out_path.is_file() else None
            if current != content:
                stale.append(str(out_path.relative_to(REPO_ROOT)))
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            print(f"✓ wrote {out_path.relative_to(REPO_ROOT)}")

    if args.check:
        if stale:
            print("✗ Stale committed outputs (run: python compiler/compile.py):")
            for s in stale:
                print(f"  - {s}")
            return 1
        print("✓ All committed agent outputs are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
