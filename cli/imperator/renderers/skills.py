"""Distribution renderers: portable skill bundles + the Claude Code plugin.

Two distributables are produced from the same rule sources:

  - A **skills bundle** (`build_skills_bundle`) of Vercel-skills-compatible folders
    (`<name>/SKILL.md`, frontmatter `name`+`description`) — the 3 authored workflow
    skills plus one generated skill per role. Used by `imperator export --format skills`.
  - The **Claude Code plugin** + marketplace (`distribution_files` / `write_distribution`
    / `check_distribution`) — committed under `plugins/imperator/` and a repo-root
    `.claude-plugin/marketplace.json`. Used by `compiler/compile.py`.

This module is a distribution format, not a per-agent compile target, so it is not part
of the `RENDERERS` dispatch.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..catalog import ROLES_AVAILABLE, VERSION
from ..loader import (filter_by_agent, find_root, load_domains, load_global,
                      load_roles)
from .base import add_generated_markers, role_instruction_doc
from .claude import render_role_agent

WORKFLOW_SKILLS = ["imperator", "imperator-review", "imperator-compact"]
PLUGIN_NAME = "imperator"
OWNER = "MyGenX"
PLUGIN_DESCRIPTION = (
    "Reusable working rules and specialist role subagents for AI coding agents."
)


# ── Skill rendering ──────────────────────────────────────────────────────────

def render_role_skill(role, global_groups, domain_groups, style: str) -> str:
    """A role rendered as a portable SKILL.md (name+description + embedded rules)."""
    body = role_instruction_doc(role, global_groups, domain_groups, style, "skills")
    frontmatter = (
        "---\n"
        f"name: {role.name}\n"
        f"description: {json.dumps(role.description)}\n"
        "---\n"
    )
    return add_generated_markers(Path("SKILL.md"), frontmatter + "\n" + body)


# ── Plugin / marketplace manifests (deterministic JSON, no comment markers) ───

def render_plugin_json() -> str:
    return json.dumps({
        "name": PLUGIN_NAME,
        "description": PLUGIN_DESCRIPTION,
        "version": VERSION,
        "author": {"name": OWNER},
    }, indent=2) + "\n"


def render_marketplace_json() -> str:
    return json.dumps({
        "name": PLUGIN_NAME,
        "owner": {"name": OWNER},
        "plugins": [{
            "name": PLUGIN_NAME,
            "source": "./plugins/imperator",
            "description": PLUGIN_DESCRIPTION,
            "version": VERSION,
        }],
    }, indent=2) + "\n"


# ── Shared loading helper ────────────────────────────────────────────────────

def _role_with_groups(role_name: str, root: Path, agent: str = "claude-code"):
    """Return (role, global_groups, domain_groups) for the role's own domains."""
    role = load_roles([role_name], root)[0]
    global_groups = filter_by_agent(load_global(root), agent)
    domain_groups = filter_by_agent(load_domains(role.domains, root), agent)
    return role, global_groups, domain_groups


# ── Vercel skills bundle (export) ─────────────────────────────────────────────

def build_skills_bundle(out_dir, root: Optional[Path] = None,
                        style: str = "standard") -> list[Path]:
    """Write workflow skills (copied) + role skills (generated) as <name>/SKILL.md."""
    root = Path(root or find_root())
    out_dir = Path(out_dir)
    written: list[Path] = []

    for name in WORKFLOW_SKILLS:
        src = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        dest = out_dir / name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(src, encoding="utf-8")
        written.append(dest)

    for role_name in ROLES_AVAILABLE:
        role, global_groups, domain_groups = _role_with_groups(role_name, root)
        dest = out_dir / role_name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render_role_skill(role, global_groups, domain_groups, style),
                        encoding="utf-8")
        written.append(dest)

    return sorted(written)


# ── Claude plugin + marketplace (committed, sync-checked) ─────────────────────

def distribution_files(repo_root, style: str = "standard") -> dict[Path, str]:
    """Map every committed distribution file -> its expected content.

    Covers the repo-root marketplace, the plugin manifest, the plugin's verbatim
    workflow-skill copies, and the plugin's generated role subagents.
    """
    repo_root = Path(repo_root)
    plugin_dir = repo_root / "plugins" / "imperator"
    files: dict[Path, str] = {}

    files[repo_root / ".claude-plugin" / "marketplace.json"] = render_marketplace_json()
    files[plugin_dir / ".claude-plugin" / "plugin.json"] = render_plugin_json()

    for name in WORKFLOW_SKILLS:
        src = (repo_root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        files[plugin_dir / "skills" / name / "SKILL.md"] = src

    for role_name in ROLES_AVAILABLE:
        role, global_groups, domain_groups = _role_with_groups(role_name, repo_root)
        path = plugin_dir / "agents" / f"{role_name}.md"
        content = render_role_agent(role, global_groups, domain_groups, style)
        files[path] = add_generated_markers(path, content)

    return files


def write_distribution(repo_root, style: str = "standard") -> list[Path]:
    """(Re)write all committed distribution files. Returns written paths (sorted)."""
    files = distribution_files(repo_root, style)
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return sorted(files)


def check_distribution(repo_root, style: str = "standard") -> list[str]:
    """Return a list of human-readable drift problems (empty == in sync)."""
    repo_root = Path(repo_root)
    problems: list[str] = []
    for path, expected in distribution_files(repo_root, style).items():
        rel = path.relative_to(repo_root)
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif path.read_text(encoding="utf-8") != expected:
            problems.append(f"stale:   {rel}")
    return problems
