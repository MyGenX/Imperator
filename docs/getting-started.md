# Getting Started

## 1. Install

```bash
# macOS / Linux / WSL
curl -fsSL https://raw.githubusercontent.com/VachaganGrigoryan/Imperator/main/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/VachaganGrigoryan/Imperator/main/install.ps1 | iex
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
- which **extensions** apply to your stack,
- which **agent** you use (Claude Code, Cursor, Codex, Gemini),
- which **style** to write (`compact` or `full`).

This writes the agent file (e.g. `CLAUDE.md`) and a small `.imperator.json` config.

Prefer a one-liner? Use a profile:

```bash
imperator init --profile fullstack-js --agent claude-code --style compact
```

## 3. Evolve

```bash
imperator add docker          # add an extension and recompile
imperator compile --agent all # regenerate every agent file
imperator stats               # see compiled size / token estimate
```

## 4. Commit the agent file

Commit the generated `CLAUDE.md` / `.cursorrules` / `AGENTS.md` / `GEMINI.md` (and
`.imperator.json`) so your whole team shares the same rules.
