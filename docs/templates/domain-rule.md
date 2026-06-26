---
category: domain
domain: my-stack            # must match the filename (rules/domains/my-stack.md)
affects: all-tokens
paths: ["**/*.ext"]         # non-empty glob list that scopes this domain to files
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — My Stack

<!--
TEMPLATE: a new domain (tech-stack) rule file. Save as rules/domains/<domain>.md.
Steps:
  1. Pick a domain id (kebab-case) and use it for both the filename and `domain:`.
  2. Register it in cli/imperator/catalog.py → DOMAINS_AVAILABLE.
  3. (Optional) add it to a PROFILES bundle in catalog.py.
  4. Number rules IMP-XXX-NNN with one consistent prefix for the file.
  5. Run: imperator validate --write-registry
The H1-to-first-rule text below is the optional "golden path" overview.
-->

**Golden path:** one or two sentences on the recommended conventions and layout for
this stack, so the rules below have framing context.

## IMP-XXX-001 · first-rule-name · required
One imperative directive sentence specific to this stack.
- A testable specific.
- A boundary or exception.

## IMP-XXX-002 · second-rule-name · recommended
Another directive.
- Specifics here.
