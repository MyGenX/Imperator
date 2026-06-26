# Authoring a role (specialist subagent)

A role is a specialist persona — backend developer, QA engineer, DevOps — that compiles to
a native subagent (Claude Code `.claude/agents/`, Codex/Gemini custom agents). Roles live
in `rules/roles/<role>.md`: frontmatter configures the agent, the body is its system
prompt.

Start from [templates/role.md](templates/role.md).

## Steps

1. **Pick a role id** — kebab-case, e.g. `data-engineer`. Used for the filename and the
   `role:` key.
2. **Write `rules/roles/<id>.md`:**

   ```yaml
   ---
   role: <id>                   # must equal the filename
   description: >-
     When the agent should delegate to this role (concrete about the work).
   tools: Read, Edit, Write, Bash, Grep, Glob   # Claude Code allowlist; "" = inherit all
   model: sonnet                # sonnet | opus | haiku | inherit
   domains: [python, postgres]  # must all exist under rules/domains/
   ---
   # <Role Title>

   You are a senior <specialty>. ...
   ```

3. **Register it** in `cli/imperator/catalog.py` → `ROLES_AVAILABLE`. The validator fails
   on an unregistered role file, a registered role with no file, or a `domains:` entry that
   names a domain with no rule file.
4. **Validate & test:**

   ```bash
   imperator validate --write-registry
   pytest cli/tests -q
   python compiler/compile.py --check
   ```

## How `domains` compose

At compile time a role subagent embeds the persona **plus** the global rules **plus** the
intersection of its `domains` and the project's selected domains (`role.domains ∩
selected`). So a `backend-developer` with `domains: [python, fastapi, postgres, api-rest]`
in a project that only selected `python` ships the persona + global rules + Python rules —
self-contained, no dangling references.

## Writing the persona

- Lead with identity and scope: what this role owns and is trusted to decide.
- Reaffirm the Imperator global rules and active domain rules.
- A few concrete standards beat a long manifesto — the global/domain rules already carry
  the detail.
- The `description` is the routing signal; make it specific so the agent delegates the
  right work and nothing else.
