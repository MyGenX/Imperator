---
name: imperator-stats
description: Report the active Imperator domains, rule count, and approximate context cost for this project. Use when asked about Imperator's footprint or token impact.
---

# Imperator — Stats

Report Imperator's footprint in this project.

## How to gather
- If the `imperator` CLI is available, run `imperator stats` and report its output.
- Otherwise, read `.imperator.json` and the generated rule files directly.

## What to report
- Configured agent and compression profile (standard / compact / strict).
- Active domains and the total number of rules in effect.
- Approximate context cost: characters and an estimate of ~chars/4 tokens for the
  always-on rules, noting that domain rules are path-scoped (load only on matching files)
  and role rules live in their own subagent/skill context.

Keep it to a short, factual summary — no speculation about runtime token usage.
