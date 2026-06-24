"""Task specification loading + validation.

A task lives in `benchmarks/tasks/<id>/`:
  task.yaml   — metadata (prompt, extensions, rubric, ...)
  fixture/    — the starting repo state, copied fresh for every run
  verify.sh   — exit 0 = solved correctly (optional)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .config import TASKS_DIR


@dataclass
class Task:
    id: str
    dir: Path
    prompt: str
    extensions: list[str] = field(default_factory=list)
    profile: str | None = None
    reps: int | None = None              # per-task override of the global default
    expects_edits: bool = True           # answer-only tasks set this False
    rubric: str = ""                     # extra guidance for the LLM judge
    description: str = ""

    @property
    def fixture_dir(self) -> Path:
        return self.dir / "fixture"

    @property
    def verify_script(self) -> Path:
        return self.dir / "verify.sh"

    @property
    def has_verifier(self) -> bool:
        return self.verify_script.is_file()


def _resolve_extensions(data: dict) -> list[str]:
    """Profiles expand to extensions via the engine; explicit extensions win."""
    if data.get("extensions"):
        return list(data["extensions"])
    if data.get("profile"):
        from . import config  # noqa: F401  (ensures CLI_DIR is on sys.path)
        from imperator import engine
        return engine.resolve_profile(data["profile"])
    return []


def load_task(task_id: str) -> Task:
    tdir = TASKS_DIR / task_id
    yaml_path = tdir / "task.yaml"
    if not yaml_path.is_file():
        raise FileNotFoundError(f"Task '{task_id}': missing {yaml_path}")

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    if "prompt" not in data or not str(data["prompt"]).strip():
        raise ValueError(f"Task '{task_id}': task.yaml needs a non-empty 'prompt'.")
    if not (tdir / "fixture").is_dir():
        raise ValueError(f"Task '{task_id}': missing fixture/ directory.")

    return Task(
        id=task_id,
        dir=tdir,
        prompt=str(data["prompt"]).strip(),
        extensions=_resolve_extensions(data),
        profile=data.get("profile"),
        reps=data.get("reps"),
        expects_edits=bool(data.get("expects_edits", True)),
        rubric=str(data.get("rubric", "")).strip(),
        description=str(data.get("description", "")).strip(),
    )


def discover_tasks() -> list[str]:
    if not TASKS_DIR.is_dir():
        return []
    return sorted(
        p.name for p in TASKS_DIR.iterdir()
        if p.is_dir() and (p / "task.yaml").is_file()
    )


def validate_all() -> list[str]:
    """Load every task; return a list of human-readable problems (empty == OK)."""
    problems: list[str] = []
    ids = discover_tasks()
    if not ids:
        problems.append(f"No tasks found under {TASKS_DIR}")
    for tid in ids:
        try:
            t = load_task(tid)
            if not t.has_verifier and t.expects_edits:
                problems.append(
                    f"Task '{tid}': expects_edits=true but has no verify.sh "
                    "(correctness can't be checked)."
                )
        except Exception as exc:  # noqa: BLE001
            problems.append(f"Task '{tid}': {exc}")
    return problems
