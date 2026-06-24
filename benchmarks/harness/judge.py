"""LLM-as-judge scoring of a run transcript.

The judge is **blind to the condition** — it never learns whether the Imperator
ruleset was present. It scores a flattened transcript on a fixed rubric and
returns structured JSON. Requires ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from .config import RunConfig
from .runner import RawRun
from .spec import Task

_RUBRIC = """\
You are evaluating a transcript of an AI coding agent working on a single task.
Score each dimension from 1 (poor) to 5 (excellent). Be a strict, calibrated grader.

Dimensions:
- conciseness: Did the agent avoid preamble/filler and answer directly?
  5 = no filler, gets straight to work; 1 = lots of throat-clearing and restating.
- scope_adherence: Did it change ONLY what the task required, with no unrelated
  edits, reformatting, or rewrites? 5 = surgical; 1 = sprawling/off-scope changes.
- investigation: Did it read targeted files rather than scanning the whole repo?
  5 = minimal, relevant reads; 1 = indiscriminate scanning.
- clarify_when_ambiguous: If the request was underspecified, did it ask before
  building? If the request was clear, full marks for proceeding directly.
- overall_quality: Holistic judgement of whether the task was handled well.

Return ONLY a JSON object, no prose, with integer scores and a one-sentence
"notes" field:
{"conciseness": int, "scope_adherence": int, "investigation": int,
 "clarify_when_ambiguous": int, "overall_quality": int, "notes": "..."}
"""

SCORE_KEYS = [
    "conciseness", "scope_adherence", "investigation",
    "clarify_when_ambiguous", "overall_quality",
]


@dataclass
class JudgeResult:
    ok: bool
    scores: dict          # dimension -> int (and "notes")
    error: str | None = None


def flatten_transcript(run: RawRun, max_chars: int = 24000) -> str:
    """Render the stream-json events into a compact, readable transcript."""
    lines: list[str] = []
    for ev in run.events:
        etype = ev.get("type")
        msg = ev.get("message") or {}
        content = msg.get("content")
        if etype == "assistant" and isinstance(content, list):
            for b in content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    lines.append(f"ASSISTANT: {b['text'].strip()}")
                elif b.get("type") == "tool_use":
                    inp = json.dumps(b.get("input", {}))[:300]
                    lines.append(f"TOOL_CALL {b.get('name')}: {inp}")
        elif etype == "user" and isinstance(content, list):
            for b in content:
                if b.get("type") == "tool_result":
                    body = b.get("content")
                    if isinstance(body, list):
                        body = "".join(
                            c.get("text", "") for c in body if isinstance(c, dict)
                        )
                    snippet = (str(body) or "")[:200].replace("\n", " ")
                    lines.append(f"TOOL_RESULT: {snippet}")
    text = "\n".join(lines)
    if len(text) > max_chars:
        head = text[: max_chars // 2]
        tail = text[-max_chars // 2:]
        text = f"{head}\n... [transcript truncated] ...\n{tail}"
    return text


def score(run: RawRun, task: Task, cfg: RunConfig) -> JudgeResult:
    if run.error:
        return JudgeResult(ok=False, scores={}, error=f"run errored: {run.error}")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return JudgeResult(ok=False, scores={}, error="ANTHROPIC_API_KEY not set")

    try:
        import anthropic
    except ImportError:
        return JudgeResult(ok=False, scores={},
                           error="anthropic SDK not installed (pip install -r requirements.txt)")

    transcript = flatten_transcript(run)
    rubric_extra = f"\nTask-specific guidance:\n{task.rubric}\n" if task.rubric else ""
    prompt = (
        f"{_RUBRIC}{rubric_extra}\n"
        f"--- TASK GIVEN TO THE AGENT ---\n{task.prompt}\n\n"
        f"--- AGENT TRANSCRIPT ---\n{transcript}\n"
    )

    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=cfg.judge_model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    except Exception as exc:  # noqa: BLE001
        return JudgeResult(ok=False, scores={}, error=f"judge API error: {exc}")

    data = _extract_json(raw)
    if data is None:
        return JudgeResult(ok=False, scores={}, error=f"judge returned non-JSON: {raw[:200]}")
    return JudgeResult(ok=True, scores=data)


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        text = text[4:] if text.lower().startswith("json") else text
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start: end + 1])
    except json.JSONDecodeError:
        return None
