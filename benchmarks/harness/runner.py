"""Execute a single (task, condition, rep) cell against Claude Code headless.

Flow:
  1. Copy the task fixture into a throwaway temp dir and git-init it (so a
     post-run diff is meaningful).
  2. For rule conditions, compile a CLAUDE.md into the copy via the engine.
  3. Run `claude -p ... --output-format stream-json --verbose` with cwd=copy.
  4. Return the raw transcript events + the working dir so metrics can inspect
     both the transcript and the resulting git diff.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Condition, RunConfig
from .spec import Task

# Engine is importable thanks to config.py putting cli/ on sys.path.
from imperator import engine


@dataclass
class RawRun:
    task_id: str
    condition: str
    rep: int
    events: list[dict]        # parsed stream-json events
    workdir: Path             # the post-run fixture copy (for git diff / verify)
    returncode: int
    wall_seconds: float
    stderr_tail: str
    error: str | None = None  # set if the run could not be executed


def _git(workdir: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=workdir, capture_output=True, text=True,
        env={"GIT_TERMINAL_PROMPT": "0", "HOME": str(workdir), "PATH": _path()},
    )


def _path() -> str:
    import os
    return os.environ.get("PATH", "/usr/bin:/bin")


def _prepare_workdir(task: Task) -> Path:
    """Copy fixture into a fresh temp dir and commit it as the baseline."""
    tmp = Path(tempfile.mkdtemp(prefix=f"imp-bench-{task.id}-"))
    workdir = tmp / "repo"
    shutil.copytree(task.fixture_dir, workdir)

    _git(workdir, "init", "-q")
    _git(workdir, "config", "user.email", "bench@imperator.local")
    _git(workdir, "config", "user.name", "Imperator Bench")
    _git(workdir, "add", "-A")
    _git(workdir, "commit", "-q", "-m", "fixture baseline")
    return workdir


def _apply_rules(workdir: Path, condition: Condition, task: Task) -> None:
    if not condition.uses_rules:
        return
    # Write the modular .claude/ layout (global + path-scoped domains). Roles are
    # omitted here: benchmark tasks are single prompts, not role-delegated work.
    engine.compile_project(
        domains=task.extensions,
        roles=[],
        style=condition.style,
        out_dir=workdir,
        agent="claude-code",
    )
    # The compiled .claude/ tree is part of the given scaffold, not an agent edit —
    # commit it so it never shows up in the post-run diff.
    _git(workdir, "add", ".claude")
    _git(workdir, "commit", "-q", "-m", "imperator ruleset")


def _build_command(prompt: str, cfg: RunConfig) -> list[str]:
    return [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--model", cfg.agent_model,
        "--permission-mode", "bypassPermissions",
        "--max-turns", str(cfg.max_turns),
    ]


def run_cell(task: Task, condition: Condition, rep: int, cfg: RunConfig) -> RawRun:
    workdir = _prepare_workdir(task)
    try:
        _apply_rules(workdir, condition, task)
    except Exception as exc:  # noqa: BLE001
        return RawRun(task.id, condition.name, rep, [], workdir, -1, 0.0, "",
                      error=f"rule compilation failed: {exc}")

    cmd = _build_command(task.prompt, cfg)
    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, cwd=workdir, capture_output=True, text=True, timeout=cfg.timeout,
        )
    except subprocess.TimeoutExpired:
        return RawRun(task.id, condition.name, rep, [], workdir, -1,
                      time.monotonic() - start, "", error="agent run timed out")
    except FileNotFoundError:
        return RawRun(task.id, condition.name, rep, [], workdir, -1, 0.0, "",
                      error="`claude` CLI not found on PATH")
    wall = time.monotonic() - start

    events: list[dict] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # non-JSON noise; ignore

    return RawRun(
        task_id=task.id,
        condition=condition.name,
        rep=rep,
        events=events,
        workdir=workdir,
        returncode=proc.returncode,
        wall_seconds=wall,
        stderr_tail=proc.stderr[-2000:] if proc.stderr else "",
    )


def cleanup(run: RawRun) -> None:
    """Remove the temp tree for a completed run (its top-level mkdtemp dir)."""
    top = run.workdir.parent  # workdir is <tmp>/repo, so parent is the mkdtemp dir
    if top.exists() and top.name.startswith("imp-bench-"):
        shutil.rmtree(top, ignore_errors=True)
