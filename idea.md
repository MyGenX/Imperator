# Imperator 👑 — Let's Build This!

Love the name! **Imperator** = ruler/commander in Latin — perfect for a project that **commands how AI agents behave**. Let's design this properly!

---

## 🏛️ Project Vision

> **Imperator** is an open-source collection of reusable rules for AI coding agents (Claude Code, Cursor, Codex and more). Each **Imperator Rule** controls agent behavior, reduces wasted tokens, and enforces best practices — universally or per stack.

---

## 📁 Proposed Project Structure

```
imperator/
├── README.md
├── LICENSE                        ← MIT
├── package.json                   ← for future CLI
│
├── core/                          ← universal rules (every project)
│   ├── behavior.md                ← what Claude can/cannot do
│   ├── output.md                  ← controls output tokens
│   ├── investigation.md           ← controls how Claude reads/explores
│   ├── processing.md              ← controls thinking/planning behavior
│   └── safety.md                  ← dangerous action guards
│
├── extensions/                    ← stack-specific rule sets
│   ├── nextjs.md
│   ├── react.md
│   ├── python.md
│   ├── postgres.md
│   ├── docker.md
│   ├── api-rest.md
│   └── typescript.md
│
├── agents/                        ← agent-specific formatting
│   ├── claude-code/
│   │   └── CLAUDE.md              ← compiled for Claude Code
│   ├── cursor/
│   │   └── .cursorrules
│   ├── codex/
│   │   └── AGENTS.md
│   └── gemini/
│       └── GEMINI.md
│
├── profiles/                      ← pre-built combinations
│   ├── fullstack-js.md            ← core + nextjs + postgres + api
│   ├── python-api.md              ← core + python + api
│   └── minimal.md                 ← core only, ultra lean
│
└── docs/
    ├── rules-spec.md              ← how to write a rule
    ├── contributing.md
    └── benchmarks.md              ← token savings evidence
```

---

## 👑 What is an Imperator Rule?

Each rule is a **named, documented, purposeful instruction** with metadata:

```markdown
---
id: IMP-OUT-001
name: no-preamble
category: output
affects: output-tokens
severity: required | recommended | optional
agents: [claude-code, cursor, codex, gemini]
---

## Rule: No Preamble

**Never** start responses with filler phrases such as:
- "Sure! I'd be happy to help..."
- "Great question!"
- "Of course! Let me help you with that..."

Start directly with the answer, code, or action.
```

---

## 🗂️ Rule Categories & Token Impact

| Category | Controls | Token Impact |
|---|---|---|
| **output** | What Claude writes back | ⬇️ Output tokens |
| **investigation** | How Claude reads/explores files | ⬇️ Processing tokens |
| **processing** | How Claude plans & thinks | ⬇️ Thinking tokens |
| **behavior** | What actions Claude takes | ⬇️ All types |
| **safety** | What Claude must never do | 🛡️ Risk reduction |
| **communication** | How Claude asks questions | ⬇️ Output tokens |

---

## 📜 Core Rules Draft

### Output Rules (`core/output.md`)
```markdown
# Imperator — Output Rules

## IMP-OUT-001 · no-preamble · required
Never open with filler phrases. Start with the answer.

## IMP-OUT-002 · no-full-file-rewrite · required
Never rewrite entire files. Show only changed lines or diffs.

## IMP-OUT-003 · no-unsolicited-summary · recommended
Never summarize what you just did unless explicitly asked.

## IMP-OUT-004 · no-redundant-comments · recommended
Never add inline code comments that restate what the code clearly does.

## IMP-OUT-005 · concise-explanations · recommended
Prefer bullet points over paragraphs. Keep explanations under 3 lines
unless complexity demands more.
```

### Investigation Rules (`core/investigation.md`)
```markdown
# Imperator — Investigation Rules

## IMP-INV-001 · no-full-codebase-scan · required
Never scan the entire codebase unless explicitly instructed.
Read only files directly relevant to the current task.

## IMP-INV-002 · no-repeat-file-read · required
Never read the same file twice in one session unless it has changed.

## IMP-INV-003 · ask-before-explore · recommended
If task scope is unclear, ask which files are relevant
before exploring independently.

## IMP-INV-004 · targeted-search · required
Use targeted searches (function name, class, keyword)
rather than reading entire directories.
```

### Processing Rules (`core/processing.md`)
```markdown
# Imperator — Processing Rules

## IMP-PRO-001 · clarify-before-build · required
Ask clarifying questions BEFORE generating large amounts of code.
Never assume ambiguous requirements.

## IMP-PRO-002 · no-scope-creep · required
Stay strictly within the task scope.
Do not refactor, rename, or improve code outside the requested change.

## IMP-PRO-003 · small-steps · recommended
Break large tasks into small confirmed steps.
Complete and confirm each step before proceeding.

## IMP-PRO-004 · flag-breaking-changes · required
Always warn about potential breaking changes BEFORE making them.
```

### Safety Rules (`core/safety.md`)
```markdown
# Imperator — Safety Rules

## IMP-SAF-001 · no-delete-without-confirm · required
Never delete files or directories without explicit confirmation.

## IMP-SAF-002 · no-env-modification · required
Never modify .env, .env.local or any secrets file without explicit instruction.

## IMP-SAF-003 · no-auto-commit · required
Never run git commit, git push, or git merge without explicit instruction.

## IMP-SAF-004 · no-dependency-install · recommended
Never install new packages or dependencies without asking first.

## IMP-SAF-005 · warn-auth-changes · required
Always flag and confirm before modifying any authentication
or authorization related code.
```

---

## 🧩 Extension Example — Next.js

```markdown
# Imperator Extension — Next.js
# extends: core

## IMP-NXT-001 · app-router-only · required
Always use App Router patterns. Never suggest Pages Router solutions.

## IMP-NXT-002 · server-first · required
Default to Server Components. Use "use client" only when
interactivity or browser APIs are explicitly needed.

## IMP-NXT-003 · no-useeffect-fetch · required
Never use useEffect for data fetching. Use Server Components
or React Query / SWR instead.

## IMP-NXT-004 · handle-loading-error · recommended
Always implement loading.tsx and error.tsx when creating new routes.
```

---

## 🚀 Roadmap

### Phase 1 — Foundation 🪨
- [ ] Set up GitHub repo
- [ ] Write core rules (output, investigation, processing, safety)
- [ ] Claude Code CLAUDE.md compiled output
- [ ] README + contributing guide
- [ ] MIT License

### Phase 2 — Extensions 🧩
- [ ] Next.js, React, TypeScript
- [ ] Python, FastAPI
- [ ] PostgreSQL, Prisma
- [ ] Docker, REST API

### Phase 3 — CLI Tool ⚡
- [ ] `npx imperator init` — interactive setup
- [ ] `npx imperator add nextjs` — adds extension
- [ ] `npx imperator compile` — generates agent-specific files
- [ ] `npx imperator stats` — token usage benchmarks

### Phase 4 — Community 🌍
- [ ] Contribution templates for new rules
- [ ] Benchmark suite to measure token savings
- [ ] Support for Cursor, Codex, Gemini
- [ ] Website / docs

---

## 💡 What Makes Imperator Unique

| | Caveman | Custom CLAUDE.md | **Imperator** |
|---|---|---|---|
| Reusable | ⚠️ Partially | ❌ Per project | ✅ Universal |
| Stack-aware | ❌ | ⚠️ Manual | ✅ Extensions |
| Token categories | Output only | Mixed | ✅ All 3 types |
| Standardized rules | ❌ | ❌ | ✅ Named + versioned |
| Multi-agent | ✅ | ❌ | ✅ Planned |
| Community driven | ✅ | ❌ | ✅ Open source |
| Measurable | ✅ | ❌ | ✅ Benchmarks |

---

## 🎯 Tagline Ideas

- *"Imperator — Command your AI agent, not the other way around"*
- *"Imperator — Rules that make AI agents smarter, faster, cheaper"*
- *"Imperator — Every rule has a reason. Every token has a purpose."*

---

Shall we start building this? I can help you:
1. **Draft the full core rules** in detail
2. **Write the README** for GitHub
3. **Design the CLI** concept
4. **Pick the best tagline** and repo structure

👑 **Imperator** could genuinely become the go-to standard for AI agent rules — just like ESLint became the standard for JavaScript! 🚀