---
category: investigation
affects: processing-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Investigation Rules

## IMP-INV-001 · no-full-codebase-scan · required
Never scan the entire codebase unless explicitly instructed. Read only files directly
relevant to the current task.

## IMP-INV-002 · no-repeat-file-read · required
Never read the same file twice in one session unless it has changed since the last read.

## IMP-INV-003 · ask-before-explore · recommended
If task scope is unclear, ask which files or areas are relevant before exploring
independently.

## IMP-INV-004 · targeted-search · required
Use targeted searches (function name, symbol, keyword) rather than reading whole
directories.

## IMP-INV-005 · stop-when-found · recommended
Stop investigating once you have enough context to act. Do not keep reading "to be safe".

## IMP-INV-006 · reuse-known-context · required
Reuse facts already established earlier in the session instead of re-deriving them.
