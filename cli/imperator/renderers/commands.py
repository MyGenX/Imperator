"""Per-agent native slash-command files, sourced from the `skills/` definitions.

Each command's description + body come from `skills/<name>/SKILL.md` (single source of
truth), and are rendered into each agent's native command format:

  - claude-code: `.claude/commands/<name>.md`   (markdown + `description:` frontmatter)
  - cursor:      `.cursor/commands/<name>.md`   (markdown prompt)
  - gemini:      `.gemini/commands/<name>.toml` (`description` + `prompt`)
  - codex:       `.codex/prompts/<name>.md`     (reviewable; Codex prompts are user-level)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..loader import find_root
from ..parser import _parse_frontmatter
from .base import write_file

# The slash commands surfaced inside agents (subset of the authored skills).
COMMANDS = [
    "imperator",
    "imperator-review",
    "imperator-plan",
    "imperator-rules",
    "imperator-stats",
]

# agent -> (subdirectory parts, file suffix)
_LAYOUT = {
    "claude-code": ((".claude", "commands"), ".md"),
    "cursor": ((".cursor", "commands"), ".md"),
    "gemini": ((".gemini", "commands"), ".toml"),
    "codex": ((".codex", "prompts"), ".md"),
}


def load_command(name: str, root: Path) -> tuple[str, str]:
    """Return (description, body) from skills/<name>/SKILL.md."""
    text = (root / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    return meta.get("description", "").strip(), body.strip()


def render_claude_command(description: str, body: str) -> str:
    return f"---\ndescription: {json.dumps(description)}\n---\n{body}\n"


def render_codex_prompt(description: str, body: str) -> str:
    return f"---\ndescription: {json.dumps(description)}\n---\n{body}\n"


def render_cursor_command(description: str, body: str) -> str:
    # Cursor uses the whole file as the prompt; lead with the description as context.
    return f"{description}\n\n{body}\n"


def render_gemini_command(description: str, body: str) -> str:
    return f"description = {json.dumps(description)}\nprompt = {json.dumps(body)}\n"


_RENDER = {
    "claude-code": render_claude_command,
    "cursor": render_cursor_command,
    "gemini": render_gemini_command,
    "codex": render_codex_prompt,
}


def write_agent_commands(agent: str, out_dir, root: Optional[Path] = None) -> list[Path]:
    """Write the agent's native command files. Returns the written paths."""
    if agent not in _LAYOUT:
        return []
    root = Path(root or find_root())
    out_dir = Path(out_dir)
    subparts, suffix = _LAYOUT[agent]
    render = _RENDER[agent]

    written: list[Path] = []
    for name in COMMANDS:
        description, body = load_command(name, root)
        path = out_dir.joinpath(*subparts, f"{name}{suffix}")
        write_file(path, render(description, body), written)
    return written
