# Benchmarks


See [methodology.md](../methodology.md) for how these numbers are produced.


## Behavioral results (the real benchmark)

Each cell is the mean over repetitions. Δ columns are the treatment relative to `control` (negative = Imperator used fewer / did less, which is the goal for tokens, edits, reads, and preamble).

### `add-feature-scoped`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 68,855 | 129,324 | +88% |
| Output tokens | 404.3 | 705.7 | +75% |
| Tool calls | 2 | 3.7 | +83% |
| Bytes read | 226 | 226 | +0% |
| Files changed | 1 | 2 | +100% |
| Lines + | 7 | 7 | +0% |
| Lines − | 0 | 0 | — |
| Preamble chars | 139.3 | 69.3 | -50% |
| Turns | 3 | 4.7 | +56% |
| Latency ms | 17,307 | 31,452 | +82% |
| Cost $ | 0.1057 | 0.1541 | +46% |
| Correct rate | 100% | 100% | — |

### `ambiguous-request`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 100,069 | 61,626 | -38% |
| Output tokens | 952.7 | 440.3 | -54% |
| Tool calls | 4.3 | 1.7 | -62% |
| Bytes read | 129.3 | 80.3 | -38% |
| Files changed | 1 | 0 | -100% |
| Lines + | 5 | 0 | -100% |
| Lines − | 0 | 0 | — |
| Preamble chars | 78 | 155.7 | +100% |
| Turns | 5.3 | 2.7 | -50% |
| Latency ms | 28,580 | 15,754 | -45% |
| Cost $ | 0.1367 | 0.1211 | -11% |
| Correct rate | — | — | — |

### `answer-question`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 97,224 | 79,345 | -18% |
| Output tokens | 537 | 331.7 | -38% |
| Tool calls | 4 | 2 | -50% |
| Bytes read | 415 | 230 | -45% |
| Files changed | 0 | 0 | — |
| Lines + | 0 | 0 | — |
| Lines − | 0 | 0 | — |
| Preamble chars | 184 | 135 | -27% |
| Turns | 5 | 3 | -40% |
| Latency ms | 21,872 | 17,484 | -20% |
| Cost $ | 0.1281 | 0.1310 | +2% |
| Correct rate | — | — | — |

### `bug-fix-targeted`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 93,886 | 138,139 | +47% |
| Output tokens | 590.7 | 736 | +25% |
| Tool calls | 3 | 4 | +33% |
| Bytes read | 307 | 307 | +0% |
| Files changed | 2 | 2 | +0% |
| Lines + | 1 | 2 | +100% |
| Lines − | 1 | 2 | +100% |
| Preamble chars | 87 | 59.3 | -32% |
| Turns | 4 | 5 | +25% |
| Latency ms | 27,759 | 25,394 | -9% |
| Cost $ | 0.1170 | 0.1579 | +35% |
| Correct rate | 100% | 100% | — |

### `multi-file-refactor`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 122,359 | 221,119 | +81% |
| Output tokens | 1,393 | 1,538 | +10% |
| Tool calls | 7 | 7.7 | +10% |
| Bytes read | 701 | 701 | +0% |
| Files changed | 6 | 6 | +0% |
| Lines + | 8 | 8 | +0% |
| Lines − | 2 | 2 | +0% |
| Preamble chars | 60 | 140.3 | +134% |
| Turns | 8 | 8.7 | +8% |
| Latency ms | 37,320 | 52,290 | +40% |
| Cost $ | 0.1458 | 0.2018 | +38% |
| Correct rate | 100% | 100% | — |

### `refactor-no-rewrite`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 85,542 | 137,741 | +61% |
| Output tokens | 584 | 758.3 | +30% |
| Tool calls | 2.7 | 4 | +50% |
| Bytes read | 291 | 291 | +0% |
| Files changed | 1 | 2 | +100% |
| Lines + | 8 | 9 | +12% |
| Lines − | 8 | 9 | +12% |
| Preamble chars | 243.7 | 151.7 | -38% |
| Turns | 3.7 | 5 | +36% |
| Latency ms | 24,009 | 30,079 | +25% |
| Cost $ | 0.1145 | 0.1576 | +38% |
| Correct rate | 100% | 100% | — |


## What this does and does not measure

**Measured (deterministic, from the run transcript + git diff):** total/output tokens, tool calls, bytes read, files changed and lines added/deleted, response preamble length, turns, latency, cost, and task correctness (each task's `verify.sh`). These are read straight from the agent's `stream-json` usage and the post-run diff — no estimation.

**Not measured:**
- Subjective answer quality — LLM-as-judge was **not** run for this batch (`--no-judge`).
- Behavior on large real-world repositories. Fixtures are small and single-purpose, chosen so correctness is checkable; absolute numbers will differ on your codebase.
- Cross-model generality. Runs use a single pinned agent model (`claude-sonnet-4-6`); other models may respond to the rules differently.
- Latency/cost under load or across providers — wall-clock here is single-machine, serial, and network-dependent.

Imperator's value is **behavioral and workload-dependent**: the static ruleset is a fixed per-session context cost (below), while the savings show up across a whole session and vary by task. Read the deltas as directional evidence, not a guarantee.


## Static ruleset size (context cost per session)

Total chars across the generated Claude Code `.claude/` files (global + path-scoped domains). Token figures use a ~4-chars/token heuristic.

| Selection | Rules | Style | Chars | ≈ Tokens |
|---|---|---|---|---|
| `minimal (global only)` | 33 | standard | 11,629 | ~2,907 |
| `minimal (global only)` | 33 | compact | 11,117 | ~2,779 |
| `minimal (global only)` | 33 | strict | 4,372 | ~1,093 |
| `fullstack-js` | 72 | standard | 23,659 | ~5,915 |
| `fullstack-js` | 72 | compact | 22,624 | ~5,656 |
| `fullstack-js` | 72 | strict | 9,355 | ~2,339 |
| `python-api` | 75 | standard | 24,481 | ~6,120 |
| `python-api` | 75 | compact | 23,397 | ~5,849 |
| `python-api` | 75 | strict | 9,621 | ~2,405 |
| `all domains` | 113 | standard | 36,210 | ~9,052 |
| `all domains` | 113 | compact | 34,670 | ~8,668 |
| `all domains` | 113 | strict | 14,613 | ~3,653 |

## Provenance

- Run: `20260626T101200Z`
- Claude Code: `2.1.193 (Claude Code)`
- Agent model: `claude-sonnet-4-6`
- Judge: not run (`--no-judge`)
- Reps per cell: 3
- Rules content hash: `f640dbc61da6`


## Reproduce

```bash
pip install -e cli
python benchmarks/harness/run.py --all --conditions control,imperator-compact --reps 3 --no-judge
python benchmarks/harness/aggregate.py benchmarks/results/raw/20260626T101200Z
```

Agent runs use your Claude Code subscription auth — no `ANTHROPIC_API_KEY` required. A key is only needed if you drop `--no-judge` to add LLM-as-judge quality scores. See [README.md](README.md) for the dry-run and smoke-run forms.