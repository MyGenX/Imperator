# Contributing to Imperator 👑

Thanks for helping command AI agents better!

## Ways to contribute

- **Add a rule** to an existing core file or extension
- **Add an extension** for a new stack
- **Improve docs** or the CLI

## Adding a rule

Rules are authored once in **compact form** — see [docs/rules-spec.md](docs/rules-spec.md)
for the full spec. In short, add a heading to the relevant file:

```markdown
## IMP-OUT-008 · my-rule-name · recommended
One or two lines describing exactly what the agent should (not) do.
```

Requirements for every rule:

- **Unique ID** — `IMP-<CAT>-<NNN>` (e.g. `IMP-NXT-007`). Use the prefix already used in
  that file.
- **kebab-case name** — short and descriptive.
- **Severity** — `required`, `recommended`, or `optional`.
- **Imperative, testable wording** — say what to do, not background theory.

## Adding an extension

1. Create `extensions/<name>.md` with file frontmatter (`category: extension`,
   `affects`, `extends: core`, `agents`).
2. Add `<name>` to `EXTENSIONS_AVAILABLE` in `cli/imperator/engine.py`.
3. If it belongs in a profile, update `PROFILES` in the same file.
4. Regenerate examples: `python compiler/compile.py`.

## Before opening a PR

```bash
pip install -e cli
pytest cli/tests
python compiler/compile.py --check   # committed agents/ outputs must be current
```

If `--check` fails, run `python compiler/compile.py` and commit the regenerated files.

## Rule philosophy

> Every rule has a reason. Every token has a purpose.

A rule earns its place only if it changes agent behavior in a way that saves tokens,
prevents mistakes, or enforces a real best practice. No filler.
