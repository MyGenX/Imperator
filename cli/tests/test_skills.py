"""Tests for the Phase 4 skills/plugin distribution."""

import json
from pathlib import Path

from imperator.parser import _parse_frontmatter
from imperator.renderers import skills

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SKILLS = {
    "imperator", "imperator-review", "imperator-compact",
    "backend-developer", "frontend-developer", "qa-engineer",
    "devops", "business-analyst",
}


def _frontmatter(text: str) -> dict:
    meta, _ = _parse_frontmatter(text)
    return meta


# ── skills bundle (export) ────────────────────────────────────────────────────

def test_skills_bundle_has_workflow_and_role_skills(tmp_path):
    written = skills.build_skills_bundle(tmp_path, root=REPO_ROOT)
    names = {p.parent.name for p in written}
    assert names == EXPECTED_SKILLS
    assert all(p.name == "SKILL.md" for p in written)


def test_every_skill_has_name_and_description(tmp_path):
    skills.build_skills_bundle(tmp_path, root=REPO_ROOT)
    for skill_md in tmp_path.rglob("SKILL.md"):
        meta = _frontmatter(skill_md.read_text(encoding="utf-8"))
        assert meta.get("name"), skill_md
        assert meta.get("description"), skill_md
        # the folder name should match the declared skill name
        assert meta["name"] == skill_md.parent.name


def test_role_skill_embeds_global_and_its_domains(tmp_path):
    skills.build_skills_bundle(tmp_path, root=REPO_ROOT)
    backend = (tmp_path / "backend-developer" / "SKILL.md").read_text(encoding="utf-8")
    assert backend.startswith("---")                 # frontmatter first
    assert "IMP-OUT-001" in backend                  # global rules embedded
    assert "Domain — Python" in backend              # python is a backend domain
    assert "Domain — TypeScript" not in backend      # typescript is not


def test_workflow_skill_is_verbatim_source_copy(tmp_path):
    skills.build_skills_bundle(tmp_path, root=REPO_ROOT)
    out = (tmp_path / "imperator" / "SKILL.md").read_text(encoding="utf-8")
    src = (REPO_ROOT / "skills" / "imperator" / "SKILL.md").read_text(encoding="utf-8")
    assert out == src


# ── plugin + marketplace manifests ────────────────────────────────────────────

def test_plugin_json_is_valid_and_named():
    data = json.loads(skills.render_plugin_json())
    assert data["name"] == "imperator"
    assert data["version"]


def test_marketplace_json_points_at_plugin():
    data = json.loads(skills.render_marketplace_json())
    assert data["name"] and data["owner"]["name"]
    assert len(data["plugins"]) == 1
    assert data["plugins"][0]["source"] == "./plugins/imperator"
    assert data["plugins"][0]["name"] == "imperator"


# ── committed distribution stays in sync ──────────────────────────────────────

def test_distribution_files_cover_plugin_layout():
    files = skills.distribution_files(REPO_ROOT)
    rels = {p.relative_to(REPO_ROOT).as_posix() for p in files}
    assert ".claude-plugin/marketplace.json" in rels
    assert "plugins/imperator/.claude-plugin/plugin.json" in rels
    assert "plugins/imperator/skills/imperator/SKILL.md" in rels
    assert "plugins/imperator/agents/backend-developer.md" in rels


def test_committed_distribution_is_in_sync():
    # The committed plugin/marketplace must match a fresh build (run compile if this fails).
    assert skills.check_distribution(REPO_ROOT) == []


def test_plugin_agent_has_subagent_frontmatter():
    files = skills.distribution_files(REPO_ROOT)
    agent_md = next(c for p, c in files.items()
                    if p.name == "backend-developer.md" and "agents" in p.parts)
    meta = _frontmatter(agent_md)
    assert meta["name"] == "backend-developer"
    assert meta.get("description")
    assert meta.get("model")
