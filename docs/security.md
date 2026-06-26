# Security

Imperator generates instruction files that your AI coding agent loads automatically.
That makes the contents of `rules/` a supply-chain surface: a malicious or careless rule
could steer an agent toward unsafe actions. This document describes how we keep that
surface trustworthy and how to report problems.

## Threat model

- **What Imperator produces** is plain, reviewable text — rule modules, subagent
  definitions, and slash commands. It runs no code on your machine at agent time.
- **Generated files are owned and marked.** Every generated file is wrapped in ownership
  markers (`imperator:begin generated` / `imperator:end generated`) so `imperator doctor`
  and `imperator clean` only ever touch Imperator-authored content, never your code.
- **The installer** clones/copies the repo and installs the CLI; review its behavior and
  flags (`--dry-run`, `--non-interactive`, `--uninstall`) in
  [install-security.md](install-security.md).
- **Community submissions** are the main risk vector. They are mitigated by review plus the
  machine checks below.

## How contributions are gated

`imperator validate` (run in CI on every PR) statically checks the rule sources before they
can ship:

- Unique rule IDs across the whole tree (duplicate IDs fail).
- Well-formed rule headings (`IMP-<CAT>-NNN · kebab-name · severity`); malformed
  rule-like headings are rejected, not silently skipped.
- Required frontmatter present; severities limited to `required` / `recommended` /
  `optional`.
- No references to unknown agents, domains, or roles; domains must declare non-empty path
  globs.
- The committed `rules/registry.json` must match the rules (drift fails CI).

Human review still applies — the checks catch structural problems, not intent. Reviewers
should reject rules that instruct an agent to weaken safety, exfiltrate data, disable
checks, or act outside a requested scope.

## Reporting a vulnerability

If you find a security issue — in the CLI, the installer, or a rule that could induce
unsafe agent behavior — please report it privately rather than opening a public issue:

- Use GitHub's **"Report a vulnerability"** (Security Advisories) on the repository, or
- email the maintainers listed in the repository metadata.

Include what you found, how to reproduce it, and the impact. We aim to acknowledge reports
promptly and will coordinate a fix and disclosure timeline with you.

## Scope

In scope: the CLI/engine, the installer scripts, and the shipped rule/role content.
Out of scope: vulnerabilities in the AI agents themselves (Claude Code, Cursor, Codex,
Gemini) — report those to their respective vendors.
