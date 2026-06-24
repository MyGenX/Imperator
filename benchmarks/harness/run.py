#!/usr/bin/env python3
"""Imperator benchmark orchestrator.

Runs the matrix of (task x condition x rep), collects deterministic metrics +
optional LLM-as-judge scores, and writes per-run JSON artifacts under
benchmarks/results/raw/<timestamp>/. Then hand that directory to aggregate.py.

Examples:
  python benchmarks/harness/run.py --dry-run
  python benchmarks/harness/run.py --task bug-fix-targeted \\
      --conditions control,imperator-compact --reps 1
  python benchmarks/harness/run.py --all --reps 3
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Allow `python benchmarks/harness/run.py` (script) and `-m` execution alike.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from harness import config, judge, metrics, runner, spec
else:
    from . import config, judge, metrics, runner, spec


def _claude_version() -> str:
    try:
        out = subprocess.run(["claude", "--version"], capture_output=True, text=True)
        return out.stdout.strip() or "unknown"
    except FileNotFoundError:
        return "not-found"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Imperator real-world benchmark runner")
    p.add_argument("--task", action="append", default=[],
                   help="task id (repeatable). Default: all discovered tasks")
    p.add_argument("--all", action="store_true", help="run every discovered task")
    p.add_argument("--conditions", default=",".join(config.DEFAULT_CONDITIONS),
                   help=f"comma list of {list(config.CONDITIONS)}")
    p.add_argument("--reps", type=int, default=config.DEFAULT_REPS)
    p.add_argument("--agent-model", default=config.DEFAULT_AGENT_MODEL)
    p.add_argument("--judge-model", default=config.DEFAULT_JUDGE_MODEL)
    p.add_argument("--max-turns", type=int, default=config.DEFAULT_MAX_TURNS)
    p.add_argument("--timeout", type=int, default=config.DEFAULT_AGENT_TIMEOUT)
    p.add_argument("--no-judge", action="store_true", help="skip LLM-as-judge scoring")
    p.add_argument("--keep-workdirs", action="store_true",
                   help="don't delete temp fixture copies (debugging)")
    p.add_argument("--dry-run", action="store_true",
                   help="validate tasks/conditions/wiring; make NO agent or API calls")
    return p.parse_args(argv)


def _resolve_tasks(args) -> list[str]:
    if args.all or not args.task:
        return spec.discover_tasks()
    return args.task


def _validate(task_ids: list[str], conditions: list[str]) -> list[str]:
    problems = spec.validate_all()
    for c in conditions:
        if c not in config.CONDITIONS:
            problems.append(f"Unknown condition '{c}'. Choices: {list(config.CONDITIONS)}")
    known = set(spec.discover_tasks())
    for t in task_ids:
        if t not in known:
            problems.append(f"Unknown task '{t}'. Discovered: {sorted(known)}")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    conditions = [c.strip() for c in args.conditions.split(",") if c.strip()]
    task_ids = _resolve_tasks(args)

    problems = _validate(task_ids, conditions)

    if args.dry_run:
        print("🔎 Dry-run validation")
        print(f"   tasks      : {task_ids}")
        print(f"   conditions : {conditions}")
        print(f"   reps       : {args.reps}")
        if problems:
            print("\n❌ Problems:")
            for pb in problems:
                print(f"   - {pb}")
            return 1
        print("\n✅ All task configs, fixtures, and conditions are valid. No calls made.")
        return 0

    if problems:
        print("❌ Refusing to run — fix these first:", file=sys.stderr)
        for pb in problems:
            print(f"   - {pb}", file=sys.stderr)
        return 1

    cfg = config.RunConfig(
        tasks=task_ids, conditions=conditions, reps=args.reps,
        agent_model=args.agent_model, judge_model=args.judge_model,
        max_turns=args.max_turns, timeout=args.timeout, judge=not args.no_judge,
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = config.RAW_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "timestamp": stamp,
        "claude_version": _claude_version(),
        "agent_model": cfg.agent_model,
        "judge_model": cfg.judge_model if cfg.judge else None,
        "reps": cfg.reps,
        "conditions": conditions,
        "tasks": task_ids,
        "rules_hash": _rules_hash(),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    total = len(task_ids) * len(conditions) * cfg.reps
    done = 0
    print(f"▶ {total} runs → {out_dir}\n")

    for tid in task_ids:
        task = spec.load_task(tid)
        reps = task.reps or cfg.reps
        for cname in conditions:
            cond = config.CONDITIONS[cname]
            for rep in range(reps):
                done += 1
                t0 = time.monotonic()
                print(f"[{done}/{total}] {tid} · {cname} · rep{rep} ...", end=" ", flush=True)
                raw = runner.run_cell(task, cond, rep, cfg)
                m = metrics.compute(raw, task)
                j = None
                if cfg.judge and not raw.error:
                    j = judge.score(raw, task, cfg)
                _write_run(out_dir, tid, cname, rep, m, j, raw)
                if not args.keep_workdirs:
                    runner.cleanup(raw)
                status = "ERR" if raw.error else ("ok" if m.correct is not False else "FAIL")
                print(f"{status} ({time.monotonic() - t0:.0f}s)")

    print(f"\n✅ Done. Aggregate with:\n   python benchmarks/harness/aggregate.py {out_dir}")
    return 0


def _write_run(out_dir, tid, cname, rep, m, j, raw) -> None:
    rec = {
        "task": tid,
        "condition": cname,
        "rep": rep,
        "metrics": m.to_dict(),
        "judge": (j.scores if (j and j.ok) else None),
        "judge_error": (j.error if (j and not j.ok) else None),
        "run_error": raw.error,
        "returncode": raw.returncode,
        "stderr_tail": raw.stderr_tail,
    }
    fname = f"{tid}__{cname}__rep{rep}.json"
    (out_dir / fname).write_text(json.dumps(rec, indent=2))


def _rules_hash() -> str:
    import hashlib
    h = hashlib.sha256()
    rules_dir = config.REPO_ROOT / "rules"
    if rules_dir.is_dir():
        for f in sorted(rules_dir.rglob("*.md")):
            h.update(f.read_bytes())
    return h.hexdigest()[:12]


if __name__ == "__main__":
    raise SystemExit(main())
