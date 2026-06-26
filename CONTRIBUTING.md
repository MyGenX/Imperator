# Contributing to Imperator 👑

Thanks for helping command AI agents better!

## Ways to contribute

- **Add a rule** to an existing global or domain file — see [docs/rule-authoring.md](docs/rule-authoring.md)
- **Add a domain** for a new tech stack — see [docs/domain-authoring.md](docs/domain-authoring.md)
- **Add a role** (specialist subagent) — see [docs/role-authoring.md](docs/role-authoring.md)
- **Add an agent renderer** — see [docs/templates/agent-renderer-checklist.md](docs/templates/agent-renderer-checklist.md)
- **Improve docs** or the CLI

Copy-paste starting points live in [docs/templates/](docs/templates/).

## Adding a rule

Rules are authored once in **compact form** — see [docs/rules-spec.md](docs/rules-spec.md)
for the full spec. Each rule is a directive line followed by a few bullets:

```markdown
## IMP-OUT-008 · my-rule-name · recommended
One imperative sentence stating the rule, concrete enough to verify.
- A specific boundary or exception (when it does / doesn't apply).
- Another short, testable specific.
```

Requirements for every rule:

- **Unique ID** — `IMP-<CAT>-<NNN>` (e.g. `IMP-NXT-007`). Use the prefix already used in
  that file.
- **kebab-case name** — short and descriptive.
- **Severity** — `required`, `recommended`, or `optional`.
- **Directive + bullets** — imperative directive first, then 2–4 testable bullets. Keep it
  lean (global rules are always in context). Add a compact `do:`/`don't:` block only for
  high-impact rules where the directive alone is easy to misread.

## Adding a domain (tech stack)

1. Create `rules/domains/<name>.md` with file frontmatter (`category: domain`,
   `domain: <name>`, `affects`, `paths: [...]` globs, `agents`).
2. Add `<name>` to `DOMAINS_AVAILABLE` in `cli/imperator/catalog.py`.
3. If it belongs in a profile, update `PROFILES` in the same file.
4. Regenerate examples: `python compiler/compile.py`.

## Adding a role (subagent)

1. Create `rules/roles/<name>.md` with frontmatter (`role`, `description`, `tools`,
   `model`, `domains: [...]`) and a system-prompt body.
2. Add `<name>` to `ROLES_AVAILABLE` in `cli/imperator/catalog.py`.
3. Regenerate examples: `python compiler/compile.py`.

## Before opening a PR

```bash
pip install -e cli
imperator validate --write-registry   # checks IDs/headings/frontmatter; updates registry
pytest cli/tests
python compiler/compile.py --check     # committed plugin/marketplace must be current
```

Commit the updated `rules/registry.json` along with your rule change. If `--check` fails,
run `python compiler/compile.py` and commit the regenerated files. CI runs the same gates.

## Rule philosophy

> Every rule has a reason. Every token has a purpose.

A rule earns its place only if it changes agent behavior in a way that saves tokens,
prevents mistakes, or enforces a real best practice. No filler.
