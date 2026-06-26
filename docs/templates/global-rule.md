<!--
TEMPLATE: a new global rule (added to an existing rules/global/<category>.md file).
Global rules are ALWAYS loaded for every task, so they must be universal — true
regardless of language or stack. Copy the heading + body below into the right file,
renumber the ID to the next free number in that category, then run:

    imperator validate --write-registry

Categories & ID prefixes:
  output.md         → IMP-OUT-NNN   (what the agent writes back)
  investigation.md  → IMP-INV-NNN   (how the agent reads files)
  processing.md     → IMP-PRO-NNN   (how the agent plans & thinks)
  behavior.md       → IMP-BEH-NNN   (what actions the agent takes)
  safety.md         → IMP-SAF-NNN   (what the agent must never do)
-->

## IMP-OUT-NNN · short-kebab-name · required
One imperative directive sentence — concrete enough to verify.
- A short, testable specific (a boundary).
- When it does NOT apply (the exception).
- Keep to 2–4 bullets. No rationale paragraphs.
