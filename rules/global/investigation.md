---
category: investigation
affects: processing-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Investigation Rules

## IMP-INV-001 · no-full-codebase-scan · required
Read only what the task needs; don't sweep the whole repo.
- Open files directly relevant to the change, not entire directories "for context".
- Use search to locate the few files that matter, then read those.
- Broad exploration is acceptable only when the user explicitly asks you to map the codebase.

## IMP-INV-002 · no-repeat-file-read · required
Don't re-read what you've already read.
- Reuse file contents already in context unless the file changed since you read it.
- Re-read only the specific section that changed, not the whole file again.

## IMP-INV-003 · ask-before-explore · recommended
When scope is unclear, ask instead of wandering.
- If you can't tell which files or area are in scope, ask before reading widely.
- A targeted question costs less than an open-ended exploration.

## IMP-INV-004 · targeted-search · required
Search by symbol, not by browsing.
- Grep for the function, class, route, or string you need.
- Prefer a precise query over reading directories top-to-bottom.
- Narrow with file globs/types when the codebase is large.

## IMP-INV-005 · stop-when-found · recommended
Stop investigating once you can act.
- When you have enough context to make the change correctly, start making it.
- Don't keep reading "to be safe" after the relevant code is identified.

## IMP-INV-006 · reuse-known-context · required
Build on what's already established this session.
- Reuse facts, file locations, and decisions already determined rather than re-deriving them.
- Don't re-investigate something the conversation already settled.
