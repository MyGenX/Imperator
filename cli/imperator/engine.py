"""
Imperator compile engine.

Single source of truth for:
  - locating the Imperator rule repository (rules/{global,domains,roles})
  - parsing compact rule files into structured Rule objects
  - parsing role files into Role (subagent) objects
  - resolving profiles and domains
  - rendering the modular `.claude/` layout (rules/ + agents/) for Claude Code
  - rendering the legacy flat single-file layout for any agent
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

VERSION = "0.2.0"

# ── Static configuration ────────────────────────────────────────────────────

GLOBAL_ORDER = ["output", "investigation", "processing", "behavior", "safety"]

DOMAINS_AVAILABLE = [
    "nextjs", "react", "typescript",
    "python", "fastapi", "postgres",
    "docker", "api-rest",
]

ROLES_AVAILABLE = [
    "business-analyst", "backend-developer", "frontend-developer",
    "qa-engineer", "devops",
]

# Domain bundles for common stacks.
PROFILES = {
    "fullstack-js": ["nextjs", "react", "typescript", "postgres"],
    "python-api": ["python", "fastapi", "postgres", "api-rest"],
    "minimal": [],
}

# Legacy single-file agents: agent -> (output filename, jinja template)
AGENTS = {
    "claude-code": ("CLAUDE.md", "claude-code.j2"),
    "cursor": (".cursorrules", "cursor.j2"),
    "codex": ("AGENTS.md", "codex.j2"),
    "gemini": ("GEMINI.md", "gemini.j2"),
}

STYLES = ["compact", "full"]
LAYOUTS = ["modular", "flat"]

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
    source: str          # "global" category name or domain name
    paths: list[str] = field(default_factory=list)   # path globs for domains
    overview: str = ""   # optional preamble between the H1 and the first rule
    rules: list[Rule] = field(default_factory=list)


@dataclass
class Role:
    name: str            # e.g. "backend-developer"
    description: str
    tools: str           # comma-separated, emitted verbatim ("" = inherit all)
    model: str           # sonnet/opus/haiku/inherit/...
    domains: list[str]   # which domains this role cares about
    body: str            # persona system prompt (markdown)


# ── Repository discovery ─────────────────────────────────────────────────────

def find_root() -> Path:
    """Locate the Imperator rule repository.

    Order: $IMPERATOR_DIR, then ~/.imperator, then walk up from this file (so the
    package works when run straight from a checkout). A valid root has a `rules/`
    directory (new layout) or a legacy `core/` directory.
    """
    def is_root(p: Path) -> bool:
        return (p / "rules" / "global").is_dir() or (p / "core").is_dir()

    env = os.environ.get("IMPERATOR_DIR")
    if env and is_root(Path(env)):
        return Path(env)

    home = Path.home() / ".imperator"
    if is_root(home):
        return home

    here = Path(__file__).resolve()
    for parent in here.parents:
        if is_root(parent):
            return parent

    raise FileNotFoundError(
        "Could not locate the Imperator rules. Set IMPERATOR_DIR or run from a checkout."
    )


def _rules_dir(root: Path) -> Path:
    """Return the rules base dir, supporting both new and legacy layouts."""
    if (root / "rules" / "global").is_dir():
        return root / "rules"
    return root  # legacy: core/ and extensions/ at top level


# ── Frontmatter parsing ──────────────────────────────────────────────────────

def _split_inline_list(inner: str) -> list[str]:
    """Split a comma-separated inline list, ignoring commas inside quotes or braces.

    So `"**/*.{ts,tsx}", "lib/**"` -> ['**/*.{ts,tsx}', 'lib/**'].
    """
    items: list[str] = []
    buf = ""
    depth = 0
    quote = ""
    for ch in inner:
        if quote:
            buf += ch
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch in "{[(":
            depth += 1
            buf += ch
        elif ch in "}])":
            depth = max(0, depth - 1)
            buf += ch
        elif ch == "," and depth == 0:
            items.append(buf)
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(buf)
    return [v.strip().strip("\"'") for v in items if v.strip()]


def _parse_scalar(value: str):
    """Inline list `[a, b]` -> list; otherwise the stripped string."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return _split_inline_list(value[1:-1])
    return value.strip('"\'')


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a leading `--- ... ---` YAML-ish block. Returns (meta, rest).

    Handles: `key: scalar`, `key: [a, b]` inline lists, folded/literal scalars
    (`key: >-`, `>`, `|` followed by indented lines), and block lists
    (`key:` followed by `  - item` lines).
    """
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    rest = text[end + 4:].lstrip("\n")

    meta: dict = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()

        # folded/literal scalar: collect indented continuation lines
        if value in (">", ">-", "|", "|-"):
            collected = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                if lines[i].strip():
                    collected.append(lines[i].strip())
                i += 1
            meta[key] = " ".join(collected)
            continue

        # block list: `key:` then `  - item` lines
        if value == "":
            items = []
            j = i + 1
            while j < len(lines) and lines[j].lstrip().startswith("- "):
                items.append(lines[j].lstrip()[2:].strip().strip('"\''))
                j += 1
            if items:
                meta[key] = items
                i = j
                continue
            meta[key] = ""
            i += 1
            continue

        meta[key] = _parse_scalar(value.split("  #", 1)[0])
        i += 1
    return meta, rest


# ── Rule file parsing ────────────────────────────────────────────────────────

def parse_file(path: Path) -> RuleGroup:
    """Parse a single rule markdown file into a RuleGroup."""
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)

    category = meta.get("category", path.stem)
    affects = meta.get("affects", "unspecified")
    default_agents = meta.get("agents") or list(AGENTS.keys())
    paths = meta.get("paths") or []
    if isinstance(paths, str):
        paths = [paths] if paths else []
    source = meta.get("domain", path.stem)

    title = path.stem
    lines = body.splitlines()
    title_idx = -1
    for idx, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            title_idx = idx
            break

    # Overview: everything between the H1 and the first rule heading.
    overview_lines: list[str] = []
    for line in lines[title_idx + 1:]:
        if _RULE_HEADING.match(line):
            break
        overview_lines.append(line)
    overview = "\n".join(overview_lines).strip()

    group = RuleGroup(title=title, category=category, source=source,
                      paths=list(paths), overview=overview)

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


def parse_role(path: Path) -> Role:
    """Parse a role markdown file into a Role (subagent definition)."""
    text = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(text)
    domains = meta.get("domains") or []
    if isinstance(domains, str):
        domains = [domains] if domains else []
    return Role(
        name=meta.get("role", path.stem),
        description=meta.get("description", "").strip(),
        tools=meta.get("tools", "").strip(),
        model=meta.get("model", "inherit").strip() or "inherit",
        domains=list(domains),
        body=body.strip(),
    )


# ── Loading & filtering ──────────────────────────────────────────────────────

def resolve_profile(profile: str) -> list[str]:
    if profile not in PROFILES:
        raise ValueError(f"Unknown profile '{profile}'. Choices: {', '.join(PROFILES)}")
    return list(PROFILES[profile])


def load_global(root: Optional[Path] = None) -> list[RuleGroup]:
    """Load the always-on global rule groups in fixed order."""
    root = root or find_root()
    base = _rules_dir(root)
    global_dir = base / "global" if (base / "global").is_dir() else base / "core"
    groups: list[RuleGroup] = []
    for name in GLOBAL_ORDER:
        path = global_dir / f"{name}.md"
        if path.is_file():
            groups.append(parse_file(path))
    return groups


def load_domains(domains: list[str], root: Optional[Path] = None) -> list[RuleGroup]:
    """Load the selected domain rule groups (in order, de-duplicated)."""
    root = root or find_root()
    base = _rules_dir(root)
    domain_dir = base / "domains" if (base / "domains").is_dir() else base / "extensions"
    groups: list[RuleGroup] = []
    seen = set()
    for dom in domains:
        if dom in seen:
            continue
        seen.add(dom)
        path = domain_dir / f"{dom}.md"
        if not path.is_file():
            raise ValueError(f"Unknown domain '{dom}'.")
        groups.append(parse_file(path))
    return groups


def load_roles(roles: list[str], root: Optional[Path] = None) -> list[Role]:
    """Load the selected role definitions (in order, de-duplicated)."""
    root = root or find_root()
    base = _rules_dir(root)
    role_dir = base / "roles"
    out: list[Role] = []
    seen = set()
    for r in roles:
        if r in seen:
            continue
        seen.add(r)
        path = role_dir / f"{r}.md"
        if not path.is_file():
            raise ValueError(f"Unknown role '{r}'.")
        out.append(parse_role(path))
    return out


# Back-compat: old API names used elsewhere (tests, benchmarks).
EXTENSIONS_AVAILABLE = DOMAINS_AVAILABLE


def load_groups(extensions: list[str], root: Optional[Path] = None) -> list[RuleGroup]:
    """Legacy: global groups followed by the selected domains."""
    return load_global(root) + load_domains(extensions, root)


def filter_by_agent(groups: list[RuleGroup], agent: str) -> list[RuleGroup]:
    """Drop rules that do not target the given agent; drop emptied groups."""
    out: list[RuleGroup] = []
    for g in groups:
        kept = [r for r in g.rules if agent in r.agents]
        if kept:
            out.append(RuleGroup(title=g.title, category=g.category, source=g.source,
                                 paths=list(g.paths), overview=g.overview, rules=kept))
    return out


# ── Rendering: rules ─────────────────────────────────────────────────────────

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
    return f"## {rule.id} · {rule.name} · {rule.severity}\n{rule.body}"


def _rules_block(groups: list[RuleGroup], style: str) -> str:
    sections: list[str] = []
    for g in groups:
        rendered = "\n\n".join(render_rule(r, style) for r in g.rules)
        header = f"## {g.title}" if style == "full" else f"# {g.title}"
        parts = [header]
        if g.overview:
            parts.append(g.overview)
        parts.append(rendered)
        sections.append("\n\n".join(parts))
    return "\n\n".join(sections)


# Legacy flat body (kept for the single-file templates).
def render_body(groups: list[RuleGroup], style: str) -> str:
    return _rules_block(groups, style)


def _env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )


def estimate_tokens(text: str) -> int:
    """Rough heuristic: ~4 characters per token."""
    return max(1, round(len(text) / 4))


# ── Rendering: modular .claude/ layout ───────────────────────────────────────

def render_global_file(groups: list[RuleGroup], style: str) -> str:
    """Always-on global rules → .claude/rules/global.md (no `paths` frontmatter)."""
    body = _rules_block(groups, style)
    return _env().get_template("claude-global.j2").render(
        version=VERSION, style=style, body=body,
        rule_count=sum(len(g.rules) for g in groups),
    )


def render_domain_file(group: RuleGroup, style: str) -> str:
    """One domain → .claude/rules/<domain>.md, path-scoped via `paths` frontmatter."""
    body = _rules_block([group], style)
    return _env().get_template("claude-rule.j2").render(
        version=VERSION, style=style, body=body, domain=group.source,
        paths=group.paths, rule_count=len(group.rules),
    )


def render_role_agent(role: Role, global_groups: list[RuleGroup],
                      domain_groups: list[RuleGroup], style: str) -> str:
    """One role → .claude/agents/<role>.md subagent.

    Embeds the persona, the global rules, and the role's active domain rules
    (`role.domains ∩ selected_domains`) so the subagent is self-contained.
    """
    active = [g for g in domain_groups if g.source in role.domains]
    global_block = _rules_block(global_groups, style)
    domain_block = _rules_block(active, style)
    return _env().get_template("claude-agent.j2").render(
        version=VERSION, role=role, persona=role.body,
        global_block=global_block, domain_block=domain_block,
        active_domains=[g.source for g in active],
    )


def render_claude_md(domains: list[str], roles: list[str]) -> str:
    return _env().get_template("claude-md.j2").render(
        version=VERSION, domains=domains, roles=roles,
    )


# ── Rendering: legacy flat single file ───────────────────────────────────────

def render(groups: list[RuleGroup], agent: str, style: str) -> str:
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'. Choices: {', '.join(AGENTS)}")
    if style not in STYLES:
        raise ValueError(f"Unknown style '{style}'. Choices: {', '.join(STYLES)}")

    _, template_name = AGENTS[agent]
    body = render_body(groups, style)
    rule_count = sum(len(g.rules) for g in groups)
    extensions = [g.source for g in groups if g.source not in GLOBAL_ORDER]

    extensions_note = (
        f"Active extensions: {', '.join(extensions)}." if extensions
        else "Core rules only."
    )

    template = _env().get_template(template_name)
    return template.render(
        body=body, style=style, version=VERSION, rule_count=rule_count,
        extensions=extensions, extensions_note=extensions_note,
    )


def compile_to_agent(extensions, agent, style="compact", out_dir=".", root=None):
    """Legacy: compile rules and write a single agent file. Returns the path."""
    groups = load_groups(extensions, root=root)
    groups = filter_by_agent(groups, agent)
    content = render(groups, agent, style)
    filename, _ = AGENTS[agent]
    out_path = Path(out_dir) / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return out_path


# ── Project compile (the main entry point) ───────────────────────────────────

def compile_project(domains, roles, style="compact", out_dir=".",
                    agent="claude-code", layout="modular", root=None):
    """Compile a project's ruleset.

    modular (claude-code): write `.claude/CLAUDE.md`, `.claude/rules/global.md`,
      `.claude/rules/<domain>.md` (path-scoped), `.claude/agents/<role>.md`.
    flat (any agent): write a single agent file (global + domains). Roles are
      ignored in flat layout (no native subagent support).

    Returns a list of written Paths.
    """
    out_dir = Path(out_dir)
    root = root or find_root()

    if layout == "flat" or agent != "claude-code":
        return [compile_to_agent(domains, agent, style=style, out_dir=out_dir, root=root)]

    global_groups = filter_by_agent(load_global(root), "claude-code")
    domain_groups = filter_by_agent(load_domains(domains, root), "claude-code")
    role_defs = load_roles(roles, root)

    claude_dir = out_dir / ".claude"
    rules_dir = claude_dir / "rules"
    agents_dir = claude_dir / "agents"
    rules_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    md = claude_dir / "CLAUDE.md"
    md.write_text(render_claude_md(domains, roles), encoding="utf-8")
    written.append(md)

    gf = rules_dir / "global.md"
    gf.write_text(render_global_file(global_groups, style), encoding="utf-8")
    written.append(gf)

    for g in domain_groups:
        df = rules_dir / f"{g.source}.md"
        df.write_text(render_domain_file(g, style), encoding="utf-8")
        written.append(df)

    if role_defs:
        agents_dir.mkdir(parents=True, exist_ok=True)
        for role in role_defs:
            af = agents_dir / f"{role.name}.md"
            af.write_text(
                render_role_agent(role, global_groups, domain_groups, style),
                encoding="utf-8",
            )
            written.append(af)

    return written
