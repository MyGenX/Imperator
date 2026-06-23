# Benchmarks

## Methodology

Imperator's value is **behavioral**: rules like `no-preamble`, `no-full-file-rewrite`,
`no-full-codebase-scan`, and `clarify-before-build` change how an agent spends tokens
across an entire session. That saving is workload-dependent and not captured by file
size alone.

What we *can* measure deterministically is the size of the compiled ruleset itself —
the fixed context cost you pay per session. Token figures below use a ~4-chars/token
heuristic (`imperator stats`); they are estimates, not tokenizer-exact.

## Compiled ruleset size (agent: claude-code)

| Selection | Rules | Style | Chars | ≈ Tokens |
|---|---|---|---|---|
| `minimal` (core only) | 32 | compact | 5,110 | ~1,278 |
| `minimal` (core only) | 32 | full | 9,429 | ~2,357 |
| `fullstack-js` | 56 | compact | 8,389 | ~2,097 |
| `fullstack-js` | 56 | full | 15,833 | ~3,958 |
| all extensions | 81 | compact | 11,593 | ~2,898 |
| all extensions | 81 | full | 22,265 | ~5,566 |

Takeaways:

- **`compact` is ~45% smaller than `full`** for the same rules — prefer it for the file
  you actually ship; reserve `full` for tooling that needs per-rule metadata.
- Even the entire ruleset (81 rules) fits in **under ~3k tokens** of context in compact
  style — a one-time cost amortized across every turn.

## Reproduce

```bash
imperator stats
```

(numbers above were produced from this repo's rules; rerun after editing rules to refresh.)
