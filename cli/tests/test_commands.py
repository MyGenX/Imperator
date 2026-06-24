"""Tests for Phase 5 agent-native slash commands."""

from pathlib import Path

from imperator import engine
from imperator.parser import _parse_frontmatter
from imperator.renderers import commands

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED = set(commands.COMMANDS)  # imperator, -review, -plan, -rules, -stats


def _compile(tmp_path, agent):
    engine.compile_project(["python"], ["backend-developer"], style="standard",
                           out_dir=tmp_path, agent=agent, root=REPO_ROOT)
    return tmp_path


def test_command_catalog_matches_skill_sources():
    # every command must have an authored skill source with name + description
    for name in commands.COMMANDS:
        desc, body = commands.load_command(name, REPO_ROOT)
        assert desc, name
        assert body, name


def test_claude_commands_written_with_frontmatter(tmp_path):
    root = _compile(tmp_path, "claude-code")
    cmd_dir = root / ".claude" / "commands"
    names = {p.stem for p in cmd_dir.glob("*.md")}
    assert names == EXPECTED

    review = (cmd_dir / "imperator-review.md").read_text(encoding="utf-8")
    meta, _ = _parse_frontmatter(review)
    assert meta.get("description")
    assert engine.MARKER_BEGIN in review


def test_cursor_commands_written(tmp_path):
    root = _compile(tmp_path, "cursor")
    names = {p.stem for p in (root / ".cursor" / "commands").glob("*.md")}
    assert names == EXPECTED


def test_gemini_commands_are_toml(tmp_path):
    root = _compile(tmp_path, "gemini")
    cmd_dir = root / ".gemini" / "commands"
    stems = {p.stem for p in cmd_dir.glob("*.toml")}
    assert EXPECTED <= stems  # role command toml(s) may also exist

    plan = (cmd_dir / "imperator-plan.toml").read_text(encoding="utf-8")
    assert "description = " in plan
    assert "prompt = " in plan
    assert engine.MARKER_BEGIN in plan


def test_codex_prompts_written(tmp_path):
    root = _compile(tmp_path, "codex")
    prompt_dir = root / ".codex" / "prompts"
    names = {p.stem for p in prompt_dir.glob("*.md")}
    assert names == EXPECTED
    stats = (prompt_dir / "imperator-stats.md").read_text(encoding="utf-8")
    meta, _ = _parse_frontmatter(stats)
    assert meta.get("description")


def test_compile_returns_command_paths(tmp_path):
    written = engine.compile_project(
        ["python"], [], style="standard", out_dir=tmp_path,
        agent="claude-code", root=REPO_ROOT,
    )
    rels = {p.relative_to(tmp_path).as_posix() for p in written}
    assert ".claude/commands/imperator.md" in rels
    assert ".claude/commands/imperator-stats.md" in rels
