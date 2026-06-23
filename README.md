# 👑 Imperator

> **Command your AI agent. Not the other way around.**

Imperator is an open-source collection of reusable rules for AI coding agents.
Each **Imperator Rule** controls agent behavior, reduces wasted tokens, and
enforces best practices — universally or per stack.

Works with **Claude Code**, Cursor, Codex, Gemini and more.

---

## Why Imperator?

AI coding agents are powerful but often:
- 🗣️ Over-explain simple things (wastes output tokens)
- 🔍 Read entire codebases when they need one file (wastes processing tokens)
- 🤔 Assume instead of asking (wastes thinking tokens)
- 💥 Make changes outside the requested scope (breaks things)
- 🔁 Repeat context they already have (wastes everything)

**Imperator fixes this** with a standardized, reusable, stack-aware ruleset you
install once and use everywhere.

---

## Install

**macOS / Linux / WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/MyGenX/Imperator/main/install.sh | bash
```

**Windows (PowerShell 5.1+):**
```powershell
irm https://raw.githubusercontent.com/MyGenX/Imperator/main/install.ps1 | iex
```

**Requirements:** Git + Python 3.8+

From a checkout you can also just `pip install -e cli`.

---

## Quick Start

```bash
# Set up your project interactively (asks for extensions, agent, and style)
imperator init

# Or use a pre-built profile
imperator init --profile fullstack-js
imperator init --profile python-api
imperator init --profile minimal

# Add extensions later
imperator add nextjs
imperator add python fastapi postgres

# Regenerate agent files anytime
imperator compile
imperator compile --agent cursor
imperator compile --agent all --style full

# See how big the compiled ruleset is
imperator stats
```

---

## How It Works

```
core rules          +    extensions      =    your CLAUDE.md
─────────────────        ──────────────       ──────────────
output.md                nextjs.md            compiled &
investigation.md    +    typescript.md   →    merged into
processing.md            postgres.md          one file
behavior.md
safety.md
```

1. **Core rules** apply to every project — output, investigation, processing, behavior, safety
2. **Extensions** add stack-specific rules for your tech
3. **The compiler** merges everything into the right file for your agent
4. **Done** — your agent follows Imperator rules every session

Rules are authored once in a compact form (single source of truth). At compile time
you choose how they are written into the agent file:

| Style | Looks like | Best for |
|---|---|---|
| `compact` (default) | `## IMP-OUT-001 · no-preamble · required` | Lean, human-readable agent files |
| `full` | per-rule YAML frontmatter (`id`, `category`, `affects`, `severity`, `agents`) | Tooling / machine processing |

```bash
imperator compile --style compact
imperator compile --style full
```

---

## Rule Categories

| Category | Controls | Token Impact |
|---|---|---|
| `output` | What the agent writes back | ⬇️ Output tokens |
| `investigation` | How the agent reads files | ⬇️ Processing tokens |
| `processing` | How the agent plans & thinks | ⬇️ Thinking tokens |
| `behavior` | What actions the agent takes | ⬇️ All types |
| `safety` | What the agent must never do | 🛡️ Risk reduction |

---

## Available Extensions

| Extension | Stack |
|---|---|
| `nextjs` | Next.js 14+ App Router |
| `react` | React general |
| `typescript` | TypeScript strict rules |
| `python` | Python best practices |
| `fastapi` | FastAPI patterns |
| `postgres` | PostgreSQL + Prisma/SQLAlchemy |
| `docker` | Docker & Compose |
| `api-rest` | REST API design rules |

---

## Profiles

Pre-built combinations for common stacks:

```bash
imperator init --profile fullstack-js   # nextjs + react + typescript + postgres
imperator init --profile python-api     # python + fastapi + postgres + api-rest
imperator init --profile minimal        # core rules only
```

---

## Supported Agents

| Agent | File Generated |
|---|---|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Codex | `AGENTS.md` |
| Gemini | `GEMINI.md` |

Compiled examples of the full ruleset live in [`agents/`](agents/).

---

## Contributing

Want to add a rule or extension? See [CONTRIBUTING.md](CONTRIBUTING.md) and
[docs/rules-spec.md](docs/rules-spec.md).

Every rule needs a unique ID (e.g. `IMP-OUT-001`), a kebab-case name, and a severity
(`required` / `recommended` / `optional`).

---

## Roadmap

- [x] Core rules
- [x] Extensions (nextjs, react, typescript, python, fastapi, postgres, docker, api-rest)
- [x] Claude Code, Cursor, Codex, Gemini outputs
- [x] `install.sh` + `install.ps1`
- [x] Python CLI (`init`, `add`, `compile`, `stats`)
- [x] Compact **and** full-frontmatter output styles
- [ ] Token savings benchmarks (real-world)
- [ ] Community rule submissions
- [ ] Website + docs

---

## License

MIT — free to use, modify, and distribute.

---

*Every rule has a reason. Every token has a purpose.* 👑
