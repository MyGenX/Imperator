# Imperator benchmarks

Reproducible, deterministic evidence for what Imperator's rules actually change when a real
agent does real work — not estimates. The harness drives **Claude Code headless**
(`claude -p … --output-format stream-json`) across a matrix of `(task × condition × rep)`,
reads metrics straight from the transcript and the post-run `git diff`, and aggregates them
into [`results.md`](results.md).

It uses your Claude Code subscription auth — **no `ANTHROPIC_API_KEY` is needed** for the
agent runs. A key is only required for the optional LLM-as-judge step; `--no-judge` skips it
and produces a complete deterministic report without one.

## Layout

```
benchmarks/
  harness/        run.py (orchestrator) · runner.py · metrics.py · judge.py · aggregate.py
  tasks/<id>/     task.yaml · fixture/ (starting repo) · verify.sh (correctness gate)
  results/
    raw/<ts>/     per-run JSON + meta.json (the artifacts)
    results.md    aggregated report (generated)
  methodology.md  how a cell is run and scored
```

## Three commands

**1. Dry run — validate wiring, make no agent/API calls (free, instant):**

```bash
python benchmarks/harness/run.py --all --dry-run
```

**2. Cheap smoke run — one task, both arms, 1 rep (a handful of agent calls):**

```bash
python benchmarks/harness/run.py --task bug-fix-targeted \
    --conditions control,imperator-compact --reps 1 --no-judge
python benchmarks/harness/aggregate.py benchmarks/results/raw/<timestamp>
```

**3. Full benchmark — all tasks, control vs. Imperator, 3 reps (deterministic, no key):**

```bash
python benchmarks/harness/run.py --all \
    --conditions control,imperator-compact --reps 3 --no-judge
python benchmarks/harness/aggregate.py benchmarks/results/raw/<timestamp>
```

Add `imperator-full` to `--conditions` for a third arm, or drop `--no-judge` (and set
`ANTHROPIC_API_KEY`) to add blind LLM-as-judge quality scores.

**Cost-regression gate (optional, after a full run):** check the fresh deltas against the
ceilings in [`budgets.yaml`](budgets.yaml) so a rule change can't silently re-inflate query
cost. Exits non-zero on a breach.

```bash
python benchmarks/harness/budget.py benchmarks/results/raw/<timestamp>
```

Like the suite, this needs real runs, so it is **not** in default CI — `--dry-run` stays the
CI-safe check.

## Conditions

| Condition | What the fixture gets |
|---|---|
| `control` | Vanilla agent — no `.claude/` rules present. |
| `imperator-compact` | Compiled Imperator ruleset (global + path-scoped domains), compact style. |
| `imperator-full` | Same ruleset, standard (full-richness) style. |

## What is and isn't measured

**Measured deterministically** (per `(task, condition)`, averaged over reps): total/output
tokens, tool calls, bytes read, files changed, lines added/deleted, preamble length, turns,
latency, cost, and task **correctness** via each task's `verify.sh`.

**Not measured:** subjective answer quality unless the judge is enabled; behavior on large
real-world repos (fixtures are deliberately small and checkable); cross-model generality
(one pinned agent model per run); cost/latency under load. See the "What this does and does
not measure" section in [results.md](results.md) and [methodology.md](methodology.md).

Imperator's value is **behavioral and workload-dependent**. The static ruleset size is a
fixed per-session context cost (reported in `results.md`); the savings accrue across a whole
session and vary by task. Treat the deltas as directional evidence, not a guarantee.

## Adding a task

Create `tasks/<id>/` with:

- `task.yaml` — `prompt`, optional `extensions` (domains to compile for rule conditions),
  optional `reps`.
- `fixture/` — the starting repository state the agent works in.
- `verify.sh` — exits `0` when the task was done correctly (the correctness gate).

`python benchmarks/harness/run.py --dry-run` validates new tasks without running them.
