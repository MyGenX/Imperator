"""Tests for the rule-source validator and the rule-ID registry."""

import json
import shutil
from pathlib import Path

import pytest

from imperator import validator

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def rules_copy(tmp_path):
    """A writable copy of the repo's rules/ tree, returned as a fake root."""
    shutil.copytree(REPO_ROOT / "rules", tmp_path / "rules")
    return tmp_path


# ── The real repo must always be clean ───────────────────────────────────────

def test_repo_validates_clean():
    problems = validator.validate_repo(REPO_ROOT)
    errors = [p for p in problems if p.level == "error"]
    assert errors == [], "\n".join(str(p) for p in errors)


def test_repo_registry_in_sync():
    # rules/registry.json must match what the rules currently produce.
    assert validator.check_registry(REPO_ROOT) == []


def test_build_registry_shape():
    reg = validator.build_registry(REPO_ROOT)
    assert reg["count"] == len(reg["rules"])
    assert reg["count"] > 100
    sample = reg["rules"][0]
    assert set(sample) == {"id", "name", "severity", "source"}
    ids = [r["id"] for r in reg["rules"]]
    assert len(ids) == len(set(ids)), "registry should never contain duplicate IDs"


# ── Negative cases ────────────────────────────────────────────────────────────

def test_duplicate_id_detected(rules_copy):
    p = rules_copy / "rules" / "global" / "output.md"
    p.write_text(p.read_text() +
                 "\n## IMP-OUT-001 · dup · required\nbody\n", encoding="utf-8")
    problems = validator.validate_repo(rules_copy)
    assert any("duplicate rule ID 'IMP-OUT-001'" in p.message for p in problems)


def test_malformed_heading_detected(rules_copy):
    p = rules_copy / "rules" / "domains" / "python.md"
    p.write_text(p.read_text() +
                 "\n## IMP-PY-999 missing-separators required\nbody\n", encoding="utf-8")
    problems = validator.validate_repo(rules_copy)
    assert any("malformed rule heading" in p.message for p in problems)


def test_domain_requires_paths(rules_copy):
    p = rules_copy / "rules" / "domains" / "python.md"
    text = p.read_text().replace('paths: ["**/*.py"]', "paths: []")
    p.write_text(text, encoding="utf-8")
    problems = validator.validate_repo(rules_copy)
    assert any("non-empty 'paths'" in p.message for p in problems)


def test_role_unknown_domain_detected(rules_copy):
    p = rules_copy / "rules" / "roles" / "backend-developer.md"
    text = p.read_text().replace(
        "domains: [python, fastapi, postgres, api-rest]",
        "domains: [python, not-a-real-domain]")
    p.write_text(text, encoding="utf-8")
    problems = validator.validate_repo(rules_copy)
    assert any("unknown domain 'not-a-real-domain'" in p.message for p in problems)


def test_unknown_agent_detected(rules_copy):
    p = rules_copy / "rules" / "domains" / "python.md"
    text = p.read_text().replace(
        "agents: [claude-code, cursor, codex, gemini]",
        "agents: [claude-code, bogus-agent]")
    p.write_text(text, encoding="utf-8")
    problems = validator.validate_repo(rules_copy)
    assert any("unknown agent 'bogus-agent'" in p.message for p in problems)


def test_registry_drift_detected(rules_copy):
    # Write a registry, then mutate a rule so the live build no longer matches.
    validator.write_registry(rules_copy)
    assert validator.check_registry(rules_copy) == []
    p = rules_copy / "rules" / "global" / "output.md"
    p.write_text(p.read_text() +
                 "\n## IMP-OUT-050 · extra · optional\nbody\n", encoding="utf-8")
    drift = validator.check_registry(rules_copy)
    assert drift and "out of sync" in drift[0].message


def test_write_registry_roundtrip(rules_copy):
    path = validator.write_registry(rules_copy)
    assert path.name == "registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == validator.build_registry(rules_copy)
