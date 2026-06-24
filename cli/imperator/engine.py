"""
Imperator compile engine.

Single source of truth for:
  - locating the Imperator rule repository (rules/{global,domains,roles})
  - parsing compact rule files into structured Rule objects
  - parsing role files into Role (subagent) objects
  - resolving profiles and domains
  - rendering modular native layouts for each supported agent
"""

from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

VERSION = "0.3.0"
MARKER_BEGIN = "imperator:begin generated"
MARKER_END = "imperator:end generated"

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

AGENTS = ["claude-code", "cursor", "codex", "gemini"]

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
    default_agents = meta.get("agents") or list(AGENTS)
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


def _env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=()),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["toml_string"] = json.dumps
    return env


def estimate_tokens(text: str) -> int:
    """Rough heuristic: ~4 characters per token."""
    return max(1, round(len(text) / 4))


def _generated_comment(agent: str, style: str) -> str:
    return f"<!-- Generated by Imperator v{VERSION} for {agent} · style: {style} · do not edit by hand -->"


def has_generated_marker(text: str) -> bool:
    return MARKER_BEGIN in text and MARKER_END in text


def has_legacy_generated_marker(text: str) -> bool:
    return "Generated by Imperator" in text


def is_generated_content(text: str) -> bool:
    return has_generated_marker(text) or has_legacy_generated_marker(text)


def _marker_comments(path: Path) -> tuple[str, str]:
    if path.suffix == ".toml":
        return f"# {MARKER_BEGIN}", f"# {MARKER_END}"
    return f"<!-- {MARKER_BEGIN} -->", f"<!-- {MARKER_END} -->"


def _split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        return "", content
    end = content.find("\n---", 4)
    if end == -1:
        return "", content
    after = end + len("\n---")
    if after < len(content) and content[after] == "\n":
        after += 1
    return content[:after], content[after:]


def add_generated_markers(path: Path, content: str) -> str:
    """Wrap generated content in ownership markers without breaking frontmatter."""
    if has_generated_marker(content):
        return content
    begin, end = _marker_comments(path)
    prefix, body = _split_frontmatter(content)
    body = body.strip("\n")
    return f"{prefix}{begin}\n{body}\n{end}\n"


def render_markdown_rule_module(groups: list[RuleGroup], style: str,
                                agent: str, title: str) -> str:
    body = _rules_block(groups, style)
    return f"{_generated_comment(agent, style)}\n# {title}\n\n{body}\n"


def _role_instruction_doc(role: Role, global_groups: list[RuleGroup],
                          domain_groups: list[RuleGroup], style: str,
                          agent: str) -> str:
    active = [g for g in domain_groups if g.source in role.domains]
    global_block = _rules_block(global_groups, style)
    domain_block = _rules_block(active, style)
    parts = [
        _generated_comment(agent, style),
        role.body,
        "Imperator global rules and active domain rules are embedded below. "
        "Follow them for all delegated work.",
        "# Imperator Global Rules",
        global_block,
    ]
    if domain_block:
        suffix = f" ({', '.join(g.source for g in active)})" if active else ""
        parts.extend([f"# Active Domain Rules{suffix}", domain_block])
    return "\n\n".join(parts).strip() + "\n"


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


# ── Rendering: modular Codex layout ──────────────────────────────────────────

def render_codex_agents_md(global_groups: list[RuleGroup],
                           domain_groups: list[RuleGroup],
                           style: str, domains: list[str],
                           roles: list[str]) -> str:
    """Project instructions → AGENTS.md for Codex.

    Codex discovers AGENTS.md files by directory, so active domain rules are
    embedded here instead of emitted as Claude-style glob-scoped rule files.
    """
    global_block = _rules_block(global_groups, style)
    domain_block = _rules_block(domain_groups, style)
    return _env().get_template("codex-agents-md.j2").render(
        version=VERSION, style=style, global_block=global_block,
        domain_block=domain_block, domains=domains, roles=roles,
        global_rule_count=sum(len(g.rules) for g in global_groups),
        domain_rule_count=sum(len(g.rules) for g in domain_groups),
    )


def render_codex_agent(role: Role, global_groups: list[RuleGroup],
                       domain_groups: list[RuleGroup], style: str) -> str:
    """One role → .codex/agents/<role>.toml custom agent."""
    instructions = _role_instruction_doc(role, global_groups, domain_groups, style, "codex")
    return _env().get_template("codex-agent.j2").render(
        version=VERSION, role=role, instructions=instructions,
    )


# ── Rendering: modular Cursor layout ─────────────────────────────────────────

def render_cursor_rule_file(groups: list[RuleGroup], style: str, *,
                            title: str, description: str,
                            globs: Optional[list[str]] = None,
                            always_apply: bool = False) -> str:
    body = _rules_block(groups, style)
    return _env().get_template("cursor-rule.mdc.j2").render(
        version=VERSION, style=style, title=title, description=description,
        globs=globs or [], always_apply=always_apply, body=body,
    )


def render_cursor_role_rule(role: Role, global_groups: list[RuleGroup],
                            domain_groups: list[RuleGroup], style: str) -> str:
    body = _role_instruction_doc(role, global_groups, domain_groups, style, "cursor")
    return _env().get_template("cursor-role.mdc.j2").render(
        version=VERSION, role=role, body=body,
    )


# ── Rendering: modular Gemini layout ─────────────────────────────────────────

def render_gemini_md(domains: list[str], roles: list[str]) -> str:
    return _env().get_template("gemini-md.j2").render(
        version=VERSION, domains=domains, roles=roles,
    )


def render_gemini_command(role: Role) -> str:
    return _env().get_template("gemini-command.toml.j2").render(
        version=VERSION, role=role,
    )


# ── Project compile (the main entry point) ───────────────────────────────────

def compile_project(domains, roles, style="compact", out_dir=".",
                    agent="claude-code", root=None):
    """Compile a project's ruleset.

    Writes the selected agent's native modular layout.
    Returns a list of written Paths.
    """
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'. Choices: {', '.join(AGENTS)}")

    out_dir = Path(out_dir)
    root = root or find_root()

    global_groups = filter_by_agent(load_global(root), agent)
    domain_groups = filter_by_agent(load_domains(domains, root), agent)
    role_defs = load_roles(roles, root)

    if agent == "claude-code":
        return _compile_claude(out_dir, domains, role_defs, global_groups, domain_groups, style)
    if agent == "cursor":
        return _compile_cursor(out_dir, role_defs, global_groups, domain_groups, style)
    if agent == "codex":
        return _compile_codex(out_dir, domains, role_defs, global_groups, domain_groups, style)
    if agent == "gemini":
        return _compile_gemini(out_dir, domains, role_defs, global_groups, domain_groups, style)

    raise AssertionError(f"Unhandled agent: {agent}")


def _write(path: Path, content: str, written: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(add_generated_markers(path, content), encoding="utf-8")
    written.append(path)


def _compile_claude(out_dir: Path, domains: list[str], role_defs: list[Role],
                    global_groups: list[RuleGroup], domain_groups: list[RuleGroup],
                    style: str) -> list[Path]:
    written: list[Path] = []

    claude_dir = out_dir / ".claude"
    rules_dir = claude_dir / "rules"
    agents_dir = claude_dir / "agents"

    _write(claude_dir / "CLAUDE.md", render_claude_md(domains, [r.name for r in role_defs]), written)
    _write(rules_dir / "global.md", render_global_file(global_groups, style), written)

    for g in domain_groups:
        _write(rules_dir / f"{g.source}.md", render_domain_file(g, style), written)

    for role in role_defs:
        _write(
            agents_dir / f"{role.name}.md",
            render_role_agent(role, global_groups, domain_groups, style),
            written,
        )

    return written


def _compile_cursor(out_dir: Path, role_defs: list[Role],
                    global_groups: list[RuleGroup], domain_groups: list[RuleGroup],
                    style: str) -> list[Path]:
    written: list[Path] = []
    rules_dir = out_dir / ".cursor" / "rules"

    _write(
        rules_dir / "global.mdc",
        render_cursor_rule_file(
            global_groups, style,
            title="Imperator Global Rules",
            description="Always-on Imperator rules for this repository.",
            always_apply=True,
        ),
        written,
    )

    for g in domain_groups:
        _write(
            rules_dir / "domains" / f"{g.source}.mdc",
            render_cursor_rule_file(
                [g], style,
                title=f"Imperator Domain Rules: {g.source}",
                description=f"Imperator {g.source} domain rules for matching files.",
                globs=g.paths,
            ),
            written,
        )

    for role in role_defs:
        _write(
            rules_dir / "roles" / f"{role.name}.mdc",
            render_cursor_role_rule(role, global_groups, domain_groups, style),
            written,
        )

    return written


def _compile_codex(out_dir: Path, domains: list[str], role_defs: list[Role],
                   global_groups: list[RuleGroup], domain_groups: list[RuleGroup],
                   style: str) -> list[Path]:
    written: list[Path] = []
    rules_dir = out_dir / ".codex" / "rules"

    _write(
        rules_dir / "global.md",
        render_markdown_rule_module(global_groups, style, "codex", "Imperator Global Rules"),
        written,
    )
    for g in domain_groups:
        _write(
            rules_dir / "domains" / f"{g.source}.md",
            render_markdown_rule_module([g], style, "codex", f"Imperator Domain Rules: {g.source}"),
            written,
        )
    for role in role_defs:
        _write(
            rules_dir / "roles" / f"{role.name}.md",
            _role_instruction_doc(role, global_groups, domain_groups, style, "codex"),
            written,
        )

    _write(
        out_dir / "AGENTS.md",
        render_codex_agents_md(global_groups, domain_groups, style, domains, [r.name for r in role_defs]),
        written,
    )

    for role in role_defs:
        _write(
            out_dir / ".codex" / "agents" / f"{role.name}.toml",
            render_codex_agent(role, global_groups, domain_groups, style),
            written,
        )

    return written


def _compile_gemini(out_dir: Path, domains: list[str], role_defs: list[Role],
                    global_groups: list[RuleGroup], domain_groups: list[RuleGroup],
                    style: str) -> list[Path]:
    written: list[Path] = []
    rules_dir = out_dir / ".gemini" / "rules"

    _write(
        rules_dir / "global.md",
        render_markdown_rule_module(global_groups, style, "gemini", "Imperator Global Rules"),
        written,
    )
    for g in domain_groups:
        _write(
            rules_dir / "domains" / f"{g.source}.md",
            render_markdown_rule_module([g], style, "gemini", f"Imperator Domain Rules: {g.source}"),
            written,
        )
    for role in role_defs:
        _write(
            rules_dir / "roles" / f"{role.name}.md",
            _role_instruction_doc(role, global_groups, domain_groups, style, "gemini"),
            written,
        )

    _write(out_dir / "GEMINI.md", render_gemini_md(domains, [r.name for r in role_defs]), written)

    for role in role_defs:
        _write(
            out_dir / ".gemini" / "commands" / "roles" / f"{role.name}.toml",
            render_gemini_command(role),
            written,
        )

    return written
