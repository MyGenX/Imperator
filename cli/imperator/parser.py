"""Parsing for Imperator rule sources.

Dataclasses (`Rule`, `RuleGroup`, `Role`), a tolerant YAML-ish frontmatter
parser, and the rule/role file parsers. No rendering or filesystem discovery
lives here — see `loader.py` and `renderers/`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .catalog import AGENTS

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


# ── Rule / role file parsing ─────────────────────────────────────────────────

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
