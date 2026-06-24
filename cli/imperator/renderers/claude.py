"""Claude Code native modular layout: .claude/CLAUDE.md + rules/ + agents/."""

from __future__ import annotations

from pathlib import Path

from ..catalog import VERSION
from ..parser import Role, RuleGroup
from .base import RenderContext, Renderer, _env, rules_block, write_file


def render_global_file(groups: list[RuleGroup], style: str) -> str:
    """Always-on global rules → .claude/rules/global.md (no `paths` frontmatter)."""
    body = rules_block(groups, style)
    return _env().get_template("claude-global.j2").render(
        version=VERSION, style=style, body=body,
        rule_count=sum(len(g.rules) for g in groups),
    )


def render_domain_file(group: RuleGroup, style: str) -> str:
    """One domain → .claude/rules/<domain>.md, path-scoped via `paths` frontmatter."""
    body = rules_block([group], style)
    return _env().get_template("claude-rule.j2").render(
        version=VERSION, style=style, body=body, domain=group.source,
        paths=group.paths, rule_count=len(group.rules),
    )


def render_role_agent(role: Role, global_groups: list[RuleGroup],
                      domain_groups: list[RuleGroup], style: str) -> str:
    """One role → .claude/agents/<role>.md subagent.

    Embeds the persona, the global rules, and the role's active domain rules
    (`role.domains ∩ selected_domains`) so the subagent is self-contained.
    """
    active = [g for g in domain_groups if g.source in role.domains]
    global_block = rules_block(global_groups, style)
    domain_block = rules_block(active, style)
    return _env().get_template("claude-agent.j2").render(
        version=VERSION, role=role, persona=role.body,
        global_block=global_block, domain_block=domain_block,
        active_domains=[g.source for g in active],
    )


def render_claude_md(domains: list[str], roles: list[str]) -> str:
    return _env().get_template("claude-md.j2").render(
        version=VERSION, domains=domains, roles=roles,
    )


class ClaudeRenderer(Renderer):
    agent = "claude-code"

    def compile(self, ctx: RenderContext) -> list[Path]:
        written: list[Path] = []
        claude_dir = ctx.out_dir / ".claude"
        rules_dir = claude_dir / "rules"
        agents_dir = claude_dir / "agents"

        write_file(claude_dir / "CLAUDE.md",
                   render_claude_md(ctx.domains, ctx.roles), written)
        write_file(rules_dir / "global.md",
                   render_global_file(ctx.global_groups, ctx.style), written)

        for g in ctx.domain_groups:
            write_file(rules_dir / f"{g.source}.md",
                       render_domain_file(g, ctx.style), written)

        for role in ctx.role_defs:
            write_file(
                agents_dir / f"{role.name}.md",
                render_role_agent(role, ctx.global_groups, ctx.domain_groups, ctx.style),
                written,
            )

        return written
