"""imperator clean — remove Imperator-generated agent files safely."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .. import engine

GENERATED_DIRS = [".claude", ".cursor", ".codex", ".gemini"]
GENERATED_FILES = ["AGENTS.md", "GEMINI.md", ".cursorrules"]


@dataclass
class CleanResult:
    removed: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


def _is_owned_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        return engine.is_generated_content(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return False


def clean_project(root: str | Path = ".", dry_run: bool = False) -> CleanResult:
    root = Path(root)
    result = CleanResult()

    for name in GENERATED_FILES:
        path = root / name
        if not path.exists():
            continue
        if _is_owned_file(path):
            result.removed.append(path)
            if not dry_run:
                path.unlink()
        else:
            result.skipped.append(path)

    for name in GENERATED_DIRS:
        directory = root / name
        if not directory.exists():
            continue
        if not directory.is_dir():
            result.skipped.append(directory)
            continue

        for path in sorted((p for p in directory.rglob("*") if p.is_file()), reverse=True):
            if _is_owned_file(path):
                result.removed.append(path)
                if not dry_run:
                    path.unlink()
            else:
                result.skipped.append(path)

        if not dry_run:
            for path in sorted((p for p in directory.rglob("*") if p.is_dir()), reverse=True):
                try:
                    path.rmdir()
                except OSError:
                    pass
            try:
                directory.rmdir()
                result.removed.append(directory)
            except OSError:
                pass
        elif not any(directory.rglob("*")):
            result.removed.append(directory)

    return result


def cmd_clean(args) -> None:
    dry_run = bool(getattr(args, "dry_run", False))
    result = clean_project(dry_run=dry_run)
    action = "Would remove" if dry_run else "Removed"

    if result.removed:
        print(f"{action}:")
        for path in result.removed:
            print(f"  ✓ {path}")
    else:
        print("No Imperator-generated files found.")

    if result.skipped:
        print("\nSkipped user-authored or unrecognized files:")
        for path in result.skipped:
            print(f"  - {path}")
