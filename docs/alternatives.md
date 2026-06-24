# Alternatives

Imperator is not a terse-output gimmick; it is a stack-aware rules compiler.

It starts with one rule source under `rules/`, then compiles those rules into the
native instruction layout each coding agent already understands. The goal is not
only shorter replies. The goal is reusable behavior, stack-specific guidance,
specialist roles, and auditable generated files your team can commit.

## Comparison

| Project | Primary focus | Imperator difference |
|---|---|---|
| [Caveman](https://github.com/JuliusBrussee/caveman) | Claude Code skill for reducing output tokens with terse phrasing. | Imperator includes output discipline, but also investigation, processing, safety, domain rules, and role agents across multiple agent formats. |
| [Vercel Skills](https://github.com/vercel-labs/skills) | Open skill tooling and registry workflow for installable agent skills. | Imperator is a rule compiler for repository policy. It emits committed project files rather than acting primarily as a skill package manager. |
| [Claude Code plugins](https://github.com/anthropics/claude-plugins-official) | Claude Code plugin distribution for commands, skills, MCP servers, and related extensions. | Imperator targets project instruction layouts and team rules, with Claude Code as one output target rather than the only runtime. |
| [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) | Official collection of agent skills. | Imperator is not a skill collection. It transforms a shared ruleset into agent-native files for Claude Code, Cursor, Codex, and Gemini. |

## Positioning

Use Imperator when you want:

- One source of truth for reusable agent rules.
- Rules split by global behavior, tech stack, and specialist role.
- Generated files that match each agent's native loading model.
- A committed project configuration that the team can review and reproduce.
- A path to support more agents without rewriting the rules themselves.

Do not use Imperator if all you need is a single personal prompt, one Claude Code
plugin, or a registry of prebuilt skills. Those tools solve different problems.
