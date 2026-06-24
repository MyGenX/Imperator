---
name: imperator-rules
description: Show and summarize the Imperator rules currently active in this project. Use when asked what rules are in effect or which conventions apply.
---

# Imperator — Rules

Report the Imperator rules active for this project. Be factual; don't invent rules.

## How to gather
- Read `.imperator.json` for the configured agent, domains, roles, and compression profile.
- Read the generated rule files for this agent (e.g. `.claude/rules/`, `.cursor/rules/`,
  `.codex/rules/`, or `.gemini/rules/`) to list the actual rules in effect.

## What to report
- The always-on **global** rules (IDs + one-line directive each).
- The **domain** rules that apply, and the file globs that scope them.
- Any **role** subagents/skills available and what each is for.
- The active **compression profile** (standard / compact / strict).

Group by tier (global, domains, roles). Keep each rule to its directive line unless asked
to expand.
