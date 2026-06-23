"""Unit tests for the Imperator compile engine."""

from pathlib import Path

import pytest

from imperator import engine

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_parse_file_extracts_rules_and_metadata():
    group = engine.parse_file(REPO_ROOT / "core" / "output.md")
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


def test_load_groups_core_first_then_extensions():
    groups = engine.load_groups(["nextjs"], root=REPO_ROOT)
    sources = [g.source for g in groups]
    assert sources[: len(engine.CORE_ORDER)] == engine.CORE_ORDER
    assert sources[-1] == "nextjs"


def test_resolve_profile():
    assert engine.resolve_profile("fullstack-js") == [
        "nextjs", "react", "typescript", "postgres"
    ]
    assert engine.resolve_profile("minimal") == []
    with pytest.raises(ValueError):
        engine.resolve_profile("does-not-exist")


def test_unknown_extension_raises():
    with pytest.raises(ValueError):
        engine.load_groups(["nonsense"], root=REPO_ROOT)


def test_filter_by_agent_keeps_targeted_rules():
    groups = engine.load_groups([], root=REPO_ROOT)
    filtered = engine.filter_by_agent(groups, "claude-code")
    assert sum(len(g.rules) for g in filtered) > 0

    # An agent not listed anywhere yields no rules.
    empty = engine.filter_by_agent(groups, "nonexistent-agent")
    assert empty == []


def test_render_compact_style():
    groups = engine.filter_by_agent(engine.load_groups([], root=REPO_ROOT), "claude-code")
    out = engine.render(groups, "claude-code", "compact")
    assert "IMP-OUT-001 · no-preamble · required" in out
    assert "CLAUDE.md" in out


def test_render_full_style_has_frontmatter():
    groups = engine.filter_by_agent(engine.load_groups([], root=REPO_ROOT), "claude-code")
    out = engine.render(groups, "claude-code", "full")
    assert "id: IMP-OUT-001" in out
    assert "severity: required" in out
    assert "### no-preamble" in out


def test_render_all_agents():
    groups = engine.filter_by_agent(
        engine.load_groups(["nextjs"], root=REPO_ROOT), "cursor"
    )
    for agent in engine.AGENTS:
        g = engine.filter_by_agent(engine.load_groups(["nextjs"], root=REPO_ROOT), agent)
        out = engine.render(g, agent, "compact")
        assert out.strip()


def test_compile_to_agent_writes_file(tmp_path):
    path = engine.compile_to_agent(
        ["nextjs"], "claude-code", style="compact", out_dir=tmp_path, root=REPO_ROOT
    )
    assert path.name == "CLAUDE.md"
    assert path.read_text(encoding="utf-8").count("IMP-NXT-") >= 1


def test_estimate_tokens():
    assert engine.estimate_tokens("a" * 400) == 100
