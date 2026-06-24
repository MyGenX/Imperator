"""Unit tests for the Imperator compile engine (v0.2 — 3-tier modular)."""

from pathlib import Path

import pytest

from imperator import engine

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
        layout="modular", root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert ".claude/CLAUDE.md" in rels
    assert ".claude/rules/global.md" in rels
    assert ".claude/rules/python.md" in rels
    assert ".claude/rules/typescript.md" in rels
    assert ".claude/agents/backend-developer.md" in rels
    assert ".claude/agents/qa-engineer.md" in rels


def test_compile_project_flat_fallback(tmp_path):
    written = engine.compile_project(
        ["nextjs"], ["backend-developer"], style="compact",
        out_dir=tmp_path, agent="cursor", layout="flat", root=REPO_ROOT,
    )
    assert len(written) == 1
    assert written[0].name == ".cursorrules"


# ── rendering: legacy flat ───────────────────────────────────────────────────

def test_render_full_style_has_frontmatter():
    groups = engine.filter_by_agent(engine.load_groups([], root=REPO_ROOT), "claude-code")
    out = engine.render(groups, "claude-code", "full")
    assert "id: IMP-OUT-001" in out
    assert "### no-preamble" in out


def test_compile_to_agent_writes_file(tmp_path):
    path = engine.compile_to_agent(
        ["nextjs"], "claude-code", style="compact", out_dir=tmp_path, root=REPO_ROOT
    )
    assert path.name == "CLAUDE.md"
    assert path.read_text(encoding="utf-8").count("IMP-NXT-") >= 1


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
