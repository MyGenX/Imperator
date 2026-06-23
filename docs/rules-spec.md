# Imperator Rules Specification

## Source format (canonical, compact)

Every file in `core/` and `extensions/` is authored in the same compact form. This is
the **single source of truth** — the compiler renders it into agent files in either
style.

```markdown
---
category: output            # extensions also add: extends: core
affects: output-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Output Rules

## IMP-OUT-001 · no-preamble · required
Never open with filler phrases. Start with the answer.

## IMP-OUT-002 · no-full-file-rewrite · required
Never rewrite an entire file when only part changes.
```

### File frontmatter

| Key | Meaning |
|---|---|
| `category` | Rule category (`output`, `investigation`, `processing`, `behavior`, `safety`, `extension`) |
| `affects` | Token impact (`output-tokens`, `processing-tokens`, `thinking-tokens`, `all-tokens`, `risk-reduction`) |
| `agents` | Default agents these rules target (a list) |
| `extends` | (extensions only) the base layer, usually `core` |

### Rule heading

```
## <ID> · <name> · <severity>
```

- **ID** — `IMP-<CAT>-<NNN>`, e.g. `IMP-OUT-001`. Unique across the project.
- **name** — kebab-case, short.
- **severity** — `required` | `recommended` | `optional`.
- The separator is the middle dot `·` (U+00B7).

The rule **body** is everything up to the next `##` heading.

## Output styles

The compiler can render each rule two ways. Choose with `--style` (stored in
`.imperator.json`).

### `compact` (default)

```markdown
## IMP-OUT-001 · no-preamble · required
Never open with filler phrases. Start with the answer.
```

Lean and human-readable — ideal for the agent file you actually ship.

### `full`

```markdown
---
id: IMP-OUT-001
name: no-preamble
category: output
affects: output-tokens
severity: required
agents: [claude-code, cursor, codex, gemini]
---

### no-preamble

Never open with filler phrases. Start with the answer.
```

Verbose and machine-readable — useful for tooling that wants per-rule metadata.

## Compilation pipeline

1. **Discover** the repo (`$IMPERATOR_DIR` → `~/.imperator` → checkout root).
2. **Load** core files (fixed order) + selected extensions (selection order).
3. **Parse** each file into `RuleGroup` → `Rule` objects.
4. **Filter** out rules that don't target the chosen agent.
5. **Render** via the agent's Jinja template in the chosen style.
6. **Write** the agent file (`CLAUDE.md`, `.cursorrules`, `AGENTS.md`, `GEMINI.md`).
