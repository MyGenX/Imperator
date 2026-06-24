---
name: imperator-plan
description: Produce a small, scoped implementation plan that honors Imperator rules before writing code. Use when asked to plan a change, a feature, or a fix.
---

# Imperator — Plan

Produce a concise implementation plan for the requested change. Do not write code yet.

## Steps
1. Restate the goal in one sentence. If the request is ambiguous, ask one clarifying
   question before planning further.
2. List the specific files/functions you expect to touch — keep it minimal and in scope.
3. Outline the change as a short ordered list of steps (smallest correct change first).
4. Call out risks: breaking changes to public APIs/schemas/shared interfaces, data
   migrations, and anything needing confirmation.
5. State how the change will be verified (which tests/build/command).

## Constraints
- Stay strictly within the requested scope — no unrelated refactors or "improvements".
- Prefer existing patterns and utilities over new abstractions.
- Keep the plan short and actionable; this is a plan, not an essay.
