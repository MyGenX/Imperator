#!/usr/bin/env python3
"""Maintainer build tool.

  - Smoke-builds every supported agent's native output from `rules/` (no committed
    `agents/` snapshots).
  - Regenerates the committed distribution: the Claude Code plugin under
    `plugins/imperator/` and the repo-root `.claude-plugin/marketplace.json`.

Run with `--check` in CI to fail if the committed plugin/marketplace drift from the
rule sources (i.e. were hand-edited instead of regenerated).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "cli"))

from imperator import engine  # noqa: E402

ALL_DOMAINS = list(engine.DOMAINS_AVAILABLE)
ALL_ROLES = list(engine.ROLES_AVAILABLE)
STYLE = "compact"


def smoke_build() -> list[str]:
    summaries: list[str] = []
    with TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        for agent in engine.AGENTS:
            out_dir = tmp_root / agent
            written = engine.compile_project(
                ALL_DOMAINS, ALL_ROLES, style=STYLE,
                out_dir=out_dir, agent=agent, root=REPO_ROOT,
            )
            if not written:
                raise RuntimeError(f"{agent} generated no files")
            summaries.append(f"{agent}: {len(written)} files")
    return summaries


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Smoke-build agent outputs and sync the committed plugin/marketplace")
    parser.add_argument("--check", action="store_true",
                        help="Verify the committed plugin/marketplace are in sync (no writes)")
    args = parser.parse_args(argv)

    from imperator.renderers import skills  # noqa: E402

    # Per-agent generation must keep working for every supported agent.
    for summary in smoke_build():
        print(f"✓ {summary}")

    if args.check:
        problems = skills.check_distribution(REPO_ROOT, STYLE)
        if problems:
            print("✗ Plugin/marketplace out of sync (run: python compiler/compile.py):")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("✓ plugin/marketplace: in sync")
        return 0

    written = skills.write_distribution(REPO_ROOT, STYLE)
    print(f"✓ plugin/marketplace: wrote {len(written)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
