---
name: imperator-review
description: Review the current diff against Imperator rules — scope creep, oversized rewrites, missing tests, and breaking changes. Use when asked to review changes, a PR, or a diff before committing.
---

# Imperator — Review

Review the current changes (working diff or named PR) against the rules below. Report
findings as a short, prioritized list; cite file:line. Don't rewrite the code unless asked.

## Check for
- **Scope creep** — edits, refactors, renames, or reformatting outside the stated task.
- **Oversized changes** — whole-file rewrites where a targeted edit would do; unrelated
  churn mixed into a behavior change.
- **Correctness risks** — unhandled errors/edge cases, unsafe assumptions, fabricated APIs.
- **Missing tests** — a bug fix without a regression test; new behavior without coverage.
- **Breaking changes** — public APIs, schemas, configs, or shared interfaces changed
  without a flagged migration path.
- **Safety** — secrets/credentials in code or logs; destructive commands; auth/authz changes.
- **Style fit** — new code that doesn't match surrounding naming, formatting, and idioms.

## Output
- Group findings by severity (blocker / should-fix / nit). Be specific and actionable.
- If the diff is clean, say so in one line rather than padding the review.
