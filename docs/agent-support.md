# Agent Support

Imperator compiles one ruleset into native project files for each supported agent.
The compiler currently supports Claude Code, Cursor, Codex, and Gemini.

## Claude Code

Status: supported.

Generated layout:

```text
.claude/
  CLAUDE.md
  rules/
    global.md
    python.md
  agents/
    backend-developer.md
```

Global rules are always-on. Domain rules use Claude Code path metadata when the
domain declares file globs. Role files compile to Claude Code subagents.

## Cursor

Status: supported.

Generated layout:

```text
.cursor/
  rules/
    global.mdc
    domains/
      python.mdc
    roles/
      backend-developer.mdc
```

Global rules compile with `alwaysApply: true`. Domain rules compile with `globs`
metadata. Role rules are description-gated Cursor project rules.

## Codex

Status: supported.

Generated layout:

```text
AGENTS.md
.codex/
  rules/
    global.md
    domains/
      python.md
    roles/
      backend-developer.md
  agents/
    backend-developer.toml
```

Codex discovers root `AGENTS.md` project instructions. Because Codex does not
auto-load arbitrary `.codex/rules/*.md` files as instruction modules, active
global and domain rules are embedded in `AGENTS.md`; generated `.codex/rules/`
files remain reviewable artifacts. Roles compile to project-scoped Codex custom
agents.

## Gemini

Status: supported.

Generated layout:

```text
GEMINI.md
.gemini/
  rules/
    global.md
    domains/
      python.md
    roles/
      backend-developer.md
  commands/
    roles/
      backend-developer.toml
```

`GEMINI.md` imports generated rule modules with `@` references. Roles compile to
role instruction files plus slash-command TOML files.

## Windsurf

Status: planned.

No output files are generated yet. Support should be added only after mapping
Imperator's global, domain, and role tiers to Windsurf's current project-rule
format.

## Cline

Status: planned.

No output files are generated yet. Support should preserve Imperator's committed
project-rule model rather than promising runtime behavior the compiler does not
emit.

## OpenCode

Status: planned.

No output files are generated yet. Support should be based on OpenCode's native
instruction and agent configuration surfaces.

## Copilot

Status: planned.

No output files are generated yet. Support should distinguish repository
instructions from editor or account-level configuration.
