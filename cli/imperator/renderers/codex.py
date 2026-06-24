"""Codex native layout.

Per Codex docs, `AGENTS.md` is the native project-guidance surface and `.codex/`
holds Codex configuration / custom-agent definitions — not arbitrary auto-loaded
rule Markdown. So active domain rules are embedded in the root `AGENTS.md`, the
`.codex/rules/` tree is emitted as reviewable generated artifacts only, and each
role becomes a `.codex/agents/<role>.toml` custom agent.

Future packaging (not generated in this phase): none beyond the above; do not
emit `.codex/config.toml`, commands, skills, or plugins here.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import VERSION
from ..parser import Role, RuleGroup
from .base import (RenderContext, Renderer, _env, render_markdown_rule_module,
                   role_instruction_doc, rules_block, write_file)


def render_codex_agents_md(global_groups: list[RuleGroup],
                           domain_groups: list[RuleGroup],
                           style: str, domains: list[str],
                           roles: list[str]) -> str:
    """Project instructions → AGENTS.md for Codex.

    Codex discovers AGENTS.md files by directory, so active domain rules are
    embedded here instead of emitted as Claude-style glob-scoped rule files.
    """
    global_block = rules_block(global_groups, style)
    domain_block = rules_block(domain_groups, style)
    return _env().get_template("codex-agents-md.j2").render(
        version=VERSION, style=style, global_block=global_block,
        domain_block=domain_block, domains=domains, roles=roles,
        global_rule_count=sum(len(g.rules) for g in global_groups),
        domain_rule_count=sum(len(g.rules) for g in domain_groups),
    )


def render_codex_agent(role: Role, global_groups: list[RuleGroup],
                       domain_groups: list[RuleGroup], style: str) -> str:
    """One role → .codex/agents/<role>.toml custom agent."""
    instructions = role_instruction_doc(role, global_groups, domain_groups, style, "codex")
    return _env().get_template("codex-agent.j2").render(
        version=VERSION, role=role, instructions=instructions,
    )


class CodexRenderer(Renderer):
    agent = "codex"

    def compile(self, ctx: RenderContext) -> list[Path]:
        written: list[Path] = []
        rules_dir = ctx.out_dir / ".codex" / "rules"

        # .codex/rules/ — reviewable generated artifacts only (not auto-loaded by Codex).
        write_file(
            rules_dir / "global.md",
            render_markdown_rule_module(ctx.global_groups, ctx.style, "codex",
                                        "Imperator Global Rules"),
            written,
        )
        for g in ctx.domain_groups:
            write_file(
                rules_dir / "domains" / f"{g.source}.md",
                render_markdown_rule_module([g], ctx.style, "codex",
                                            f"Imperator Domain Rules: {g.source}"),
                written,
            )
        for role in ctx.role_defs:
            write_file(
                rules_dir / "roles" / f"{role.name}.md",
                role_instruction_doc(role, ctx.global_groups, ctx.domain_groups,
                                     ctx.style, "codex"),
                written,
            )

        # AGENTS.md — the native project guidance surface (global + active domains).
        write_file(
            ctx.out_dir / "AGENTS.md",
            render_codex_agents_md(ctx.global_groups, ctx.domain_groups, ctx.style,
                                   ctx.domains, ctx.roles),
            written,
        )

        # .codex/agents/<role>.toml — custom agents.
        for role in ctx.role_defs:
            write_file(
                ctx.out_dir / ".codex" / "agents" / f"{role.name}.toml",
                render_codex_agent(role, ctx.global_groups, ctx.domain_groups, ctx.style),
                written,
            )

        return written
