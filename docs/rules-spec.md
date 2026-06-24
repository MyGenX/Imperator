# Imperator Rules Specification

Imperator organizes rules into three tiers, authored once under `rules/` and compiled
into each agent's native layout.

| Tier | Source | Compiles to (Claude Code) | Loads |
|---|---|---|---|
| **Global** | `rules/global/*.md` | `.claude/rules/global.md` | every session |
| **Domain** (tech stack) | `rules/domains/*.md` | `.claude/rules/<domain>.md` | only when editing matching files (path-scoped) |
| **Role** (persona) | `rules/roles/*.md` | `.claude/agents/<role>.md` (subagent) | delegated by task |

## Global & domain rule files (compact, single source of truth)

```markdown
---
category: output            # global tier
affects: output-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Output Rules

## IMP-OUT-001 · no-preamble · required
Never open with filler phrases. Start with the answer.
```

A **domain** file adds `domain` and `paths` (the path globs that scope it):

```markdown
---
category: domain
domain: python
affects: all-tokens
paths: ["**/*.py"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — Python

## IMP-PY-001 · type-hints · required
Add type hints to function signatures and public APIs.
```

### File frontmatter

| Key | Meaning |
|---|---|
| `category` | `output` / `investigation` / `processing` / `behavior` / `safety` (global), or `domain` |
| `affects` | Token impact (`output-tokens`, `all-tokens`, `risk-reduction`, ...) |
| `agents` | Default agents these rules target (a list) |
| `domain` | (domain files) the domain id, e.g. `python` |
| `paths` | (domain files) glob list; compiled to Claude Code path-scoped `paths:` frontmatter |

### Overview preamble (optional)

Any text between the file's H1 and its first `## IMP-…` rule is captured as the group's
**overview** and rendered above the rules. Use it on domain files for a short "golden path"
— the recommended conventions and layout for that stack — so the rules have framing
context. Global files normally omit it.

```markdown
# Imperator Domain — Next.js (App Router)

**Golden path:** App Router; Server Components by default; Server Actions for mutations;
`loading.tsx`/`error.tsx` per route. Go client-side only for interactivity or browser APIs.

## IMP-NXT-001 · app-router-only · required
...
```

### Rule heading

```
## <ID> · <name> · <severity>
```

- **ID** — `IMP-<CAT>-<NNN>`, e.g. `IMP-OUT-001`. Unique across the project.
- **name** — kebab-case, short.  **severity** — `required` | `recommended` | `optional`.
- The separator is the middle dot `·` (U+00B7). The rule **body** runs to the next `##`.

### Rule body format

Each rule body is a short, structured prompt — not a paragraph. Keep it lean:

```markdown
## IMP-OUT-002 · no-full-file-rewrite · required
Edit in place; never regenerate a whole file to change part of it.
- Touch only the lines that actually change.
- Preserve unrelated code, comments, and formatting exactly.
- Reprint a full file only when explicitly asked, or when creating a new file.
```

- **Line 1 — directive:** one imperative sentence stating the rule, concrete enough to verify.
- **Bullets:** 2–4 short, testable specifics — boundaries and exceptions (when it does /
  doesn't apply). No rationale paragraphs.
- **Examples (sparingly):** for a few high-impact rules where the directive is easy to
  misread, append a compact do/don't block. Reserve these — they cost always-on context:

  ```markdown
  ```
  do:    raise specific exceptions (except ValueError: ...)
  don't: bare `except:` that swallows everything
  ```
  ```

Because only lines matching `## IMP-<CAT>-NNN · … · …` start a new rule, bodies may freely
contain bullets, blank lines, and fenced code blocks. The same body format applies to
**domain** rules.

## Role files (→ subagents)

Each `rules/roles/<role>.md` defines a specialist persona that compiles to a Claude Code
subagent. Frontmatter configures the subagent; the body is its system prompt.

```markdown
---
role: backend-developer
description: Implements and reviews server-side code, APIs, data access, migrations.
tools: Read, Edit, Write, Bash, Grep, Glob
model: sonnet
domains: [python, fastapi, postgres, api-rest]
---
# Backend Developer

You are a senior backend developer. Follow the Imperator global rules ...
```

| Key | Meaning |
|---|---|
| `role` | subagent `name` (lowercase-hyphen) |
| `description` | when Claude should delegate to this role |
| `tools` | comma-separated tool allowlist (omit to inherit all) |
| `model` | `sonnet` / `opus` / `haiku` / `inherit` / full id |
| `domains` | domains this role cares about |

At compile time a role subagent embeds the persona + the global rules + the
**intersection of its `domains` and the project's selected domains** (`role.domains ∩
selected`), so the subagent is self-contained.

## Output styles

`compact` (default) renders `## IMP-OUT-001 · no-preamble · required`; `full` renders
per-rule YAML frontmatter. Choose with `--style` (stored in `.imperator.json`).

## Layouts

- `modular` (default for **claude-code**) — the `.claude/` tree above.
- `flat` — a single file (`CLAUDE.md` / `.cursorrules` / `AGENTS.md` / `GEMINI.md`),
  global + domains only (no subagents). Used for Cursor/Codex/Gemini and available for
  Claude Code via `imperator compile --layout flat`.

## Compilation pipeline

1. **Discover** the repo (`$IMPERATOR_DIR` → `~/.imperator` → checkout root).
2. **Load** global (fixed order) + selected domains + selected roles.
3. **Parse** into `RuleGroup`/`Rule` and `Role` objects.
4. **Filter** rules that don't target the chosen agent.
5. **Render** global, each domain (with `paths`), and each role subagent.
6. **Write** the `.claude/` tree (modular) or a single file (flat).
