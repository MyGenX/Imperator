# Release process

Imperator ships two things from one source tree: the **Python CLI** (`cli/`) and the
committed **distribution** (the Claude Code plugin under `plugins/imperator/` and the
repo-root `.claude-plugin/marketplace.json`). A release makes sure both, plus the rule-ID
registry, are consistent and tagged.

## Versioning

Single source of truth: `VERSION` in `cli/imperator/catalog.py`. Follow semver:

- **patch** — rule wording fixes, docs, bug fixes (no ID or schema changes).
- **minor** — new rules, domains, roles, or an agent renderer (additive, IDs only added).
- **major** — renamed/removed rule IDs, changed frontmatter schema, or other breaking
  changes to generated output.

Renaming or removing a rule ID is breaking — existing projects reference it. Prefer adding
a new rule and marking the old one clearly.

## Checklist

1. Bump `VERSION` in `cli/imperator/catalog.py`.
2. Regenerate the rule-ID registry:
   ```bash
   imperator validate --write-registry
   ```
3. Regenerate the committed distribution (plugin + marketplace):
   ```bash
   python compiler/compile.py
   ```
4. Run the gates:
   ```bash
   imperator validate
   pytest cli/tests -q
   python compiler/compile.py --check
   bash -n install.sh
   ```
5. Update `CHANGELOG`/release notes (new rules, domains, roles; any breaking IDs).
6. Commit, then tag:
   ```bash
   git tag -a vX.Y.Z -m "Imperator vX.Y.Z"
   git push --tags
   ```

## What CI enforces

Every PR runs `imperator validate`, `pytest cli/tests`, and `python compiler/compile.py
--check`. A release should be green on all of these before tagging — the tag is just the
human step on top of an already-passing tree.
