---
category: safety
affects: risk-reduction
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Safety Rules

## IMP-SAF-001 · no-delete-without-confirm · required
Never delete files or directories without explicit confirmation.

## IMP-SAF-002 · no-env-modification · required
Never modify `.env`, `.env.local`, or any secrets file without explicit instruction.

## IMP-SAF-003 · no-auto-commit · required
Never run `git commit`, `git push`, or `git merge` without explicit instruction.

## IMP-SAF-004 · no-dependency-install · recommended
Never install new packages or dependencies without asking first.

## IMP-SAF-005 · warn-auth-changes · required
Always flag and confirm before modifying authentication or authorization code.

## IMP-SAF-006 · no-destructive-commands · required
Never run destructive or irreversible commands (`rm -rf`, `DROP`, `git reset --hard`,
force-push) without explicit confirmation.

## IMP-SAF-007 · no-secret-exposure · required
Never print, log, or commit secrets, tokens, or credentials.
