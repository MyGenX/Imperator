---
role: my-role               # must match the filename (rules/roles/my-role.md)
description: >-
  One or two sentences describing WHEN an agent should delegate to this role.
  This is what the agent reads to decide routing — be concrete about the work.
tools: Read, Edit, Write, Bash, Grep, Glob   # Claude Code tool allowlist ("" = inherit all)
model: sonnet               # sonnet | opus | haiku | inherit
domains: [python, postgres] # domains this role knows (must all exist in catalog)
---
# My Role

<!--
TEMPLATE: a new specialist role → subagent. Save as rules/roles/<role>.md.
Steps:
  1. Pick a role id (kebab-case); use it for the filename and `role:`.
  2. Register it in cli/imperator/catalog.py → ROLES_AVAILABLE.
  3. Every domain in `domains:` must already exist under rules/domains/.
  4. Run: imperator validate --write-registry
At compile time the subagent embeds this persona + the global rules + the
intersection of `domains` with the project's selected domains.
-->

You are a senior <specialty>. State the persona's responsibilities, what it owns,
and its standards. Follow the Imperator global rules at all times, plus the active
domain rules for this project's stack.

- Concrete behavior or standard 1.
- Concrete behavior or standard 2.
