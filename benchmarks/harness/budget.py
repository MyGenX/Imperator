#!/usr/bin/env python3
"""Token-cost regression gate for the benchmark.

Loads a results/raw/<timestamp>/ directory, recomputes the treatment-vs-control
deltas (reusing aggregate.py), and checks them against the ceilings in
benchmarks/budgets.yaml. Exits non-zero if any task breaches its budget, so a
rule change that re-inflates query cost is caught before it ships.

This needs *real* runs to check against, so — like the suite itself — it is not
part of default CI. Run it right after aggregate.py:

  python benchmarks/harness/budget.py benchmarks/results/raw/<timestamp>
  python benchmarks/harness/budget.py <dir> --budgets benchmarks/budgets.yaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from harness import aggregate, config
else:
    from . import aggregate, config

CONTROL = aggregate.CONTROL

# metric in budgets.yaml -> metric key in the per-cell stats
_PCT_CHECKS = {
    "max_total_pct": "total_tokens",
    "max_output_pct": "output_tokens",
    "max_preamble_pct": "preamble_chars",
}

DEFAULT_BUDGETS = config.BENCHMARKS_DIR / "budgets.yaml"


def _delta_pct(treat: float, ctrl: float) -> float | None:
    if ctrl == 0:
        return None
    return (treat - ctrl) / ctrl * 100.0


def _threshold(budgets: dict, task: str, key: str):
    """Per-task override wins; `null` (None) means 'don't check'. Missing == default."""
    task_cfg = (budgets.get("tasks") or {}).get(task) or {}
    if key in task_cfg:
        return task_cfg[key]
    return (budgets.get("defaults") or {}).get(key)


def check(raw_dir: Path, budgets: dict) -> tuple[list[str], list[str]]:
    """Return (violations, notes). Empty violations == within budget."""
    runs, _meta = aggregate._load(raw_dir)
    cells = aggregate._cell_stats(runs)
    treatment = budgets.get("treatment", "imperator-compact")

    tasks = sorted({k[0] for k in cells})
    violations: list[str] = []
    notes: list[str] = []

    for task in tasks:
        ctrl = cells.get((task, CONTROL))
        treat = cells.get((task, treatment))
        if not treat:
            continue
        if not ctrl:
            notes.append(f"{task}: no control cell — skipped")
            continue

        for bkey, metric in _PCT_CHECKS.items():
            ceiling = _threshold(budgets, task, bkey)
            if ceiling is None:
                continue
            d = _delta_pct(treat[metric][0], ctrl[metric][0])
            if d is None:
                continue
            verdict = "ok" if d <= ceiling else "FAIL"
            line = f"{task}: {metric} Δ {d:+.0f}% (ceiling {ceiling:+.0f}%) {verdict}"
            (violations if verdict == "FAIL" else notes).append(line)

        floor = _threshold(budgets, task, "min_correct_rate")
        rate = treat.get("correct_rate")
        if floor is not None and rate is not None:
            verdict = "ok" if rate >= floor else "FAIL"
            line = f"{task}: correct_rate {rate * 100:.0f}% (floor {floor * 100:.0f}%) {verdict}"
            (violations if verdict == "FAIL" else notes).append(line)

    return violations, notes


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    ap = argparse.ArgumentParser(description="Benchmark token-cost regression gate")
    ap.add_argument("raw_dir", help="results/raw/<timestamp> directory to check")
    ap.add_argument("--budgets", default=str(DEFAULT_BUDGETS),
                    help="path to budgets.yaml (default: benchmarks/budgets.yaml)")
    args = ap.parse_args(argv)

    raw_dir = Path(args.raw_dir).resolve()
    if not raw_dir.is_dir():
        print(f"Not a directory: {raw_dir}", file=sys.stderr)
        return 2
    budgets = yaml.safe_load(Path(args.budgets).read_text(encoding="utf-8")) or {}

    violations, notes = check(raw_dir, budgets)

    for line in notes:
        print(f"  · {line}")
    if violations:
        print("\n❌ Budget exceeded:", file=sys.stderr)
        for v in violations:
            print(f"   - {v}", file=sys.stderr)
        return 1
    print("\n✅ All tasks within token budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
