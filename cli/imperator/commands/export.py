"""imperator export — emit Imperator rules as installable skill bundles."""

from __future__ import annotations

import sys
from pathlib import Path

from ..config import load_config
from ..renderers import build_skills_bundle

FORMATS = ["skills"]
DEFAULT_OUT = "dist/skills"


def cmd_export(args) -> None:
    fmt = getattr(args, "format", "skills")
    if fmt not in FORMATS:
        print(f"✗ Unknown format '{fmt}'. Choices: {', '.join(FORMATS)}")
        sys.exit(1)

    out = Path(getattr(args, "out", None) or DEFAULT_OUT)
    style = load_config().get("style", "compact")

    written = build_skills_bundle(out, style=style)

    print(f"✓ Exported {len(written)} skills ({fmt}) → {out}")
    for path in written:
        print(f"  ✓ {path.relative_to(out).as_posix()}")
    print("\n  Install with the Vercel skills CLI, e.g.:")
    print(f"    npx skills add {out} --list")
