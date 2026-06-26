---
category: processing
affects: thinking-tokens
agents: [claude-code, cursor, codex, gemini]
---
# Imperator — Processing Rules

## IMP-PRO-001 · clarify-before-build · required
Resolve ambiguity before writing significant code.
- Ask targeted questions when requirements, scope, or acceptance criteria are unclear.
- Never guess at an ambiguous spec and build a large solution on the guess.
- When the request is concrete and unambiguous, skip the question and act — don't manufacture
  clarifications. Once the request is clear, proceed without further hand-holding.
```
do:    "Should deletes be soft or hard? It changes the schema." then build
don't: assume soft-delete, build it, and hope it's right
```

## IMP-PRO-002 · no-scope-creep · required
Stay strictly inside the requested change.
- Don't refactor, rename, reorganize, or "improve" code outside the task.
- Note unrelated issues you notice; don't fix them unprompted.

## IMP-PRO-003 · small-steps · recommended
Break large work into confirmable steps.
- Sequence the work and complete one coherent step at a time.
- For genuinely large or multi-part tasks, confirm the approach on the first slice before
  doing the rest.
- A change that is a single coherent step needs no plan announcement — just make it.

## IMP-PRO-004 · flag-breaking-changes · required
Warn before doing anything that breaks existing behavior or contracts.
- Call out changes to public APIs, schemas, configs, or shared interfaces before making them.
- Describe the blast radius and the migration/rollback path.
- Flag only *actual* breaking changes; a purely internal, behavior-preserving change (e.g. a
  local refactor) needs no warning — just make it.

## IMP-PRO-005 · prefer-existing-patterns · required
Follow the patterns already in the codebase.
- Match existing architecture, naming, and module structure rather than inventing new ones.
- If a better pattern exists, propose it instead of unilaterally introducing it.

## IMP-PRO-006 · no-speculative-abstraction · recommended
Build for the task in front of you, not an imagined future.
- Don't add config options, hooks, or generality the current requirement doesn't need.
- Solve the concrete case; generalize later when a second case actually appears.
