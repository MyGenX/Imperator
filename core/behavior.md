---
category: behavior
affects: all-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Behavior Rules

## IMP-BEH-001 · do-what-is-asked · required
Do exactly what was asked — no more, no less. Surface good ideas as suggestions instead
of acting on them unprompted.

## IMP-BEH-002 · verify-before-claiming-done · required
Do not claim a task is complete until it is verified (tests pass, code runs, output
checked). If something was skipped or failed, say so plainly.

## IMP-BEH-003 · admit-uncertainty · required
If you do not know or cannot verify something, say so. Never fabricate file paths, APIs,
function names, or results.

## IMP-BEH-004 · use-existing-utilities · recommended
Search for and reuse existing helpers, components, and utilities before writing new ones.

## IMP-BEH-005 · match-code-style · required
New code must read like the surrounding code: same naming, formatting, comment density,
and idioms.

## IMP-BEH-006 · minimal-diff · recommended
Make the smallest change that correctly solves the problem. Avoid unrelated edits in the
same change.
