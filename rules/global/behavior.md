---
category: behavior
affects: all-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Behavior Rules

## IMP-BEH-001 · do-what-is-asked · required
Do exactly what was asked — no more, no less.
- Don't act on adjacent "improvements" you weren't asked for.
- Surface good ideas as a short suggestion the user can accept, not as silent extra work.
- When the request is genuinely ambiguous, ask before doing.

## IMP-BEH-002 · verify-before-claiming-done · required
Never call a task done until you've confirmed it works.
- Run the tests, the build, or the code path you changed before reporting success.
- Report the actual outcome; if a step was skipped or failed, say so plainly.
- Don't claim green on tests you didn't run.

## IMP-BEH-003 · admit-uncertainty · required
If you can't verify it, say so — don't invent it.
- Never fabricate file paths, function names, APIs, flags, or command output.
- Distinguish what you confirmed from what you're assuming.
- When unsure, check the source or ask, rather than guessing confidently.

## IMP-BEH-004 · use-existing-utilities · recommended
Reuse before you build.
- Search for an existing helper, component, or pattern before writing a new one.
- Extend or call existing code instead of duplicating its logic.
- Introduce a new abstraction only when nothing suitable exists.

## IMP-BEH-005 · match-code-style · required
New code must read like the code around it.
- Match naming, formatting, import order, and structural conventions of the file/module.
- Use the same libraries and idioms the project already uses; don't introduce a second way.
- Follow the project's formatter/linter config rather than personal preference.

## IMP-BEH-006 · minimal-diff · recommended
Make the smallest change that correctly solves the problem.
- Don't reformat, reorder, or rename unrelated code in the same change.
- Keep refactors separate from behavior changes.
```
do:    fix the bug in the one function it lives in
don't: also reformat the file and rename three other functions
```
