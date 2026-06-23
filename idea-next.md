# Imperator — Full Project Setup 👑

Let's design this properly from the ground up!

---

## 📁 Final Project Structure

```
imperator/
│
├── README.md
├── LICENSE                          ← MIT
├── CONTRIBUTING.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── new-rule.md
│   │   └── bug-report.md
│   └── workflows/
│       └── ci.yml
│
├── install.sh                       ← macOS/Linux/WSL installer
├── install.ps1                      ← Windows PowerShell installer
│
├── cli/                             ← Python CLI (future)
│   ├── __init__.py
│   ├── main.py
│   ├── commands/
│   │   ├── init.py
│   │   ├── add.py
│   │   ├── compile.py
│   │   └── stats.py
│   ├── requirements.txt
│   └── setup.py
│
├── core/                            ← universal rules
│   ├── output.md
│   ├── investigation.md
│   ├── processing.md
│   ├── behavior.md
│   └── safety.md
│
├── extensions/                      ← stack-specific rules
│   ├── nextjs.md
│   ├── react.md
│   ├── typescript.md
│   ├── python.md
│   ├── fastapi.md
│   ├── postgres.md
│   ├── docker.md
│   └── api-rest.md
│
├── profiles/                        ← pre-built combinations
│   ├── fullstack-js.md
│   ├── python-api.md
│   └── minimal.md
│
├── agents/                          ← compiled per-agent outputs
│   ├── claude-code/
│   │   └── CLAUDE.md
│   ├── cursor/
│   │   └── .cursorrules
│   ├── codex/
│   │   └── AGENTS.md
│   └── gemini/
│       └── GEMINI.md
│
├── compiler/                        ← rule compiler scripts
│   ├── compile.py                   ← merges rules into agent files
│   └── templates/
│       ├── claude-code.j2
│       ├── cursor.j2
│       └── codex.j2
│
├── benchmarks/                      ← token savings evidence
│   └── results.md
│
└── docs/
    ├── rules-spec.md
    ├── getting-started.md
    └── contributing.md
```

---

## 🐚 install.sh (macOS / Linux / WSL)

```bash
#!/usr/bin/env bash
set -e

REPO="https://github.com/YOUR_USERNAME/imperator"
IMPERATOR_DIR="$HOME/.imperator"
VERSION="main"

# ── Colors ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${BOLD}👑 Imperator Installer${NC}"
echo -e "────────────────────────────────"
echo ""

# ── Check dependencies ───────────────────────────────────
check_dep() {
  if ! command -v "$1" &>/dev/null; then
    echo -e "${RED}✗ $1 is required but not installed.${NC}"
    echo -e "  Install it and re-run this script."
    exit 1
  fi
}

echo -e "${BLUE}→ Checking dependencies...${NC}"
check_dep git
check_dep python3

echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

# ── Clone or update repo ─────────────────────────────────
if [ -d "$IMPERATOR_DIR" ]; then
  echo -e "${YELLOW}→ Imperator already installed. Updating...${NC}"
  git -C "$IMPERATOR_DIR" pull --quiet
  echo -e "${GREEN}✓ Updated to latest version${NC}"
else
  echo -e "${BLUE}→ Cloning Imperator...${NC}"
  git clone --quiet "$REPO" "$IMPERATOR_DIR"
  echo -e "${GREEN}✓ Cloned to $IMPERATOR_DIR${NC}"
fi

echo ""

# ── Install Python CLI ───────────────────────────────────
echo -e "${BLUE}→ Installing Python CLI...${NC}"
pip3 install -e "$IMPERATOR_DIR/cli" --quiet
echo -e "${GREEN}✓ CLI installed${NC}"

echo ""

# ── Add to PATH if needed ────────────────────────────────
SHELL_RC=""
if [[ "$SHELL" == *"zsh"* ]]; then
  SHELL_RC="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
  SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
  if ! grep -q "imperator" "$SHELL_RC" 2>/dev/null; then
    echo "export PATH=\"\$HOME/.imperator/bin:\$PATH\"" >> "$SHELL_RC"
    echo -e "${GREEN}✓ Added to PATH in $SHELL_RC${NC}"
  fi
fi

echo ""
echo -e "${BOLD}${GREEN}✓ Imperator installed successfully!${NC}"
echo ""
echo -e "  Run ${BOLD}imperator init${NC} in your project to get started"
echo -e "  Docs: ${BLUE}https://github.com/YOUR_USERNAME/imperator${NC}"
echo ""
```

---

## 💻 install.ps1 (Windows PowerShell)

```powershell
# Imperator Installer for Windows
# Requires PowerShell 5.1+ and Git + Python 3

$ErrorActionPreference = "Stop"
$REPO = "https://github.com/YOUR_USERNAME/imperator"
$IMPERATOR_DIR = "$HOME\.imperator"

Write-Host ""
Write-Host "👑 Imperator Installer" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "────────────────────────────────" -ForegroundColor Blue
Write-Host ""

# ── Check dependencies ───────────────────────────────────
function Check-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "✗ $cmd is required but not installed." -ForegroundColor Red
        Write-Host "  Please install it and re-run this script." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "→ Checking dependencies..." -ForegroundColor Cyan
Check-Command "git"
Check-Command "python"
Write-Host "✓ All dependencies found" -ForegroundColor Green
Write-Host ""

# ── Clone or update ──────────────────────────────────────
if (Test-Path $IMPERATOR_DIR) {
    Write-Host "→ Imperator already installed. Updating..." -ForegroundColor Yellow
    git -C $IMPERATOR_DIR pull --quiet
    Write-Host "✓ Updated to latest version" -ForegroundColor Green
} else {
    Write-Host "→ Cloning Imperator..." -ForegroundColor Cyan
    git clone --quiet $REPO $IMPERATOR_DIR
    Write-Host "✓ Cloned to $IMPERATOR_DIR" -ForegroundColor Green
}

Write-Host ""

# ── Install Python CLI ───────────────────────────────────
Write-Host "→ Installing Python CLI..." -ForegroundColor Cyan
pip install -e "$IMPERATOR_DIR\cli" --quiet
Write-Host "✓ CLI installed" -ForegroundColor Green

Write-Host ""

# ── Add to PATH ──────────────────────────────────────────
$BinPath = "$IMPERATOR_DIR\bin"
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($CurrentPath -notlike "*imperator*") {
    [Environment]::SetEnvironmentVariable(
        "PATH",
        "$CurrentPath;$BinPath",
        "User"
    )
    Write-Host "✓ Added to PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "✓ Imperator installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "  Run 'imperator init' in your project to get started" -ForegroundColor White
Write-Host "  Docs: https://github.com/YOUR_USERNAME/imperator" -ForegroundColor Cyan
Write-Host ""
```

---

## 🐍 Python CLI — `cli/main.py`

```python
#!/usr/bin/env python3
"""
Imperator CLI — Command your AI agent
"""

import argparse
import sys
from commands.init import cmd_init
from commands.add import cmd_add
from commands.compile import cmd_compile
from commands.stats import cmd_stats

VERSION = "0.1.0"

def main():
    parser = argparse.ArgumentParser(
        prog="imperator",
        description="👑 Imperator — Reusable rules for AI coding agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  imperator init                  Interactive project setup
  imperator add nextjs            Add Next.js extension rules
  imperator add python fastapi    Add multiple extensions
  imperator compile               Generate agent-specific files
  imperator stats                 Show token savings estimate
        """
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"Imperator {VERSION}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    # ── init ─────────────────────────────────────────────
    init_parser = subparsers.add_parser(
        "init",
        help="Interactive setup for your project"
    )
    init_parser.add_argument(
        "--profile",
        choices=["minimal", "fullstack-js", "python-api"],
        help="Use a pre-built profile"
    )

    # ── add ──────────────────────────────────────────────
    add_parser = subparsers.add_parser(
        "add",
        help="Add extension rules to your project"
    )
    add_parser.add_argument(
        "extensions",
        nargs="+",
        help="Extensions to add (e.g. nextjs react postgres)"
    )

    # ── compile ──────────────────────────────────────────
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile rules into agent-specific files"
    )
    compile_parser.add_argument(
        "--agent",
        choices=["claude-code", "cursor", "codex", "gemini", "all"],
        default="claude-code",
        help="Target agent (default: claude-code)"
    )

    # ── stats ────────────────────────────────────────────
    subparsers.add_parser(
        "stats",
        help="Show estimated token savings"
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "init": cmd_init,
        "add": cmd_add,
        "compile": cmd_compile,
        "stats": cmd_stats,
    }

    commands[args.command](args)

if __name__ == "__main__":
    main()
```

---

## 🐍 CLI — `cli/commands/init.py`

```python
"""
imperator init — Interactive project setup
"""

import os
import json
import shutil

IMPERATOR_DIR = os.path.expanduser("~/.imperator")
EXTENSIONS_AVAILABLE = [
    "nextjs", "react", "typescript",
    "python", "fastapi", "postgres",
    "docker", "api-rest"
]

PROFILES = {
    "fullstack-js": ["nextjs", "react", "typescript", "postgres"],
    "python-api":   ["python", "fastapi", "postgres", "api-rest"],
    "minimal":      []
}

def cmd_init(args):
    print("\n👑 Imperator — Project Setup\n")
    print("─" * 40)

    # ── Profile or manual ────────────────────────────────
    if hasattr(args, "profile") and args.profile:
        selected = PROFILES[args.profile]
        print(f"✓ Using profile: {args.profile}")
    else:
        selected = interactive_setup()

    # ── Agent selection ──────────────────────────────────
    agent = select_agent()

    # ── Compile and write ────────────────────────────────
    compile_rules(selected, agent)

    # ── Save config ──────────────────────────────────────
    save_config(selected, agent)

    print("\n✓ Imperator setup complete!\n")
    print(f"  Agent file generated for: {agent}")
    print(f"  Extensions active: {', '.join(selected) if selected else 'core only'}")
    print("\n  Run 'imperator compile' anytime to regenerate.\n")


def interactive_setup():
    print("\nAvailable extensions:\n")
    for i, ext in enumerate(EXTENSIONS_AVAILABLE, 1):
        print(f"  [{i}] {ext}")

    print("\nEnter extension numbers separated by commas")
    print("(or press Enter for core rules only):\n")

    raw = input("  → ").strip()

    if not raw:
        return []

    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(EXTENSIONS_AVAILABLE):
                selected.append(EXTENSIONS_AVAILABLE[idx])

    return selected


def select_agent():
    agents = ["claude-code", "cursor", "codex", "gemini"]
    print("\nSelect your AI agent:\n")
    for i, agent in enumerate(agents, 1):
        print(f"  [{i}] {agent}")

    print("")
    raw = input("  → ").strip()

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(agents):
            return agents[idx]

    return "claude-code"


def compile_rules(extensions, agent):
    from commands.compile import compile_to_agent
    compile_to_agent(extensions, agent)


def save_config(extensions, agent):
    config = {
        "agent": agent,
        "extensions": extensions,
        "version": "0.1.0"
    }
    with open(".imperator.json", "w") as f:
        json.dump(config, f, indent=2)
```

---

## 📄 README.md

````markdown
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

**Imperator fixes this** with a standardized, reusable, stack-aware ruleset
you install once and use everywhere.

---

## Install

**macOS / Linux / WSL:**
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/imperator/main/install.sh | bash
```

**Windows (PowerShell 5.1+):**
```powershell
irm https://raw.githubusercontent.com/YOUR_USERNAME/imperator/main/install.ps1 | iex
```

**Requirements:** Git + Python 3.8+

---

## Quick Start

```bash
# Setup your project interactively
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
```

---

## How It Works

```
core rules          +    extensions      =    your CLAUDE.md
─────────────────        ──────────────       ──────────────
output.md                nextjs.md            compiled &
investigation.md    +    typescript.md   →    merged into
processing.md            postgres.md          one file
safety.md
```

1. **Core rules** apply to every project — output control, safety, behavior
2. **Extensions** add stack-specific rules for your tech
3. **Compiler** merges everything into the right file for your agent
4. **Done** — your agent now follows Imperator rules every session

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

---

## Contributing

Want to add a rule or extension? See [CONTRIBUTING.md](CONTRIBUTING.md)

Every rule needs:
- A unique ID (e.g. `IMP-OUT-001`)
- A clear name
- A category
- Token impact declaration
- Supported agents list

---

## Roadmap

- [x] Core rules
- [x] Basic extensions
- [x] Claude Code support
- [x] install.sh + install.ps1
- [x] Python CLI (init, add, compile)
- [ ] Token savings benchmarks
- [ ] Cursor / Codex / Gemini support
- [ ] `imperator stats` command
- [ ] Community rule submissions
- [ ] Website + docs

---

## License

MIT — free to use, modify, and distribute.

---

*Every rule has a reason. Every token has a purpose.* 👑
````

---

## 🚀 Next Steps to Launch

1. **Create the GitHub repo** — `imperator`
2. **Push the structure** with all files above
3. **Write the core rules** in detail (we can do this together!)
4. **Test the install scripts** on macOS + Windows
5. **Share it** — this could genuinely trend on GitHub! 🌟

---

Want me to now write out the **full detailed core rules** or the **compiler logic** in Python next? 👑