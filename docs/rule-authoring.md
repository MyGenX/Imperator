# Authoring a global rule

Global rules live in `rules/global/<category>.md` and are **always loaded** for every
task on every project. That makes them the most expensive context Imperator ships, so the
bar is high: a global rule must be universally true — independent of language, framework,
or stack. Anything stack-specific belongs in a [domain](domain-authoring.md).

See [rules-spec.md](rules-spec.md) for the full format reference and
[templates/global-rule.md](templates/global-rule.md) for a copy-paste starting point.

## Categories

| File | ID prefix | Controls |
|---|---|---|
| `output.md` | `IMP-OUT` | What the agent writes back (output tokens) |
| `investigation.md` | `IMP-INV` | How the agent reads files (processing tokens) |
| `processing.md` | `IMP-PRO` | How the agent plans & thinks (thinking tokens) |
| `behavior.md` | `IMP-BEH` | What actions the agent takes |
| `safety.md` | `IMP-SAF` | What the agent must never do (risk reduction) |

## The heading

```
## IMP-<CAT>-<NNN> · <kebab-name> · <severity>
```

- **ID** unique across the whole project; use the next free number in the category.
- **name** short kebab-case.
- **severity** one of `required` | `recommended` | `optional`.
- The separator is the middle dot `·` (U+00B7), not a hyphen or bullet.

## The body

A rule body is a structured prompt, not prose:

1. **Directive** — one imperative sentence, concrete enough to verify.
2. **2–4 bullets** — testable specifics: boundaries and exceptions. No rationale paragraphs.
3. **Examples (rare)** — only for high-impact rules that are easy to misread, append a
   compact fenced do/don't block. These cost always-on context, so reserve them.

The compression profile decides how much of this ships: `standard` keeps everything,
`compact` drops the fenced examples, `strict` keeps only the directive line. Write the
full richness; compression trims it deterministically.

## Checklist

1. Add the heading + body to the right `rules/global/*.md` file.
2. `imperator validate --write-registry` — updates `rules/registry.json` and checks
   uniqueness, heading format, and frontmatter.
3. `pytest cli/tests -q` and `python compiler/compile.py --check`.
4. Open a PR (the template lists these same gates).

## Good vs. over-reaching

- ✅ "Edit in place; never regenerate a whole file to change part of it." — universal.
- ❌ "Use `ruff` to format." — stack-specific; that belongs in the Python domain.
- ❌ A rule that restates a more specific one. Keep the set orthogonal.
