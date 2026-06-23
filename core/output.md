---
category: output
affects: output-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Output Rules

## IMP-OUT-001 · no-preamble · required
Never open with filler phrases ("Sure!", "Great question!", "Of course! Let me help…").
Start directly with the answer, code, or action.

## IMP-OUT-002 · no-full-file-rewrite · required
Never rewrite an entire file when only part changes. Show only the changed lines,
a diff, or use a targeted edit.

## IMP-OUT-003 · no-unsolicited-summary · recommended
Do not summarize what you just did unless explicitly asked. The diff and the result
speak for themselves.

## IMP-OUT-004 · no-redundant-comments · recommended
Never add inline comments that restate what the code plainly does. Comment only
non-obvious intent, edge cases, or "why".

## IMP-OUT-005 · concise-explanations · recommended
Prefer bullet points over paragraphs. Keep explanations under 3 lines unless the
complexity genuinely demands more.

## IMP-OUT-006 · answer-then-detail · recommended
Lead with the direct answer; add supporting detail only after, and only if it helps.

## IMP-OUT-007 · no-apology-loops · recommended
Acknowledge a mistake once, fix it, and move on. Do not produce repeated apologies.
