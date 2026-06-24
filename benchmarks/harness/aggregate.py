#!/usr/bin/env python3
"""Aggregate raw benchmark runs into benchmarks/results/results.md.

Reads a results/raw/<timestamp>/ directory of per-run JSON files, computes
mean/stddev across repetitions per (task, condition), derives treatment-vs-control
deltas, and renders the report. Also (re)generates the static ruleset-size section.

Usage:
  python benchmarks/harness/aggregate.py benchmarks/results/raw/<timestamp>
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from harness import config
else:
    from . import config

from imperator import engine

# metric -> (label, lower_is_better)
NUMERIC = {
    "total_tokens": ("Total tokens", True),
    "output_tokens": ("Output tokens", True),
    "tool_calls": ("Tool calls", True),
    "bytes_read": ("Bytes read", True),
    "files_changed": ("Files changed", True),
    "lines_added": ("Lines +", True),
    "lines_deleted": ("Lines −", True),
    "preamble_chars": ("Preamble chars", True),
    "num_turns": ("Turns", True),
    "latency_ms": ("Latency ms", True),
    "cost_usd": ("Cost $", True),
}

CONTROL = "control"


def _load(raw_dir: Path):
    runs = []
    for f in sorted(raw_dir.glob("*.json")):
        if f.name == "meta.json":
            continue
        runs.append(json.loads(f.read_text()))
    meta = {}
    mp = raw_dir / "meta.json"
    if mp.is_file():
        meta = json.loads(mp.read_text())
    return runs, meta


def _mean_std(values: list[float]) -> tuple[float, float]:
    vals = [v for v in values if v is not None]
    if not vals:
        return 0.0, 0.0
    if len(vals) == 1:
        return float(vals[0]), 0.0
    return statistics.mean(vals), statistics.pstdev(vals)


def _cell_stats(runs: list[dict]) -> dict:
    """Group runs by (task, condition) -> aggregated metric dict."""
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for r in runs:
        grouped[(r["task"], r["condition"])].append(r)

    out: dict[tuple, dict] = {}
    for key, rs in grouped.items():
        agg: dict = {"n": len(rs)}
        for m in NUMERIC:
            agg[m] = _mean_std([r["metrics"].get(m) for r in rs])
        # correctness rate
        corrects = [r["metrics"].get("correct") for r in rs]
        checked = [c for c in corrects if c is not None]
        agg["correct_rate"] = (sum(1 for c in checked if c) / len(checked)) if checked else None
        # judge means
        jvals: dict[str, list[float]] = defaultdict(list)
        for r in rs:
            for k, v in (r.get("judge") or {}).items():
                if isinstance(v, (int, float)):
                    jvals[k].append(v)
        agg["judge"] = {k: _mean_std(v)[0] for k, v in jvals.items()}
        agg["errors"] = sum(1 for r in rs if r.get("run_error"))
        out[key] = agg
    return out


def _pct(treat: float, ctrl: float) -> str:
    if ctrl == 0:
        return "—"
    delta = (treat - ctrl) / ctrl * 100
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta:.0f}%"


def _behavioral_section(cells: dict) -> str:
    tasks = sorted({k[0] for k in cells})
    conditions = sorted({k[1] for k in cells})
    treatments = [c for c in conditions if c != CONTROL]

    lines = ["## Behavioral results (the real benchmark)\n"]
    lines.append(
        "Each cell is the mean over repetitions. Δ columns are the treatment relative "
        "to `control` (negative = Imperator used fewer / did less, which is the goal for "
        "tokens, edits, reads, and preamble).\n"
    )

    for task in tasks:
        lines.append(f"### `{task}`\n")
        header = ["Metric", CONTROL]
        for t in treatments:
            header += [t, f"Δ {t}"]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("|" + "---|" * len(header))

        ctrl = cells.get((task, CONTROL))
        for metric, (label, _lower) in NUMERIC.items():
            row = [label]
            cmean = ctrl[metric][0] if ctrl else 0.0
            row.append(_fmt(cmean, metric))
            for t in treatments:
                cell = cells.get((task, t))
                tmean = cell[metric][0] if cell else 0.0
                row.append(_fmt(tmean, metric))
                row.append(_pct(tmean, cmean) if ctrl else "—")
            lines.append("| " + " | ".join(row) + " |")

        # correctness + judge
        cr = ["Correct rate"]
        cr.append(_fmt_rate(ctrl["correct_rate"]) if ctrl else "—")
        for t in treatments:
            cell = cells.get((task, t))
            cr.append(_fmt_rate(cell["correct_rate"]) if cell else "—")
            cr.append("—")
        lines.append("| " + " | ".join(cr) + " |")
        lines.append("")

        # judge sub-table
        jkeys = sorted({k for (tk, _c), v in cells.items() if tk == task
                        for k in v.get("judge", {})})
        if jkeys:
            lines.append("Judge scores (1–5):\n")
            jheader = ["Dimension"] + conditions
            lines.append("| " + " | ".join(jheader) + " |")
            lines.append("|" + "---|" * len(jheader))
            for jk in jkeys:
                jrow = [jk]
                for c in conditions:
                    cell = cells.get((task, c))
                    val = cell["judge"].get(jk) if cell else None
                    jrow.append(f"{val:.1f}" if val is not None else "—")
                lines.append("| " + " | ".join(jrow) + " |")
            lines.append("")

    return "\n".join(lines)


def _fmt(v: float, metric: str) -> str:
    if metric == "cost_usd":
        return f"{v:.4f}"
    if v >= 1000:
        return f"{v:,.0f}"
    return f"{v:.0f}" if v == int(v) else f"{v:.1f}"


def _fmt_rate(r) -> str:
    return "—" if r is None else f"{r * 100:.0f}%"


def _static_section() -> str:
    """Regenerate the deterministic ruleset-size table (context cost per session)."""
    import tempfile

    rows = []
    cases = [
        ("minimal (global only)", []),
        ("fullstack-js", engine.resolve_profile("fullstack-js")),
        ("python-api", engine.resolve_profile("python-api")),
        ("all domains", list(engine.DOMAINS_AVAILABLE)),
    ]
    for label, domains in cases:
        groups = engine.filter_by_agent(
            engine.load_global() + engine.load_domains(domains), "claude-code"
        )
        n = sum(len(g.rules) for g in groups)
        for style in ("compact", "full"):
            with tempfile.TemporaryDirectory() as tmp:
                written = engine.compile_project(
                    domains, [], style=style, out_dir=tmp, agent="claude-code",
                )
                chars = sum(len(p.read_text(encoding="utf-8")) for p in written)
            rows.append(
                f"| `{label}` | {n} | {style} | {chars:,} | "
                f"~{engine.estimate_tokens('x' * chars):,} |"
            )
    body = [
        "## Static ruleset size (context cost per session)\n",
        "Total chars across the generated Claude Code `.claude/` files (global + "
        "path-scoped domains). Token figures use a ~4-chars/token heuristic.\n",
        "| Selection | Rules | Style | Chars | ≈ Tokens |",
        "|---|---|---|---|---|",
        *rows,
    ]
    return "\n".join(body)


def _provenance(meta: dict) -> str:
    if not meta:
        return ""
    return (
        "## Provenance\n\n"
        f"- Run: `{meta.get('timestamp', '?')}`\n"
        f"- Claude Code: `{meta.get('claude_version', '?')}`\n"
        f"- Agent model: `{meta.get('agent_model', '?')}`\n"
        f"- Judge model: `{meta.get('judge_model', '?')}`\n"
        f"- Reps per cell: {meta.get('reps', '?')}\n"
        f"- Rules content hash: `{meta.get('rules_hash', '?')}`\n"
    )


def render_report(raw_dir: Path) -> str:
    runs, meta = _load(raw_dir)
    cells = _cell_stats(runs)
    parts = [
        "# Benchmarks\n",
        "See [methodology.md](../methodology.md) for how these numbers are produced.\n",
        _behavioral_section(cells) if cells else
        "_No behavioral runs found in this directory._\n",
        _static_section(),
        _provenance(meta),
        "## Reproduce\n\n```bash\n"
        "pip install -r benchmarks/requirements.txt\n"
        "python benchmarks/harness/run.py --all --reps 3\n"
        f"python benchmarks/harness/aggregate.py {raw_dir}\n```\n",
    ]
    return "\n\n".join(p for p in parts if p)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: aggregate.py <results/raw/timestamp dir>", file=sys.stderr)
        return 2
    raw_dir = Path(argv[0]).resolve()
    if not raw_dir.is_dir():
        print(f"Not a directory: {raw_dir}", file=sys.stderr)
        return 2

    report = render_report(raw_dir)
    config.REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"✅ Wrote {config.REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
