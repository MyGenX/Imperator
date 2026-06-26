# Authoring a domain (tech stack)

A domain is a set of rules scoped to one tech stack — Python, Postgres, Docker, etc.
Domains live in `rules/domains/<domain>.md` and are loaded only when a project selects
them. Agents that support file-scoped rules (Claude Code, Cursor) apply them only to
files matching the domain's `paths` globs.

Start from [templates/domain-rule.md](templates/domain-rule.md); the format reference is
in [rules-spec.md](rules-spec.md).

## Steps

1. **Pick an id** — kebab-case, e.g. `go` or `react-native`. It is used for the filename,
   the `domain:` frontmatter key, and the CLI (`imperator add <id>`).
2. **Write `rules/domains/<id>.md`** with the required frontmatter:

   ```yaml
   ---
   category: domain
   domain: <id>                 # must equal the filename
   affects: all-tokens
   paths: ["**/*.ext"]          # non-empty; what files this domain scopes to
   agents: [claude-code, cursor, codex, gemini]
   ---
   ```

3. **Register it** in `cli/imperator/catalog.py` → `DOMAINS_AVAILABLE`. The validator
   fails if a domain file is not registered, or a registered domain has no file.
4. *(Optional)* add it to a bundle in `catalog.PROFILES` (e.g. `python-api`).
5. **Author the rules** — one consistent `IMP-<PREFIX>-NNN` prefix per file, each with a
   directive + bullets (see [rule-authoring.md](rule-authoring.md)). Add an optional
   "golden path" overview between the H1 and the first rule.
6. **Validate & test:**

   ```bash
   imperator validate --write-registry
   pytest cli/tests -q
   python compiler/compile.py --check
   ```

## `paths` matter

`paths` is what makes a domain cheap: it is compiled into Claude Code `paths:` and Cursor
`globs` metadata so the rules load only when the agent touches matching files. A domain
with no meaningful path scope is really a global rule — reconsider the tier. The validator
requires a non-empty `paths` list for every domain.

## Keep domains focused

A domain should capture the *non-obvious, opinionated* conventions of a stack — the things
a competent agent gets wrong without guidance. Avoid restating language basics or
duplicating global rules.
