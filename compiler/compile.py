#!/usr/bin/env python3
"""Smoke-build generated agent outputs from the full ruleset.

The repository no longer commits generated `agents/` snapshots. This maintainer
tool verifies that every supported agent can still be generated from `rules/`
and the CLI templates.
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
    parser = argparse.ArgumentParser(description="Smoke-build generated agent outputs")
    parser.add_argument("--check", action="store_true",
                        help="Alias for the default smoke build")
    parser.parse_args(argv)

    for summary in smoke_build():
        print(f"✓ {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
