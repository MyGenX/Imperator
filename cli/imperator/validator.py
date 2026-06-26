"""Static validation for Imperator rule sources.

Parses the *raw* rule/role/domain files (not just the lenient loader path) so
malformed headings, missing frontmatter, duplicate IDs, and dangling references
are caught before they reach a generated agent layout. Used by both the
`imperator validate` command and CI.

Nothing here writes to the agent output tree; it only reads `rules/` and the
committed rule-ID registry.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .catalog import AGENTS, DOMAINS_AVAILABLE, GLOBAL_ORDER, ROLES_AVAILABLE, VERSION
from .loader import _rules_dir, find_root
from .parser import _RULE_HEADING, _parse_frontmatter, parse_file, parse_role

SEVERITIES = ("required", "recommended", "optional")
REGISTRY_NAME = "registry.json"

# A `## ` heading that *looks* like a rule attempt: mentions an IMP- id or uses
# the `·` separator. Used to flag malformed headings that the strict rule regex
# would otherwise silently skip.
_RULE_LIKE = re.compile(r"^##\s+(IMP-|.*\s·\s)")


@dataclass(frozen=True)
class Problem:
    level: str            # "error" or "warning"
    location: str         # e.g. "rules/domains/python.md:5"
    message: str

    def __str__(self) -> str:
        tag = "✗" if self.level == "error" else "⚠"
        return f"{tag} {self.location}: {self.message}"


@dataclass
class RuleRef:
    id: str
    name: str
    severity: str
    source: str           # "global/output", "domain/python", ...
    location: str         # path:line


# ── Collection ───────────────────────────────────────────────────────────────

def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _scan_headings(root: Path, path: Path, source: str,
                   problems: list[Problem]) -> list[RuleRef]:
    """Read a rule file line by line, returning well-formed rule refs and
    appending a problem for every malformed rule-like heading."""
    refs: list[RuleRef] = []
    rel = _rel(root, path)
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = _RULE_HEADING.match(line)
        if m:
            refs.append(RuleRef(
                id=m.group("id"), name=m.group("name"), severity=m.group("severity"),
                source=source, location=f"{rel}:{lineno}",
            ))
        elif _RULE_LIKE.match(line):
            problems.append(Problem(
                "error", f"{rel}:{lineno}",
                f"malformed rule heading; expected "
                f"'## IMP-XXX-NNN · kebab-name · {'|'.join(SEVERITIES)}': {line.strip()!r}",
            ))
    return refs


def _check_prefix_consistency(refs: list[RuleRef], source: str,
                              problems: list[Problem]) -> None:
    """All rules in one file should share a single IMP-<CAT> prefix."""
    prefixes = {r.id.rsplit("-", 1)[0] for r in refs}
    if len(prefixes) > 1:
        problems.append(Problem(
            "warning", source,
            f"file mixes rule-ID prefixes {sorted(prefixes)}; "
            "rules in one file normally share one prefix",
        ))


# ── Per-tier validation ──────────────────────────────────────────────────────

def _validate_global(base: Path, root: Path,
                     problems: list[Problem]) -> list[RuleRef]:
    refs: list[RuleRef] = []
    global_dir = base / "global"
    for name in GLOBAL_ORDER:
        path = global_dir / f"{name}.md"
        if not path.is_file():
            problems.append(Problem("error", _rel(root, global_dir),
                                    f"missing global rule file '{name}.md'"))
            continue
        meta, _ = _parse_frontmatter(path.read_text(encoding="utf-8"))
        for key in ("category", "affects", "agents"):
            if not meta.get(key):
                problems.append(Problem("error", _rel(root, path),
                                        f"missing required frontmatter key '{key}'"))
        _check_agents(meta.get("agents"), path, root, problems)
        file_refs = _scan_headings(root, path, f"global/{name}", problems)
        if not file_refs:
            problems.append(Problem("error", _rel(root, path),
                                    "no rules found in global file"))
        _check_prefix_consistency(file_refs, _rel(root, path), problems)
        refs.extend(file_refs)
    return refs


def _validate_domains(base: Path, root: Path,
                      problems: list[Problem]) -> list[RuleRef]:
    refs: list[RuleRef] = []
    domain_dir = base / "domains"
    found: set[str] = set()
    for path in sorted(domain_dir.glob("*.md")):
        stem = path.stem
        found.add(stem)
        rel = _rel(root, path)
        meta, _ = _parse_frontmatter(path.read_text(encoding="utf-8"))

        if meta.get("category") != "domain":
            problems.append(Problem("error", rel,
                                    "domain frontmatter must set 'category: domain'"))
        if meta.get("domain") != stem:
            problems.append(Problem("error", rel,
                                    f"frontmatter 'domain' ({meta.get('domain')!r}) "
                                    f"must match filename ({stem!r})"))
        if not meta.get("affects"):
            problems.append(Problem("error", rel, "missing required frontmatter 'affects'"))

        paths = meta.get("paths")
        if not paths or not isinstance(paths, list) or not any(p.strip() for p in paths):
            problems.append(Problem("error", rel,
                                    "domain must declare a non-empty 'paths' glob list"))
        _check_agents(meta.get("agents"), path, root, problems)

        if stem not in DOMAINS_AVAILABLE:
            problems.append(Problem("error", rel,
                                    f"domain '{stem}' is not registered in "
                                    "catalog.DOMAINS_AVAILABLE"))
        file_refs = _scan_headings(root, path, f"domain/{stem}", problems)
        if not file_refs:
            problems.append(Problem("error", rel, "no rules found in domain file"))
        _check_prefix_consistency(file_refs, rel, problems)
        refs.extend(file_refs)

    for missing in sorted(set(DOMAINS_AVAILABLE) - found):
        problems.append(Problem("error", _rel(root, domain_dir),
                                f"catalog lists domain '{missing}' but no "
                                f"'{missing}.md' rule file exists"))
    return refs


def _validate_roles(base: Path, root: Path, problems: list[Problem]) -> None:
    role_dir = base / "roles"
    if not role_dir.is_dir():
        return
    found: set[str] = set()
    known_domains = set(DOMAINS_AVAILABLE)
    for path in sorted(role_dir.glob("*.md")):
        stem = path.stem
        found.add(stem)
        rel = _rel(root, path)
        role = parse_role(path)
        if role.name != stem:
            problems.append(Problem("error", rel,
                                    f"frontmatter 'role' ({role.name!r}) must match "
                                    f"filename ({stem!r})"))
        if not role.description:
            problems.append(Problem("error", rel, "role missing 'description'"))
        if not role.body:
            problems.append(Problem("error", rel, "role missing a system-prompt body"))
        for dom in role.domains:
            if dom not in known_domains:
                problems.append(Problem("error", rel,
                                        f"role references unknown domain '{dom}'"))
        if stem not in ROLES_AVAILABLE:
            problems.append(Problem("error", rel,
                                    f"role '{stem}' is not registered in "
                                    "catalog.ROLES_AVAILABLE"))

    for missing in sorted(set(ROLES_AVAILABLE) - found):
        problems.append(Problem("error", _rel(root, role_dir),
                                f"catalog lists role '{missing}' but no "
                                f"'{missing}.md' file exists"))


def _check_agents(agents, path: Path, root: Path, problems: list[Problem]) -> None:
    if agents is None:
        return
    if isinstance(agents, str):
        agents = [agents]
    for a in agents:
        if a not in AGENTS:
            problems.append(Problem("error", _rel(root, path),
                                    f"unknown agent '{a}' in frontmatter "
                                    f"(known: {AGENTS})"))


# ── Public API ───────────────────────────────────────────────────────────────

def collect_rules(root: Optional[Path] = None) -> tuple[list[RuleRef], list[Problem]]:
    """Return (all rule refs, structural problems) across every tier."""
    root = root or find_root()
    base = _rules_dir(root)
    problems: list[Problem] = []
    refs: list[RuleRef] = []
    refs.extend(_validate_global(base, root, problems))
    refs.extend(_validate_domains(base, root, problems))
    _validate_roles(base, root, problems)
    return refs, problems


def _check_duplicate_ids(refs: list[RuleRef], problems: list[Problem]) -> None:
    by_id: dict[str, list[RuleRef]] = {}
    for r in refs:
        by_id.setdefault(r.id, []).append(r)
    for rid, group in sorted(by_id.items()):
        if len(group) > 1:
            locs = ", ".join(g.location for g in group)
            problems.append(Problem("error", group[0].location,
                                    f"duplicate rule ID '{rid}' (also at: {locs})"))


def validate_repo(root: Optional[Path] = None) -> list[Problem]:
    """Full structural validation: headings, frontmatter, references, duplicate IDs."""
    refs, problems = collect_rules(root)
    _check_duplicate_ids(refs, problems)
    return problems


# ── Rule-ID registry ─────────────────────────────────────────────────────────

def build_registry(root: Optional[Path] = None) -> dict:
    """Build the deterministic rule-ID registry from the current rule sources."""
    refs, _ = collect_rules(root)
    rules = sorted(
        ({"id": r.id, "name": r.name, "severity": r.severity, "source": r.source}
         for r in refs),
        key=lambda d: (d["source"], d["id"]),
    )
    return {"count": len(rules), "rules": rules}


def registry_path(root: Optional[Path] = None) -> Path:
    root = root or find_root()
    return _rules_dir(root) / REGISTRY_NAME


def write_registry(root: Optional[Path] = None) -> Path:
    root = root or find_root()
    path = registry_path(root)
    path.write_text(json.dumps(build_registry(root), indent=2) + "\n", encoding="utf-8")
    return path


def check_registry(root: Optional[Path] = None) -> list[Problem]:
    """Return a problem if the committed registry drifts from current rules."""
    root = root or find_root()
    path = registry_path(root)
    rel = _rel(root, path)
    expected = build_registry(root)
    if not path.is_file():
        return [Problem("error", rel,
                        "rule-ID registry is missing; run `imperator validate --write-registry`")]
    try:
        actual = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [Problem("error", rel, f"registry is not valid JSON: {exc}")]
    if actual != expected:
        return [Problem("error", rel,
                        "rule-ID registry is out of sync with rules; "
                        "run `imperator validate --write-registry`")]
    return []
