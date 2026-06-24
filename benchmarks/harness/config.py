"""Static configuration + path wiring for the benchmark harness.

Conditions, pinned models, and directory locations live here so the rest of the
harness has a single source of truth.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# ── Repo layout ──────────────────────────────────────────────────────────────

BENCHMARKS_DIR = Path(__file__).resolve().parent.parent      # benchmarks/
REPO_ROOT = BENCHMARKS_DIR.parent                            # Imperator/
CLI_DIR = REPO_ROOT / "cli"                                  # cli/ (the package)
TASKS_DIR = BENCHMARKS_DIR / "tasks"
RESULTS_DIR = BENCHMARKS_DIR / "results"
RAW_DIR = RESULTS_DIR / "raw"
REPORT_PATH = RESULTS_DIR / "results.md"

# Make the installable engine importable without installing it.
if str(CLI_DIR) not in sys.path:
    sys.path.insert(0, str(CLI_DIR))


# ── Pinned models ────────────────────────────────────────────────────────────
# Pin explicitly so results are comparable across runs. Override on the CLI.

DEFAULT_AGENT_MODEL = "claude-sonnet-4-6"   # the model Claude Code drives per task
DEFAULT_JUDGE_MODEL = "claude-opus-4-8"     # the blind LLM-as-judge

DEFAULT_REPS = 3
DEFAULT_MAX_TURNS = 40           # safety cap so a runaway run can't bill forever
DEFAULT_AGENT_TIMEOUT = 600      # seconds per single agent run


# ── Conditions ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Condition:
    """One arm of the A/B. `style=None` means no CLAUDE.md is written (control)."""
    name: str
    style: str | None        # "compact", "full", or None for control
    description: str

    @property
    def uses_rules(self) -> bool:
        return self.style is not None


CONDITIONS: dict[str, Condition] = {
    "control": Condition(
        "control", None,
        "Vanilla Claude Code — no CLAUDE.md present.",
    ),
    "imperator-compact": Condition(
        "imperator-compact", "compact",
        "Compiled Imperator ruleset, compact style.",
    ),
    "imperator-full": Condition(
        "imperator-full", "full",
        "Compiled Imperator ruleset, full per-rule frontmatter style.",
    ),
}

DEFAULT_CONDITIONS = ["control", "imperator-compact"]


@dataclass
class RunConfig:
    """Resolved configuration for a single invocation of the harness."""
    tasks: list[str]
    conditions: list[str]
    reps: int = DEFAULT_REPS
    agent_model: str = DEFAULT_AGENT_MODEL
    judge_model: str = DEFAULT_JUDGE_MODEL
    max_turns: int = DEFAULT_MAX_TURNS
    timeout: int = DEFAULT_AGENT_TIMEOUT
    judge: bool = True
    dry_run: bool = False
    extra: dict = field(default_factory=dict)
