"""
Imperator compile engine.

Single source of truth for:
  - locating the Imperator rule repository
  - parsing compact rule files into structured Rule objects
  - resolving profiles and extensions
  - rendering rules into agent-specific files (compact or full-frontmatter style)
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

VERSION = "0.1.0"

# ── Static configuration ────────────────────────────────────────────────────

CORE_ORDER = ["output", "investigation", "processing", "behavior", "safety"]

EXTENSIONS_AVAILABLE = [
    "nextjs", "react", "typescript",
    "python", "fastapi", "postgres",
    "docker", "api-rest",
]

PROFILES = {
    "fullstack-js": ["nextjs", "react", "typescript", "postgres"],
    "python-api": ["python", "fastapi", "postgres", "api-rest"],
    "minimal": [],
}

# agent -> (output filename, jinja template)
AGENTS = {
    "claude-code": ("CLAUDE.md", "claude-code.j2"),
    "cursor": (".cursorrules", "cursor.j2"),
    "codex": ("AGENTS.md", "codex.j2"),
    "gemini": ("GEMINI.md", "gemini.j2"),
}

STYLES = ["compact", "full"]

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# `##  IMP-OUT-001 · no-preamble · required`
_RULE_HEADING = re.compile(
    r"^##\s+(?P<id>IMP-[A-Z]+-\d+)\s+·\s+(?P<name>[a-z0-9-]+)\s+·\s+"
    r"(?P<severity>required|recommended|optional)\s*$"
)


# ── Data model ───────────────────────────────────────────────────────────────

@dataclass
class Rule:
    id: str
    name: str
    severity: str
    category: str
    affects: str
    agents: list[str]
    body: str


@dataclass
class RuleGroup:
    title: str           # the file's H1, e.g. "Imperator — Output Rules"
    category: str
    source: str          # "core" or extension name
    rules: list[Rule] = field(default_factory=list)


# ── Repository discovery ─────────────────────────────────────────────────────

def find_root() -> Path:
    """Locate the Imperator rule repository.

    Order: $IMPERATOR_DIR, then ~/.imperator, then walk up from this file (so the
    package works when run straight from a checkout).
    """
    env = os.environ.get("IMPERATOR_DIR")
    if env and (Path(env) / "core").is_dir():
        return Path(env)

    home = Path.home() / ".imperator"
    if (home / "core").is_dir():
        return home

    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "core").is_dir() and (parent / "extensions").is_dir():
            return parent

    raise FileNotFoundError(
        "Could not locate the Imperator rules. Set IMPERATOR_DIR or run from a checkout."
    )


# ── Parsing ──────────────────────────────────────────────────────────────────

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a minimal leading `--- ... ---` YAML-ish block. Returns (meta, rest)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    rest = text[end + 4:].lstrip("\n")

    meta: dict = {}
    for line in block.splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip() for v in value[1:-1].split(",") if v.strip()]
            meta[key] = items
        else:
            meta[key] = value
    return meta, rest


def parse_file(path: Path) -> RuleGroup:
    """Parse a single rule markdown file into a RuleGroup."""
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)

    category = meta.get("category", path.stem)
    affects = meta.get("affects", "unspecified")
    default_agents = meta.get("agents") or list(AGENTS.keys())

    title = path.stem
    lines = body.splitlines()

    # capture the first H1 as the group title
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break

    group = RuleGroup(title=title, category=category, source=path.stem)

    current: Optional[Rule] = None
    buffer: list[str] = []

    def flush():
        if current is not None:
            current.body = "\n".join(buffer).strip()
            group.rules.append(current)

    for line in lines:
        m = _RULE_HEADING.match(line)
        if m:
            flush()
            buffer = []
            current = Rule(
                id=m.group("id"),
                name=m.group("name"),
                severity=m.group("severity"),
                category=category,
                affects=affects,
                agents=list(default_agents),
                body="",
            )
        elif current is not None:
            buffer.append(line)
    flush()

    return group


# ── Loading & filtering ──────────────────────────────────────────────────────

def resolve_profile(profile: str) -> list[str]:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile '{profile}'. Choices: {', '.join(PROFILES)}")
    return list(PROFILES[profile])


def load_groups(extensions: list[str], root: Optional[Path] = None) -> list[RuleGroup]:
    """Load core groups (fixed order) followed by the selected extensions (in order)."""
    root = root or find_root()
    groups: list[RuleGroup] = []

    for name in CORE_ORDER:
        path = root / "core" / f"{name}.md"
        if path.is_file():
            groups.append(parse_file(path))

    seen = set()
    for ext in extensions:
        if ext in seen:
            continue
        seen.add(ext)
        path = root / "extensions" / f"{ext}.md"
        if not path.is_file():
            raise ValueError(f"Unknown extension '{ext}'.")
        groups.append(parse_file(path))

    return groups


def filter_by_agent(groups: list[RuleGroup], agent: str) -> list[RuleGroup]:
    """Drop rules that do not target the given agent; drop emptied groups."""
    out: list[RuleGroup] = []
    for g in groups:
        kept = [r for r in g.rules if agent in r.agents]
        if kept:
            out.append(RuleGroup(title=g.title, category=g.category,
                                 source=g.source, rules=kept))
    return out


# ── Rendering ────────────────────────────────────────────────────────────────

def render_rule(rule: Rule, style: str) -> str:
    if style == "full":
        fm = (
            "---\n"
            f"id: {rule.id}\n"
            f"name: {rule.name}\n"
            f"category: {rule.category}\n"
            f"affects: {rule.affects}\n"
            f"severity: {rule.severity}\n"
            f"agents: [{', '.join(rule.agents)}]\n"
            "---\n"
        )
        return f"{fm}\n### {rule.name}\n\n{rule.body}"
    # compact (default)
    return f"## {rule.id} · {rule.name} · {rule.severity}\n{rule.body}"


def render_body(groups: list[RuleGroup], style: str) -> str:
    sections: list[str] = []
    for g in groups:
        rendered = "\n\n".join(render_rule(r, style) for r in g.rules)
        sections.append(f"## {g.title}\n\n{rendered}" if style == "full"
                        else f"# {g.title}\n\n{rendered}")
    return "\n\n".join(sections)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def render(groups: list[RuleGroup], agent: str, style: str) -> str:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'. Choices: {', '.join(AGENTS)}")
    if style not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Choices: {', '.join(STYLES)}")

    _, template_name = AGENTS[agent]
    body = render_body(groups, style)
    rule_count = sum(len(g.rules) for g in groups)
    extensions = [g.source for g in groups if g.source not in CORE_ORDER]

    extensions_note = (
        f"Active extensions: {', '.join(extensions)}." if extensions
        else "Core rules only."
    )

    template = _env().get_template(template_name)
    return template.render(
        body=body,
        style=style,
        version=VERSION,
        rule_count=rule_count,
        extensions=extensions,
        extensions_note=extensions_note,
    )


def compile_to_agent(
    extensions: list[str],
    agent: str,
    style: str = "compact",
    out_dir: str | os.PathLike = ".",
    root: Optional[Path] = None,
) -> Path:
    """Compile rules and write the agent file. Returns the written path."""
    groups = load_groups(extensions, root=root)
    groups = filter_by_agent(groups, agent)
    content = render(groups, agent, style)

    filename, _ = AGENTS[agent]
    out_path = Path(out_dir) / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ── Stats ────────────────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Rough heuristic: ~4 characters per token."""
    return max(1, round(len(text) / 4))
