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
# Set up your project interactively (asks for domains, roles, agent, style)
imperator init

# Or use a pre-built profile (domain bundle) + roles
imperator init --profile python-api --role backend-developer --role qa-engineer

# Add tech-stack (domain) rules later
imperator add python typescript postgres

# Add specialist role subagents
imperator role add frontend-developer
imperator role list

# See everything available
imperator list

# Regenerate output anytime
imperator compile                 # native modular tree for the configured agent
imperator compile --agent all     # modular files for every supported agent

# Token impact, broken down by tier
imperator stats
```

---

## How It Works

Imperator has **three tiers**, authored once and compiled into the layout your agent
loads natively.

For Claude Code, modular output is a `.claude/` tree:

```
rules/                          .claude/
  global/      ──────────────►    rules/global.md        (always loaded)
    output.md ...
  domains/     ──────────────►    rules/python.md        (path-scoped: **/*.py)
    python.md ...                 rules/typescript.md     (path-scoped: **/*.{ts,tsx})
  roles/       ──────────────►    agents/backend-developer.md   (subagent)
    qa-engineer.md ...            agents/qa-engineer.md         (subagent)
```

1. **Global rules** apply to every project — output, investigation, processing, behavior, safety. Always loaded.
2. **Domain rules** are tech-stack rules (python, typescript, postgres, ...). Agents
   with path metadata, like Claude Code and Cursor, scope them to matching files.
3. **Roles** are specialist personas (backend developer, frontend developer, QA, DevOps,
   business analyst) compiled to native **subagents** the agent delegates to by task.
4. **Done** — Claude Code loads `.claude/rules/` and `.claude/agents/` automatically.

Cursor uses `.cursor/rules/*.mdc` project rules:

```
rules/                          .cursor/rules/
  global/      ──────────────►    global.mdc                  (alwaysApply)
  domains/     ──────────────►    domains/python.mdc          (globs: **/*.py)
  roles/       ──────────────►    roles/backend-developer.mdc  (description-gated)
```

For Codex, modular output uses Codex-native project instructions and custom agents:

```
rules/                          codex project output
  global/      ──────────────►    AGENTS.md + .codex/rules/global.md
    output.md ...
  domains/     ──────────────►    AGENTS.md + .codex/rules/domains/python.md
    python.md ...
  roles/       ──────────────►    .codex/rules/roles/backend-developer.md
    qa-engineer.md ...            .codex/agents/qa-engineer.toml
```

Codex loads `AGENTS.md` through its project-instruction discovery. Role files compile
to generated rule modules and project-scoped Codex custom agents under `.codex/`.
Codex does not auto-load arbitrary `.codex/rules/*.md` instruction files, so active
global and domain guidance is embedded in root `AGENTS.md` while the rule modules
remain reviewable generated artifacts.

Gemini uses root `GEMINI.md`, generated `.gemini/rules/`, and role slash commands
under `.gemini/commands/roles/`.

Rules are authored once in a compact form (single source of truth). At compile time
you choose how they are written:

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

## Available Domains (tech stacks)

Each domain declares path globs used by agent surfaces that support file-scoped rules.

| Domain | Stack | Path scope |
|---|---|---|
| `nextjs` | Next.js 14+ App Router | `app/**`, `pages/**`, `**/*.{tsx,ts,jsx,js}` |
| `react` | React general | `**/*.{jsx,tsx}` |
| `typescript` | TypeScript strict rules | `**/*.{ts,tsx}` |
| `python` | Python best practices | `**/*.py` |
| `fastapi` | FastAPI patterns | `**/*.py` |
| `postgres` | PostgreSQL + Prisma/SQLAlchemy | `**/*.sql`, `**/migrations/**` |
| `docker` | Docker & Compose | `**/Dockerfile`, `**/compose*.y*ml` |
| `api-rest` | REST API design rules | `**/{api,routes,controllers}/**` |

## Available Roles (subagents)

| Role | Delegates | Domains it knows |
|---|---|---|
| `business-analyst` | requirements, user stories, scope (no code) | — |
| `backend-developer` | server logic, APIs, data, migrations | python, fastapi, postgres, api-rest |
| `frontend-developer` | UI, components, state, a11y | typescript, react, nextjs |
| `qa-engineer` | tests, edge cases, regression | python, typescript, fastapi, react |
| `devops` | build, CI/CD, containers, deploy | docker, postgres |

```bash
imperator role add backend-developer qa-engineer
imperator role list
```

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

| Agent | Output | Layout |
|---|---|---|
| Claude Code | `.claude/rules/` + `.claude/agents/` | **modular** (path-scoped rules + role subagents) |
| Cursor | `.cursor/rules/` | **modular** (project rules + glob-scoped domains) |
| Codex | `AGENTS.md` + `.codex/rules/` + `.codex/agents/` | **modular** (project instructions + rule modules + custom agents) |
| Gemini | `GEMINI.md` + `.gemini/rules/` + `.gemini/commands/` | **modular** (context imports + role commands) |

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
- [x] Token savings benchmarks (real-world harness — `benchmarks/`)
- [x] Modular `.claude/` layout — path-scoped domain rules + role subagents
- [x] Modular Codex layout — `AGENTS.md` + `.codex/rules/` + `.codex/agents/`
- [x] Modular Cursor layout — `.cursor/rules/*.mdc`
- [x] Modular Gemini layout — `GEMINI.md` + `.gemini/`
- [ ] Community rule + role submissions
- [ ] Website + docs

---

## License

MIT — free to use, modify, and distribute.

---

*Every rule has a reason. Every token has a purpose.* 👑
