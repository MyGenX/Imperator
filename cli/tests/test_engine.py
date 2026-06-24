"""Unit tests for the Imperator compile engine (v0.2 — 3-tier modular)."""

import json
from pathlib import Path

import pytest

from imperator import engine
from imperator.config import load_config

REPO_ROOT = Path(__file__).resolve().parents[2]


# ── parsing ──────────────────────────────────────────────────────────────────

def test_parse_global_file_extracts_rules_and_metadata():
    group = engine.parse_file(REPO_ROOT / "rules" / "global" / "output.md")
    assert group.category == "output"
    assert group.title == "Imperator — Output Rules"
    assert len(group.rules) >= 5

    first = group.rules[0]
    assert first.id == "IMP-OUT-001"
    assert first.name == "no-preamble"
    assert first.severity == "required"
    assert first.affects == "output-tokens"
    assert "filler" in first.body.lower()
    assert "claude-code" in first.agents


def test_domain_file_has_path_globs_with_brace_groups():
    group = engine.parse_file(REPO_ROOT / "rules" / "domains" / "typescript.md")
    assert group.source == "typescript"
    # brace group must survive the inline-list splitter
    assert group.paths == ["**/*.{ts,tsx}"]


def test_global_file_has_no_paths():
    group = engine.parse_file(REPO_ROOT / "rules" / "global" / "safety.md")
    assert group.paths == []


def test_domain_overview_parsed_and_rendered_above_rules():
    group = engine.parse_file(REPO_ROOT / "rules" / "domains" / "nextjs.md")
    # overview captured from between the H1 and the first rule
    assert group.overview
    assert "Golden path" in group.overview
    assert "IMP-NXT" not in group.overview  # stops before the first rule

    # render through the real compile path (filter_by_agent must preserve overview)
    filtered = engine.filter_by_agent([group], "claude-code")[0]
    assert filtered.overview == group.overview
    out = engine.render_domain_file(filtered, "compact")
    assert out.index("Golden path") < out.index("## IMP-NXT-001")


def test_global_file_has_no_overview():
    group = engine.parse_file(REPO_ROOT / "rules" / "global" / "output.md")
    assert group.overview == ""


# ── roles ────────────────────────────────────────────────────────────────────

def test_load_roles_parses_folded_description_and_domains():
    roles = {r.name: r for r in engine.load_roles(engine.ROLES_AVAILABLE, REPO_ROOT)}
    assert set(roles) == set(engine.ROLES_AVAILABLE)

    backend = roles["backend-developer"]
    assert backend.model == "sonnet"
    assert "python" in backend.domains
    assert backend.description and backend.description.endswith(".")  # folded scalar joined
    assert "Read" in backend.tools

    # business-analyst has no domains and is read-only
    ba = roles["business-analyst"]
    assert ba.domains == []
    assert "Edit" not in ba.tools


def test_unknown_role_raises():
    with pytest.raises(ValueError):
        engine.load_roles(["not-a-role"], REPO_ROOT)


# ── loading / profiles / filtering ───────────────────────────────────────────

def test_load_groups_global_first_then_domains():
    groups = engine.load_groups(["nextjs"], root=REPO_ROOT)
    sources = [g.source for g in groups]
    assert sources[: len(engine.GLOBAL_ORDER)] == engine.GLOBAL_ORDER
    assert sources[-1] == "nextjs"


def test_resolve_profile():
    assert engine.resolve_profile("fullstack-js") == [
        "nextjs", "react", "typescript", "postgres"
    ]
    assert engine.resolve_profile("minimal") == []
    with pytest.raises(ValueError):
        engine.resolve_profile("does-not-exist")


def test_unknown_domain_raises():
    with pytest.raises(ValueError):
        engine.load_domains(["nonsense"], root=REPO_ROOT)


def test_filter_by_agent_keeps_targeted_rules():
    groups = engine.load_global(REPO_ROOT)
    filtered = engine.filter_by_agent(groups, "claude-code")
    assert sum(len(g.rules) for g in filtered) > 0
    assert engine.filter_by_agent(groups, "nonexistent-agent") == []


# ── rendering: modular ───────────────────────────────────────────────────────

def test_render_domain_file_has_paths_frontmatter():
    g = engine.parse_file(REPO_ROOT / "rules" / "domains" / "python.md")
    out = engine.render_domain_file(g, "compact")
    assert out.startswith("---")
    assert 'paths:' in out
    assert '"**/*.py"' in out
    assert "IMP-PY-001 · type-hints · required" in out


def test_render_global_file_has_no_paths_frontmatter():
    groups = engine.filter_by_agent(engine.load_global(REPO_ROOT), "claude-code")
    out = engine.render_global_file(groups, "compact")
    assert not out.lstrip().startswith("---\npaths")
    assert "IMP-OUT-001" in out


def test_role_agent_embeds_only_intersection_of_domains():
    global_groups = engine.filter_by_agent(engine.load_global(REPO_ROOT), "claude-code")
    domain_groups = engine.filter_by_agent(
        engine.load_domains(["python", "typescript"], REPO_ROOT), "claude-code"
    )
    backend = engine.load_roles(["backend-developer"], REPO_ROOT)[0]
    out = engine.render_role_agent(backend, global_groups, domain_groups, "compact")

    assert out.startswith("---")
    assert "name: backend-developer" in out
    assert "model: sonnet" in out
    # backend.domains ∩ selected = {python}; typescript is excluded
    assert "Domain — Python" in out
    assert "Domain — TypeScript" not in out
    # global rules always present
    assert "IMP-OUT-001" in out


def test_compile_project_modular_writes_tree(tmp_path):
    written = engine.compile_project(
        ["python", "typescript"], ["backend-developer", "qa-engineer"],
        style="compact", out_dir=tmp_path, agent="claude-code",
        root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert ".claude/CLAUDE.md" in rels
    assert ".claude/rules/global.md" in rels
    assert ".claude/rules/python.md" in rels
    assert ".claude/rules/typescript.md" in rels
    assert ".claude/agents/backend-developer.md" in rels
    assert ".claude/agents/qa-engineer.md" in rels


def test_compile_project_codex_modular_writes_tree(tmp_path):
    written = engine.compile_project(
        ["python", "typescript"], ["backend-developer", "qa-engineer"],
        style="compact", out_dir=tmp_path, agent="codex",
        root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert "AGENTS.md" in rels
    assert ".codex/rules/global.md" in rels
    assert ".codex/rules/domains/python.md" in rels
    assert ".codex/rules/roles/backend-developer.md" in rels
    assert ".codex/agents/backend-developer.toml" in rels
    assert ".codex/agents/qa-engineer.toml" in rels
    assert not any(p.startswith(".claude/") for p in rels)


def test_codex_role_agent_is_toml_custom_agent_without_claude_fields():
    global_groups = engine.filter_by_agent(engine.load_global(REPO_ROOT), "codex")
    domain_groups = engine.filter_by_agent(
        engine.load_domains(["python", "typescript"], REPO_ROOT), "codex"
    )
    backend = engine.load_roles(["backend-developer"], REPO_ROOT)[0]
    out = engine.render_codex_agent(backend, global_groups, domain_groups, "compact")

    assert 'name = "backend-developer"' in out
    assert 'description = "Implements and reviews server-side code:' in out
    assert "developer_instructions =" in out
    assert "tools:" not in out
    assert "model:" not in out
    assert "Domain \\u2014 Python" in out
    assert "Domain \\u2014 TypeScript" not in out
    assert "IMP-OUT-001" in out


def test_codex_modular_root_embeds_domain_rules():
    global_groups = engine.filter_by_agent(engine.load_global(REPO_ROOT), "codex")
    domain_groups = engine.filter_by_agent(
        engine.load_domains(["python"], REPO_ROOT), "codex"
    )
    out = engine.render_codex_agents_md(
        global_groups, domain_groups, "compact", ["python"], ["backend-developer"]
    )

    assert out.startswith("<!-- Generated by Imperator")
    assert "# Imperator Global Rules" in out
    assert "# Active Domain Rules" in out
    assert "Domain — Python" in out
    assert ".codex/agents/" in out


def test_compile_project_cursor_modular_writes_rules(tmp_path):
    written = engine.compile_project(
        ["python", "typescript"], ["backend-developer"],
        style="compact", out_dir=tmp_path, agent="cursor", root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert ".cursor/rules/global.mdc" in rels
    assert ".cursor/rules/domains/python.mdc" in rels
    assert ".cursor/rules/domains/typescript.mdc" in rels
    assert ".cursor/rules/roles/backend-developer.mdc" in rels
    assert ".cursorrules" not in rels

    global_rule = (tmp_path / ".cursor" / "rules" / "global.mdc").read_text(
        encoding="utf-8"
    )
    assert "alwaysApply: true" in global_rule
    domain_rule = (tmp_path / ".cursor" / "rules" / "domains" / "python.mdc").read_text(
        encoding="utf-8"
    )
    assert "globs:" in domain_rule
    assert '"**/*.py"' in domain_rule


def test_compile_project_gemini_modular_writes_rules_and_commands(tmp_path):
    written = engine.compile_project(
        ["python"], ["backend-developer"], style="compact",
        out_dir=tmp_path, agent="gemini", root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert "GEMINI.md" in rels
    assert ".gemini/rules/global.md" in rels
    assert ".gemini/rules/domains/python.md" in rels
    assert ".gemini/rules/roles/backend-developer.md" in rels
    assert ".gemini/commands/roles/backend-developer.toml" in rels

    gemini_md = (tmp_path / "GEMINI.md").read_text(encoding="utf-8")
    assert "@.gemini/rules/global.md" in gemini_md
    assert "@.gemini/rules/domains/python.md" in gemini_md


def test_load_config_drops_legacy_layout(tmp_path):
    (tmp_path / ".imperator.json").write_text(
        json.dumps({"agent": "codex", "domains": [], "roles": [], "layout": "flat"}),
        encoding="utf-8",
    )
    config = load_config(tmp_path)
    assert config["agent"] == "codex"
    assert "layout" not in config


def test_old_flat_templates_are_removed():
    templates = REPO_ROOT / "cli" / "imperator" / "templates"
    assert not (templates / "claude-code.j2").exists()
    assert not (templates / "cursor.j2").exists()
    assert not (templates / "codex.j2").exists()
    assert not (templates / "gemini.j2").exists()


# ── per-renderer schema (generated markers + native frontmatter) ─────────────

def _compile(tmp_path, agent, domains=("python", "typescript"),
             roles=("backend-developer",)):
    engine.compile_project(list(domains), list(roles), style="compact",
                           out_dir=tmp_path, agent=agent, root=REPO_ROOT)
    return tmp_path


def test_claude_schema_frontmatter_before_marker(tmp_path):
    root = _compile(tmp_path, "claude-code")

    domain = (root / ".claude/rules/python.md").read_text(encoding="utf-8")
    assert domain.startswith("---")                       # YAML frontmatter first
    assert "paths:" in domain
    assert domain.index("paths:") < domain.index(engine.MARKER_BEGIN)
    assert engine.MARKER_END in domain

    glob = (root / ".claude/rules/global.md").read_text(encoding="utf-8")
    assert engine.MARKER_BEGIN in glob and engine.MARKER_END in glob
    assert "---\npaths" not in glob.lstrip()              # global is not path-scoped

    agent_file = (root / ".claude/agents/backend-developer.md").read_text(encoding="utf-8")
    for field in ("name:", "description:", "model:"):
        assert field in agent_file
        assert agent_file.index(field) < agent_file.index(engine.MARKER_BEGIN)


def test_cursor_schema_frontmatter_before_marker(tmp_path):
    root = _compile(tmp_path, "cursor")

    glob = (root / ".cursor/rules/global.mdc").read_text(encoding="utf-8")
    assert glob.startswith("---")
    assert "alwaysApply: true" in glob
    assert glob.index("alwaysApply") < glob.index(engine.MARKER_BEGIN)

    domain = (root / ".cursor/rules/domains/python.mdc").read_text(encoding="utf-8")
    assert "globs:" in domain
    assert domain.index("globs:") < domain.index(engine.MARKER_BEGIN)
    assert '"**/*.py"' in domain


def test_codex_schema_agents_md_and_toml_agent(tmp_path):
    root = _compile(tmp_path, "codex")

    agents_md = (root / "AGENTS.md").read_text(encoding="utf-8")
    assert engine.MARKER_BEGIN in agents_md and engine.MARKER_END in agents_md
    assert "# Imperator Global Rules" in agents_md
    assert "# Active Domain Rules" in agents_md

    toml_agent = (root / ".codex/agents/backend-developer.toml").read_text(encoding="utf-8")
    assert f"# {engine.MARKER_BEGIN}" in toml_agent      # toml-comment marker
    assert 'name = "backend-developer"' in toml_agent
    assert "developer_instructions =" in toml_agent

    assert (root / ".codex/rules/global.md").is_file()   # reviewable artifacts only
    assert not (root / ".claude").exists()


def test_gemini_schema_md_rules_and_command(tmp_path):
    root = _compile(tmp_path, "gemini")

    gemini_md = (root / "GEMINI.md").read_text(encoding="utf-8")
    assert engine.MARKER_BEGIN in gemini_md
    assert "@.gemini/rules/global.md" in gemini_md

    rule = (root / ".gemini/rules/domains/python.md").read_text(encoding="utf-8")
    assert engine.MARKER_BEGIN in rule and engine.MARKER_END in rule

    command = (root / ".gemini/commands/roles/backend-developer.toml").read_text(encoding="utf-8")
    assert f"# {engine.MARKER_BEGIN}" in command


def test_engine_facade_reexports_submodules():
    # the shim must keep re-exporting the split modules' public names
    from imperator import catalog, compiler, loader, parser
    from imperator.renderers import RENDERERS
    assert engine.compile_project is compiler.compile_project
    assert engine.parse_file is parser.parse_file
    assert engine.find_root is loader.find_root
    assert engine.VERSION == catalog.VERSION
    assert set(RENDERERS) == set(engine.AGENTS)


def test_estimate_tokens():
    assert engine.estimate_tokens("a" * 400) == 100


def test_multiline_rule_body_preserves_bullets():
    group = engine.parse_file(REPO_ROOT / "rules" / "global" / "output.md")
    rule = next(r for r in group.rules if r.name == "no-full-file-rewrite")
    # the body must keep its bullet list (not collapse to one line)
    assert "\n- " in rule.body

    compact = engine.render_rule(rule, "compact")
    assert "## IMP-OUT-002 · no-full-file-rewrite · required" in compact
    assert "\n- " in compact

    full = engine.render_rule(rule, "full")
    assert "### no-full-file-rewrite" in full
    assert "\n- " in full
