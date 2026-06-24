"""Deterministic metrics extracted from a RawRun.

Everything here is objective and parsed straight from the stream-json transcript,
the resulting git diff, and the task verifier — no model judgement involved.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from .runner import RawRun, _git
from .spec import Task

_CODE_FENCE = re.compile(r"```")


@dataclass
class Metrics:
    ok: bool                      # did the run execute at all
    error: str | None

    # tokens (from the final result usage event)
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    total_tokens: int = 0

    # tool usage
    tool_calls: int = 0
    read_calls: int = 0
    bytes_read: int = 0
    tool_breakdown: dict = None

    # edit footprint (git numstat vs. baseline)
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0

    # behavior proxies
    preamble_chars: int = 0       # text before first code fence in first reply
    num_turns: int = 0

    # outcome
    correct: bool | None = None   # None == no verifier
    latency_ms: int = 0

    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def _content_blocks(event: dict) -> list[dict]:
    msg = event.get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        return content
    return []


def _text_of(block: dict) -> str:
    if isinstance(block, dict) and block.get("type") == "text":
        return block.get("text", "") or ""
    return ""


def _tool_result_text(block: dict) -> str:
    """Extract text length of a tool_result block (content can be str or list)."""
    content = block.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            (c.get("text", "") if isinstance(c, dict) else str(c)) for c in content
        )
    return ""


def _parse_transcript(events: list[dict]) -> dict:
    tool_calls = 0
    read_calls = 0
    bytes_read = 0
    breakdown: dict[str, int] = {}
    tool_names: dict[str, str] = {}     # tool_use_id -> name
    preamble_chars = 0
    seen_first_text = False

    result_event = None

    for ev in events:
        etype = ev.get("type")
        if etype == "assistant":
            for block in _content_blocks(ev):
                btype = block.get("type")
                if btype == "text" and not seen_first_text:
                    text = block.get("text", "") or ""
                    if text.strip():
                        seen_first_text = True
                        m = _CODE_FENCE.search(text)
                        preamble_chars = m.start() if m else len(text.strip())
                elif btype == "tool_use":
                    tool_calls += 1
                    name = block.get("name", "?")
                    breakdown[name] = breakdown.get(name, 0) + 1
                    tool_names[block.get("id", "")] = name
                    if name == "Read":
                        read_calls += 1
        elif etype == "user":
            for block in _content_blocks(ev):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    tuid = block.get("tool_use_id", "")
                    if tool_names.get(tuid) == "Read":
                        bytes_read += len(_tool_result_text(block))
        elif etype == "result":
            result_event = ev

    return {
        "tool_calls": tool_calls,
        "read_calls": read_calls,
        "bytes_read": bytes_read,
        "tool_breakdown": breakdown,
        "preamble_chars": preamble_chars,
        "result_event": result_event,
    }


def _diff_stats(workdir: Path) -> tuple[int, int, int]:
    """files_changed, lines_added, lines_deleted vs. the committed baseline."""
    proc = _git(workdir, "diff", "HEAD", "--numstat")
    files = added = deleted = 0
    for line in proc.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        files += 1
        a, d, _ = parts
        added += int(a) if a.isdigit() else 0
        deleted += int(d) if d.isdigit() else 0
    # untracked new files also count as changes
    untracked = _git(workdir, "ls-files", "--others", "--exclude-standard")
    files += len([l for l in untracked.stdout.splitlines() if l.strip()])
    return files, added, deleted


def _run_verifier(task: Task, workdir: Path) -> bool | None:
    if not task.has_verifier:
        return None
    proc = subprocess.run(
        ["bash", str(task.verify_script)], cwd=workdir,
        capture_output=True, text=True, timeout=300,
    )
    return proc.returncode == 0


def compute(run: RawRun, task: Task) -> Metrics:
    if run.error:
        return Metrics(ok=False, error=run.error, latency_ms=int(run.wall_seconds * 1000),
                       tool_breakdown={})

    parsed = _parse_transcript(run.events)
    res = parsed["result_event"] or {}
    usage = res.get("usage") or {}

    files, added, deleted = _diff_stats(run.workdir)

    try:
        correct = _run_verifier(task, run.workdir)
        verify_err = None
    except Exception as exc:  # noqa: BLE001
        correct, verify_err = None, str(exc)

    input_tokens = int(usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("output_tokens", 0) or 0)
    cache_read = int(usage.get("cache_read_input_tokens", 0) or 0)
    cache_creation = int(usage.get("cache_creation_input_tokens", 0) or 0)

    return Metrics(
        ok=True,
        error=verify_err,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read,
        cache_creation_tokens=cache_creation,
        total_tokens=input_tokens + output_tokens + cache_read + cache_creation,
        tool_calls=parsed["tool_calls"],
        read_calls=parsed["read_calls"],
        bytes_read=parsed["bytes_read"],
        tool_breakdown=parsed["tool_breakdown"],
        files_changed=files,
        lines_added=added,
        lines_deleted=deleted,
        preamble_chars=parsed["preamble_chars"],
        num_turns=int(res.get("num_turns", 0) or 0),
        correct=correct,
        latency_ms=int(res.get("duration_ms", run.wall_seconds * 1000) or 0),
        cost_usd=float(res.get("total_cost_usd", 0.0) or 0.0),
    )
