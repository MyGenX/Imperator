<!-- Thanks for contributing to Imperator! Keep PRs small and scoped. -->

## What & why

<!-- One or two sentences: what this changes and the reason. -->

## Type of change

- [ ] New / changed **global rule** (`rules/global/`)
- [ ] New / changed **domain** (`rules/domains/` + `catalog.DOMAINS_AVAILABLE`)
- [ ] New / changed **role** (`rules/roles/` + `catalog.ROLES_AVAILABLE`)
- [ ] New **agent renderer**
- [ ] CLI / engine change
- [ ] Docs / benchmarks only

## Checklist

- [ ] Rule IDs are unique and follow `IMP-<CAT>-NNN · kebab-name · severity`.
- [ ] Ran `imperator validate --write-registry` and committed `rules/registry.json`.
- [ ] `imperator validate` passes (no errors).
- [ ] `pytest cli/tests -q` passes.
- [ ] `python compiler/compile.py --check` is green (committed plugin/marketplace in sync).
- [ ] Updated relevant docs (see `docs/rule-authoring.md`, `docs/domain-authoring.md`,
      `docs/role-authoring.md`) and the README tables if the change is user-visible.

## Notes for reviewers

<!-- Anything non-obvious, trade-offs, or follow-ups. -->
