# Benchmarks


See [methodology.md](../methodology.md) for how these numbers are produced.


## Behavioral results (the real benchmark)

Each cell is the mean over repetitions. Δ columns are the treatment relative to `control` (negative = Imperator used fewer / did less, which is the goal for tokens, edits, reads, and preamble).

### `add-feature-scoped`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 61,280 | 98,583 | +61% |
| Output tokens | 389 | 611.7 | +57% |
| Tool calls | 2 | 3 | +50% |
| Bytes read | 226 | 226 | +0% |
| Files changed | 1 | 2 | +100% |
| Lines + | 7 | 7 | +0% |
| Lines − | 0 | 0 | — |
| Preamble chars | 69 | 68 | -1% |
| Turns | 3 | 4 | +33% |
| Latency ms | 13,780 | 25,822 | +87% |
| Cost $ | 0.0873 | 0.1259 | +44% |
| Correct rate | 100% | 100% | — |

### `ambiguous-request`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 89,590 | 55,665 | -38% |
| Output tokens | 941.3 | 417.7 | -56% |
| Tool calls | 4.3 | 1.3 | -69% |
| Bytes read | 147 | 62.7 | -57% |
| Files changed | 1 | 0 | -100% |
| Lines + | 5 | 0 | -100% |
| Lines − | 0 | 0 | — |
| Preamble chars | 68.3 | 316 | +362% |
| Turns | 5.3 | 2.3 | -56% |
| Latency ms | 25,677 | 16,475 | -36% |
| Cost $ | 0.1175 | 0.1037 | -12% |
| Correct rate | — | — | — |

### `answer-question`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 69,680 | 79,499 | +14% |
| Output tokens | 409.3 | 369.7 | -10% |
| Tool calls | 2.7 | 2.3 | -12% |
| Bytes read | 291.7 | 230 | -21% |
| Files changed | 0 | 0 | — |
| Lines + | 0 | 0 | — |
| Lines − | 0 | 0 | — |
| Preamble chars | 160 | 152.7 | -5% |
| Turns | 3.7 | 3.3 | -9% |
| Latency ms | 20,284 | 18,806 | -7% |
| Cost $ | 0.0936 | 0.1149 | +23% |
| Correct rate | — | — | — |

### `bug-fix-targeted`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 83,451 | 106,960 | +28% |
| Output tokens | 596.3 | 628 | +5% |
| Tool calls | 3 | 3.3 | +11% |
| Bytes read | 307 | 307 | +0% |
| Files changed | 2 | 2 | +0% |
| Lines + | 1.3 | 1.7 | +25% |
| Lines − | 1.3 | 1.7 | +25% |
| Preamble chars | 41 | 62.3 | +52% |
| Turns | 4 | 4.3 | +8% |
| Latency ms | 24,448 | 22,942 | -6% |
| Cost $ | 0.0981 | 0.1290 | +32% |
| Correct rate | 100% | 100% | — |

### `refactor-no-rewrite`

| Metric | control | imperator-compact | Δ imperator-compact |
|---|---|---|---|
| Total tokens | 61,374 | 123,429 | +101% |
| Output tokens | 425.7 | 761.3 | +79% |
| Tool calls | 2 | 4 | +100% |
| Bytes read | 291 | 291 | +0% |
| Files changed | 1 | 2 | +100% |
| Lines + | 7.3 | 9 | +23% |
| Lines − | 8 | 9 | +12% |
| Preamble chars | 27 | 113.7 | +321% |
| Turns | 3 | 5 | +67% |
| Latency ms | 13,485 | 29,076 | +116% |
| Cost $ | 0.0881 | 0.1364 | +55% |
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
| `minimal (global only)` | 33 | standard | 10,811 | ~2,703 |
| `minimal (global only)` | 33 | compact | 10,299 | ~2,575 |
| `minimal (global only)` | 33 | strict | 4,333 | ~1,083 |
| `fullstack-js` | 72 | standard | 22,841 | ~5,710 |
| `fullstack-js` | 72 | compact | 21,806 | ~5,452 |
| `fullstack-js` | 72 | strict | 9,316 | ~2,329 |
| `python-api` | 75 | standard | 23,663 | ~5,916 |
| `python-api` | 75 | compact | 22,579 | ~5,645 |
| `python-api` | 75 | strict | 9,582 | ~2,396 |
| `all domains` | 113 | standard | 35,392 | ~8,848 |
| `all domains` | 113 | compact | 33,852 | ~8,463 |
| `all domains` | 113 | strict | 14,574 | ~3,644 |

## Provenance

- Run: `20260624T195416Z`
- Claude Code: `2.1.190 (Claude Code)`
- Agent model: `claude-sonnet-4-6`
- Judge: not run (`--no-judge`)
- Reps per cell: 3
- Rules content hash: `3535fa277046`


## Reproduce

```bash
pip install -e cli
python benchmarks/harness/run.py --all --conditions control,imperator-compact --reps 3 --no-judge
python benchmarks/harness/aggregate.py benchmarks/results/raw/20260624T195416Z
```

Agent runs use your Claude Code subscription auth — no `ANTHROPIC_API_KEY` required. A key is only needed if you drop `--no-judge` to add LLM-as-judge quality scores. See [README.md](README.md) for the dry-run and smoke-run forms.