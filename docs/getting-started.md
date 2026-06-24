# Getting Started

## 1. Install

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/MyGenX/Imperator/main/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/MyGenX/Imperator/main/install.ps1 | iex
```

Or, from a checkout:

```bash
pip install -e cli
```

## 2. Initialize a project

Run inside your project root:

```bash
imperator init
```

You'll be asked for:
- **domains** — the tech stacks in your project (python, typescript, postgres, ...),
- **roles** — specialist subagents to add (backend-developer, qa-engineer, ...),
- **agent** (Claude Code, Cursor, Codex, Gemini) and **style** (`compact` / `full`).

For **Claude Code** this writes a modular `.claude/` tree:

```
.claude/
  CLAUDE.md            # thin pointer
  rules/
    global.md          # always-on rules
    python.md          # path-scoped: loads only when editing **/*.py
    ...
  agents/
    backend-developer.md   # specialist subagent
    ...
.imperator.json
```

For **Codex** this writes modular Codex-native files:

```
AGENTS.md                 # project instructions with global + active domain rules
.codex/
  rules/
    global.md
    domains/python.md
    roles/backend-developer.md
  agents/
    backend-developer.toml   # specialist custom agent
    ...
.imperator.json
```

Codex custom agents are used when you explicitly ask Codex to delegate work to them.
Unlike Claude Code rule files, Codex project instructions are directory-layered, not
glob-scoped, so active domain guidance is embedded in root `AGENTS.md`.

For **Cursor** this writes `.cursor/rules/*.mdc`. For **Gemini** this writes
`GEMINI.md`, `.gemini/rules/`, and `.gemini/commands/roles/`.

Prefer a one-liner? Use a profile (domain bundle) and `--role`:

```bash
imperator init --profile python-api --agent claude-code --style compact \
  --role backend-developer --role qa-engineer

imperator init --profile python-api --agent codex --style compact \
  --role backend-developer --role qa-engineer

imperator init --profile fullstack-js --agent cursor --style compact \
  --role frontend-developer

imperator init --profile python-api --agent gemini --style compact \
  --role backend-developer
```

## 3. Evolve

```bash
imperator add docker              # add a tech-stack (domain) and recompile
imperator role add devops         # add a specialist subagent
imperator role list               # see available roles
imperator list                    # see all domains and roles
imperator compile                 # regenerate native output from config
imperator stats                   # token impact by tier
```

## 4. Commit the output

Commit the generated native output (`.claude/`, `.cursor/`, `AGENTS.md` + `.codex/`,
or `GEMINI.md` + `.gemini/`) and `.imperator.json` so your whole team shares the
same rules and role subagents.
