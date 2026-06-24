"""
Imperator compile engine — backward-compatible facade.

The engine was split into focused modules:

  - ``catalog``   — version, marker constants, agent/style/profile/domain/role lists
  - ``parser``    — dataclasses + frontmatter / rule / role parsing
  - ``loader``    — repo discovery, loading, profile resolution, agent filtering
  - ``renderers`` — per-agent native-layout renderers + shared helpers
  - ``compiler``  — ``compile_project`` and renderer dispatch

This module re-exports the public names so existing imports
(``from imperator import engine``) keep working unchanged.
"""

from __future__ import annotations

from .catalog import (
    AGENTS,
    DOMAINS_AVAILABLE,
    EXTENSIONS_AVAILABLE,
    GLOBAL_ORDER,
    MARKER_BEGIN,
    MARKER_END,
    PROFILES,
    ROLES_AVAILABLE,
    STYLES,
    VERSION,
)
from .compiler import compile_project
from .loader import (
    filter_by_agent,
    find_root,
    load_domains,
    load_global,
    load_groups,
    load_roles,
    resolve_profile,
)
from .parser import (
    Role,
    Rule,
    RuleGroup,
    _parse_frontmatter,
    _RULE_HEADING,
    parse_file,
    parse_role,
)
from .renderers import (
    add_generated_markers,
    estimate_tokens,
    has_generated_marker,
    has_legacy_generated_marker,
    is_generated_content,
    render_claude_md,
    render_codex_agent,
    render_codex_agents_md,
    render_cursor_role_rule,
    render_cursor_rule_file,
    render_domain_file,
    render_gemini_command,
    render_gemini_md,
    render_global_file,
    render_markdown_rule_module,
    render_role_agent,
    render_rule,
)

__all__ = [
    # catalog
    "VERSION", "MARKER_BEGIN", "MARKER_END", "GLOBAL_ORDER", "DOMAINS_AVAILABLE",
    "EXTENSIONS_AVAILABLE", "ROLES_AVAILABLE", "PROFILES", "AGENTS", "STYLES",
    # parser
    "Rule", "RuleGroup", "Role", "parse_file", "parse_role",
    # loader
    "find_root", "resolve_profile", "load_global", "load_domains", "load_roles",
    "load_groups", "filter_by_agent",
    # rendering / markers
    "render_rule", "estimate_tokens", "render_markdown_rule_module",
    "has_generated_marker", "has_legacy_generated_marker", "is_generated_content",
    "add_generated_markers",
    "render_global_file", "render_domain_file", "render_role_agent", "render_claude_md",
    "render_cursor_rule_file", "render_cursor_role_rule",
    "render_codex_agents_md", "render_codex_agent",
    "render_gemini_md", "render_gemini_command",
    # compiler
    "compile_project",
]
