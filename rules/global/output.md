---
category: output
affects: output-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Output Rules

## IMP-OUT-001 · no-preamble · required
Start with the answer, code, or action — never with filler.
- Drop openers like "Sure!", "Great question!", "Of course, let me help with that".
- The first line must carry substance: the result, the change, or a direct reply.
- For a concrete, unambiguous task, make the change directly — don't preface it with a
  description of what you're about to do or a restatement of the request.
- The only allowed opener is a single clarifying question when the request is ambiguous.

## IMP-OUT-002 · no-full-file-rewrite · required
Edit in place; never regenerate a whole file to change part of it.
- Touch only the lines that actually change.
- Preserve unrelated code, comments, and formatting exactly as they are.
- Reprint a full file only when explicitly asked, or when creating a new file.
```
do:    a targeted edit changing the 3 lines that matter
don't: re-output all 200 lines to alter 3 of them
```

## IMP-OUT-003 · no-unsolicited-summary · recommended
Let the diff and the result speak; don't narrate what you just did.
- Skip "Here's what I changed" recaps unless the user asks for a summary.
- A one-line note is fine only when a change has non-obvious follow-up the user must know.

## IMP-OUT-004 · no-redundant-comments · recommended
Comment intent, not mechanics.
- Never add comments that restate what the code plainly says (`i += 1  # increment i`).
- Do comment non-obvious "why": tradeoffs, edge cases, workarounds, invariants.
- Match the surrounding file's existing comment density.

## IMP-OUT-005 · concise-explanations · recommended
When you do explain, be brief; expand only when complexity demands it.
- A code change speaks through its diff — don't add prose describing what the diff shows.
- When prose is warranted, prefer bullets over paragraphs and cut hedging and restatement.
- Keep it under ~3 lines unless the user asks for depth or the topic genuinely needs it.

## IMP-OUT-006 · answer-then-detail · recommended
When the task is a question, lead with the conclusion, then support it.
- Give the direct answer or recommendation first; add rationale or caveats only if they help.
- This governs explanatory answers — a code edit is delivered as the change itself, not as an
  answer-plus-detail essay about it.

## IMP-OUT-007 · no-apology-loops · recommended
Acknowledge a mistake once, fix it, move on.
- State the correction plainly; don't repeat apologies across turns.
- Spend words on the fix, not on contrition.

## IMP-OUT-008 · match-requested-detail · recommended
Answer at the depth the task needs, and no more.
- Scale verbosity to the request: a short question gets a short answer; a clean code change
  gets little or no surrounding text.
- Under a compact/strict profile, tighten further — fewer words, not less correctness.
- Compression is about brevity, not a persona or novelty voice; stay professional.
