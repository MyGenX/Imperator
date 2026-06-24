"""Per-agent native-layout renderers + shared rendering helpers."""

from __future__ import annotations

from .base import (
    RenderContext,
    Renderer,
    add_generated_markers,
    estimate_tokens,
    generated_comment,
    has_generated_marker,
    has_legacy_generated_marker,
    is_generated_content,
    render_markdown_rule_module,
    render_rule,
    role_instruction_doc,
    rules_block,
    write_file,
)
from .claude import (
    ClaudeRenderer,
    render_claude_md,
    render_domain_file,
    render_global_file,
    render_role_agent,
)
from .cursor import CursorRenderer, render_cursor_role_rule, render_cursor_rule_file
from .codex import CodexRenderer, render_codex_agent, render_codex_agents_md
from .gemini import GeminiRenderer, render_gemini_command, render_gemini_md
from .skills import (
    build_skills_bundle,
    check_distribution,
    distribution_files,
    render_marketplace_json,
    render_plugin_json,
    render_role_skill,
    write_distribution,
)

#: agent name -> renderer instance (dispatch table used by the compiler)
RENDERERS = {
    r.agent: r
    for r in (ClaudeRenderer(), CursorRenderer(), CodexRenderer(), GeminiRenderer())
}

__all__ = [
    "RenderContext", "Renderer", "RENDERERS",
    "add_generated_markers", "estimate_tokens", "generated_comment",
    "has_generated_marker", "has_legacy_generated_marker", "is_generated_content",
    "render_markdown_rule_module", "render_rule", "role_instruction_doc",
    "rules_block", "write_file",
    "ClaudeRenderer", "render_claude_md", "render_domain_file",
    "render_global_file", "render_role_agent",
    "CursorRenderer", "render_cursor_role_rule", "render_cursor_rule_file",
    "CodexRenderer", "render_codex_agent", "render_codex_agents_md",
    "GeminiRenderer", "render_gemini_command", "render_gemini_md",
    "build_skills_bundle", "check_distribution", "distribution_files",
    "write_distribution", "render_role_skill", "render_plugin_json",
    "render_marketplace_json",
]
