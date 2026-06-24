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

Prefer a one-liner? Use a profile (domain bundle) and `--role`:

```bash
imperator init --profile python-api --agent claude-code --style compact \
  --role backend-developer --role qa-engineer
```

## 3. Evolve

```bash
imperator add docker              # add a tech-stack (domain) and recompile
imperator role add devops         # add a specialist subagent
imperator role list               # see available roles
imperator list                    # see all domains and roles
imperator compile                 # regenerate .claude/ from config
imperator compile --layout flat   # single-file output instead
imperator stats                   # token impact by tier
```

## 4. Commit the output

Commit the generated `.claude/` tree (or the flat agent file) and `.imperator.json`
so your whole team shares the same rules and role subagents.
