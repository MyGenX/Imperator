# Agent renderer checklist

Use this when adding support for a new agent target (e.g. Windsurf, Cline, Copilot).
A renderer turns the parsed `RuleGroup`/`Role` model into that agent's native layout.

## Wiring
- [ ] Add the agent id to `cli/imperator/catalog.py` → `AGENTS`.
- [ ] Add a renderer in `cli/imperator/renderers/` (follow `base.py` helpers:
      `write_file`, `add_generated_markers`, `rules_block`, `render_rule`).
- [ ] Dispatch it from `cli/imperator/compiler.py::compile_project`.
- [ ] Emit native slash commands via `commands.write_agent_commands` (or document why
      the target has no command surface).

## Output contract
- [ ] Every generated file is wrapped in the ownership markers
      (`imperator:begin generated` / `imperator:end generated`) so `clean`/`doctor`
      only touch Imperator-owned files.
- [ ] Global rules are always-on; domain rules carry path metadata where the target
      supports it (else embed active domains in the root instruction file).
- [ ] Roles compile to the target's native subagent/custom-agent surface, or are
      skipped with a documented reason.
- [ ] Respect the compression `style` (standard / compact / strict) via `render_rule`.

## Verification
- [ ] `compiler/compile.py` smoke-builds the new agent (it iterates `engine.AGENTS`).
- [ ] Add tests in `cli/tests/` covering the new layout (see `test_engine.py`,
      `test_commands.py`).
- [ ] Update `docs/agent-support.md`, `docs/rules-spec.md` (tier table), and the
      README "Supported Agents" table.
- [ ] `imperator validate` and `pytest cli/tests -q` pass; `python compiler/compile.py
      --check` stays green.
