"""imperator doctor — inspect installation, config, and generated outputs."""

from __future__ import annotations

import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from .. import engine
from ..config import CONFIG_FILE, load_config
from .clean import GENERATED_DIRS, GENERATED_FILES


@dataclass
class DoctorResult:
    ok: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    detected: list[Path] = field(default_factory=list)
    missing: list[Path] = field(default_factory=list)
    stale: list[Path] = field(default_factory=list)
    extra: list[Path] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not self.errors and not self.missing and not self.stale


def _detected_agent_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for name in GENERATED_DIRS + GENERATED_FILES:
        path = root / name
        if path.exists():
            paths.append(path)
    return paths


def _generated_files_under(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in GENERATED_FILES:
        path = root / name
        if path.is_file():
            files.append(path)
    for name in GENERATED_DIRS:
        directory = root / name
        if directory.is_dir():
            files.extend(p for p in directory.rglob("*") if p.is_file())
    return files


def _is_generated(path: Path) -> bool:
    try:
        return path.is_file() and engine.is_generated_content(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return False


def _validate_config(config: dict, result: DoctorResult) -> bool:
    valid = True
    agent = config.get("agent")
    style = config.get("style")
    domains = config.get("domains", [])
    roles = config.get("roles", [])

    if agent not in engine.AGENTS:
        result.errors.append(f"Unsupported agent in {CONFIG_FILE}: {agent!r}")
        valid = False
    if style not in engine.STYLES:
        result.errors.append(f"Unsupported style in {CONFIG_FILE}: {style!r}")
        valid = False

    unknown_domains = [d for d in domains if d not in engine.DOMAINS_AVAILABLE]
    if unknown_domains:
        result.errors.append(f"Unknown domain(s) in {CONFIG_FILE}: {', '.join(unknown_domains)}")
        valid = False

    unknown_roles = [r for r in roles if r not in engine.ROLES_AVAILABLE]
    if unknown_roles:
        result.errors.append(f"Unknown role(s) in {CONFIG_FILE}: {', '.join(unknown_roles)}")
        valid = False

    if valid:
        result.ok.append(
            f"{CONFIG_FILE}: agent={agent}, style={style}, "
            f"domains={len(domains)}, roles={len(roles)}"
        )
    return valid


def run_doctor(root: str | Path = ".") -> DoctorResult:
    root = Path(root)
    result = DoctorResult()

    cli_path = shutil.which("imperator")
    if cli_path:
        result.ok.append(f"CLI: Imperator {engine.VERSION} at {cli_path}")
    else:
        result.warnings.append(f"CLI: Imperator {engine.VERSION} import works, but `imperator` is not on PATH")

    try:
        rule_root = engine.find_root()
        result.ok.append(f"Rule repo: {rule_root}")
    except Exception as exc:  # noqa: BLE001 - doctor should report the concrete failure.
        result.errors.append(f"Rule repo not found: {exc}")
        rule_root = None

    config_path = root / CONFIG_FILE
    if not config_path.is_file():
        result.errors.append(f"{CONFIG_FILE} not found")
        result.detected = _detected_agent_paths(root)
        return result

    try:
        config = load_config(root)
    except json.JSONDecodeError as exc:
        result.errors.append(f"{CONFIG_FILE} is not valid JSON: {exc}")
        result.detected = _detected_agent_paths(root)
        return result

    if not _validate_config(config, result) or rule_root is None:
        result.detected = _detected_agent_paths(root)
        return result

    with TemporaryDirectory() as tmp:
        expected = engine.compile_project(
            config.get("domains", []),
            config.get("roles", []),
            style=config.get("style", "compact"),
            out_dir=tmp,
            agent=config.get("agent", "claude-code"),
            root=rule_root,
        )
        expected_rels = {p.relative_to(tmp): p for p in expected}

        for rel, expected_path in expected_rels.items():
            actual = root / rel
            if not actual.exists():
                result.missing.append(actual)
            elif actual.read_text(encoding="utf-8") != expected_path.read_text(encoding="utf-8"):
                result.stale.append(actual)

        for actual in _generated_files_under(root):
            rel = actual.relative_to(root)
            if rel not in expected_rels and _is_generated(actual):
                result.extra.append(actual)

    if not result.missing and not result.stale:
        result.ok.append("Generated output: fresh")
    result.detected = _detected_agent_paths(root)
    return result


def _print_group(title: str, paths: list[Path]) -> None:
    if not paths:
        return
    print(f"\n{title}:")
    for path in paths:
        print(f"  - {path}")


def cmd_doctor(args) -> None:
    result = run_doctor()

    for item in result.ok:
        print(f"✓ {item}")
    for item in result.warnings:
        print(f"! {item}")
    for item in result.errors:
        print(f"✗ {item}")

    _print_group("Missing generated files", result.missing)
    _print_group("Stale generated files", result.stale)
    _print_group("Extra generated files", result.extra)
    _print_group("Detected agent files", result.detected)

    if not result.healthy:
        sys.exit(1)
