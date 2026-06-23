---
category: processing
affects: thinking-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Processing Rules

## IMP-PRO-001 · clarify-before-build · required
Ask clarifying questions BEFORE generating large amounts of code. Never assume ambiguous
requirements.

## IMP-PRO-002 · no-scope-creep · required
Stay strictly within the task scope. Do not refactor, rename, or "improve" code outside
the requested change.

## IMP-PRO-003 · small-steps · recommended
Break large tasks into small, confirmable steps. Complete and confirm each step before
proceeding.

## IMP-PRO-004 · flag-breaking-changes · required
Always warn about potential breaking changes BEFORE making them.

## IMP-PRO-005 · prefer-existing-patterns · required
Match the conventions, naming, and structure already present in the codebase rather than
introducing new ones.

## IMP-PRO-006 · no-speculative-abstraction · recommended
Do not add abstractions, config options, or generality that the current task does not
require.
