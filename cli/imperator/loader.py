"""Repository discovery, rule/role loading, profile resolution, agent filtering."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from .catalog import GLOBAL_ORDER, PROFILES
from .parser import RuleGroup, Role, parse_file, parse_role


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
