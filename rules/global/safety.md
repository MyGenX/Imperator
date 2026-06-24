---
category: safety
affects: risk-reduction
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Safety Rules

## IMP-SAF-001 · no-delete-without-confirm · required
Never delete files or directories without explicit confirmation.
- Confirm before removing anything you didn't create in this session.
- Prefer moving or deprecating over deleting when the intent is unclear.
- If a deletion target contradicts how it was described, stop and surface that.

## IMP-SAF-002 · no-env-modification · required
Don't touch environment or secrets files without explicit instruction.
- Leave `.env`, `.env.local`, and credential/secret files alone unless told otherwise.
- Suggest the change for the user to apply rather than editing these files yourself.

## IMP-SAF-003 · no-auto-commit · required
Don't run git history or remote operations on your own.
- No `git commit`, `git push`, `git merge`, or tag/branch deletion without being asked.
- When the user asks you to commit, follow their stated message/branch conventions.

## IMP-SAF-004 · no-dependency-install · recommended
Don't add dependencies silently.
- Ask before installing new packages or changing lockfiles.
- Prefer the standard library or an already-present dependency when it suffices.

## IMP-SAF-005 · warn-auth-changes · required
Treat auth code as high-risk.
- Flag and confirm before modifying authentication, authorization, or session logic.
- Explain the security impact of the change before making it.

## IMP-SAF-006 · no-destructive-commands · required
Never run irreversible or destructive commands without explicit confirmation.
- Includes `rm -rf`, `git reset --hard`, force-push, and any DB `DROP`/`TRUNCATE`/mass `DELETE`.
- Don't run migrations or data-mutating scripts against real data unprompted.
```
do:    show the command and ask before running `git reset --hard`
don't: run `rm -rf build/` (or worse) on your own initiative
```

## IMP-SAF-007 · no-secret-exposure · required
Never expose secrets.
- Don't print, log, echo, or commit tokens, keys, passwords, or connection strings.
- Redact secrets in examples and output; reference them by name, not value.
