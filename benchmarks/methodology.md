# Benchmark methodology

Imperator's value is **behavioral**: rules like `no-preamble`, `no-full-codebase-scan`,
`no-full-file-rewrite`, and `clarify-before-build` change how an agent spends tokens and
what it edits across a real session. File size alone cannot capture that — so this
harness runs a real agent on real tasks and measures what actually happened.

## The experiment

For every **task** we run the agent under two or more **conditions** and repeat each cell
N times (agents are stochastic):

| Condition | What's different |
|---|---|
| `control` | Vanilla Claude Code — **no** `CLAUDE.md` in the project. |
| `imperator-compact` | A compiled Imperator `CLAUDE.md` (compact style) is present. |
| `imperator-full` | Same rules, full per-rule frontmatter style (optional). |

Claude Code auto-loads `CLAUDE.md` from the project root, so the *only* thing that differs
between arms is the presence/style of the ruleset. Same prompt, same fixture, same model.

Each run happens in a **fresh throwaway git clone of the task fixture**, so edits are
isolated and a post-run `git diff` is meaningful. The compiled `CLAUDE.md` is committed to
the baseline before the agent starts, so it never pollutes the measured diff.

## What we measure

**Deterministic** (parsed from the `stream-json` transcript, git diff, and verifier):

- **Tokens** — input / output / cache-read / cache-creation / total, taken from the real
  `result` usage event (exact, not the chars/4 heuristic).
- **Tool calls & bytes read** — how much the agent read (proxy for `no-full-codebase-scan`).
- **Edit footprint** — files changed + lines added/deleted (proxy for scope creep and
  `no-full-file-rewrite`).
- **Preamble** — characters before the first code fence in the first reply (`no-preamble`).
- **Correctness** — each task ships a `verify.sh`; exit 0 = solved.
- **Latency & turns** — wall time / `num_turns` to completion.

**LLM-as-judge** (Anthropic API, blind to condition): scores the transcript 1–5 on
conciseness, scope adherence, investigation discipline, clarify-when-ambiguous, and
overall quality. The judge never learns which arm produced a transcript.

## Reading the results

`results.md` reports the mean per cell and a **Δ vs. control** column. For tokens, edits,
reads, and preamble, **negative Δ is the win** (Imperator did less). For correctness and
judge scores, higher is better. Variance across reps is summarized; one run proves nothing.

## Caveats

- Claude Code's sampling temperature isn't user-settable — we mitigate with repetitions
  and report variance, not single runs.
- Token counts depend on the pinned model and Claude Code version (recorded in Provenance).
- LLM-as-judge is directional, not ground truth; pair it with the deterministic metrics.
- Real runs cost money and need `ANTHROPIC_API_KEY`, so they are **not** in default CI.
  `run.py --dry-run` validates the whole suite without spending anything.

## Running it

```bash
pip install -r benchmarks/requirements.txt
export ANTHROPIC_API_KEY=sk-...

# validate configs only (no calls, CI-safe)
python benchmarks/harness/run.py --dry-run

# one task, one rep, two arms (cheap smoke run)
python benchmarks/harness/run.py --task bug-fix-targeted \
    --conditions control,imperator-compact --reps 1

# full suite
python benchmarks/harness/run.py --all --reps 3
python benchmarks/harness/aggregate.py benchmarks/results/raw/<timestamp>
```
