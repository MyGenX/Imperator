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

Imperator is not a terse-output gimmick; it is a stack-aware rules compiler.

## Why not just CLAUDE.md?

`CLAUDE.md` is useful, but it is one agent's project instruction file. Imperator
keeps rules in one source tree, then compiles them into the native layout for
each agent:

- Global behavior rules for every task.
- Domain rules for Python, TypeScript, Postgres, Docker, and other stacks.
- Role instructions for specialist subagents.
- Reviewable generated files your team can commit.

That means the same rule policy can produce `.claude/`, `.cursor/rules/`,
`AGENTS.md` + `.codex/`, or `GEMINI.md` + `.gemini/` without rewriting the rules
by hand.

## Before / After

Source rules:

```text
rules/
  global/
    output.md
    investigation.md
    processing.md
    behavior.md
    safety.md
  domains/
    python.md
    postgres.md
  roles/
    backend-developer.md
    qa-engineer.md
```

Generated Claude Code output:

```text
.claude/
  CLAUDE.md
  rules/
    global.md
    python.md
    postgres.md
  agents/
    backend-developer.md
    qa-engineer.md
```

Generated Codex output:

```text
AGENTS.md
.codex/
  rules/
    global.md
    domains/python.md
    domains/postgres.md
    roles/backend-developer.md
    roles/qa-engineer.md
  agents/
    backend-developer.toml
    qa-engineer.toml
```

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

Review the installer behavior in [docs/install-security.md](docs/install-security.md).

Installer flags:

```bash
./install.sh --dry-run --dir ~/.imperator --no-color --non-interactive
./install.sh --force
./install.sh --uninstall
```

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

# Check and clean generated files
imperator doctor
imperator clean --dry-run
imperator clean

# Validate rule sources + rule-ID registry (also runs in CI)
imperator validate

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

Rules are authored once (single source of truth). At compile time you pick a
**compression profile** that controls how verbosely each rule is written:

| Profile | Renders | Best for |
|---|---|---|
| `standard` (default) | directive + bullets + do/don't examples | Full detail |
| `compact` | directive + bullets (no examples) | Leaner context |
| `strict` | directive line only | Minimal footprint |

```bash
imperator compile --style standard
imperator compile --style strict
```

## Slash commands

Every compiled project also gets native slash commands for its agent
(`.claude/commands/`, `.cursor/commands/`, `.gemini/commands/`, `.codex/prompts/`):

| Command | Does |
|---|---|
| `/imperator` | Apply Imperator working rules to the current task |
| `/imperator-review` | Review the diff for scope, minimal-diff, tests, breaking changes |
| `/imperator-plan` | Produce a small, scoped implementation plan |
| `/imperator-rules` | Summarize the active rules |
| `/imperator-stats` | Report active domains, rule count, approx. context cost |

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

| Agent | Status | Output |
|---|---|---|
| Claude Code | Current | `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/agents/` |
| Cursor | Current | `.cursor/rules/` |
| Codex | Current | `AGENTS.md`, `.codex/rules/`, `.codex/agents/` |
| Gemini | Current | `GEMINI.md`, `.gemini/rules/`, `.gemini/commands/` |
| Windsurf | Planned | Not generated yet |
| Cline | Planned | Not generated yet |
| OpenCode | Planned | Not generated yet |
| Copilot | Planned | Not generated yet |

See [docs/agent-support.md](docs/agent-support.md) for the generated layout and
current limitations of each target.

## Alternatives

Imperator is a rules compiler, not a single-agent prompt, output-tone trick, or
skill registry. See [docs/alternatives.md](docs/alternatives.md) for the baseline
comparison with Caveman, Vercel Skills, Claude Code plugins, and Vercel
agent-skills.

## Contributing

Want to add a rule or extension? See [CONTRIBUTING.md](CONTRIBUTING.md), the per-tier
guides ([rule](docs/rule-authoring.md) · [domain](docs/domain-authoring.md) ·
[role](docs/role-authoring.md) authoring), copy-paste [templates](docs/templates/), and
the [rules spec](docs/rules-spec.md). Maintainers: [release](docs/release.md) ·
[security](docs/security.md).

Every rule needs a unique ID (e.g. `IMP-OUT-001`), a kebab-case name, and a severity
(`required` / `recommended` / `optional`). Run `imperator validate --write-registry`
before opening a PR — CI enforces it.

---

## Roadmap

- [x] Core rules
- [x] Extensions (nextjs, react, typescript, python, fastapi, postgres, docker, api-rest)
- [x] Claude Code, Cursor, Codex, Gemini outputs
- [x] `install.sh` + `install.ps1`
- [x] Python CLI (`init`, `add`, `compile`, `stats`)
- [x] Compression profiles (standard / compact / strict)
- [x] Agent-native slash commands (`/imperator`, `/imperator-review`, ...)
- [x] Token savings benchmarks (real-world harness — `benchmarks/`)
- [x] Modular `.claude/` layout — path-scoped domain rules + role subagents
- [x] Modular Codex layout — `AGENTS.md` + `.codex/rules/` + `.codex/agents/`
- [x] Modular Cursor layout — `.cursor/rules/*.mdc`
- [x] Modular Gemini layout — `GEMINI.md` + `.gemini/`
- [x] Real-world benchmark results (`benchmarks/results.md` — deterministic, reproducible)
- [x] Community submission workflow (`imperator validate`, rule-ID registry, authoring docs + templates)
- [ ] Website + docs

---

## License

MIT — free to use, modify, and distribute.

---

*Every rule has a reason. Every token has a purpose.* 👑
