"""Gemini CLI native layout: GEMINI.md + .gemini/rules/ + .gemini/commands/roles/.

Future packaging (not generated in this phase): `gemini-extension.json` extension
packaging — see the Gemini CLI extensions docs. Tracked as TODO, not emitted here.
"""

from __future__ import annotations

from pathlib import Path

from ..catalog import VERSION
from ..parser import Role
from .base import (RenderContext, Renderer, _env, render_markdown_rule_module,
                   role_instruction_doc, write_file)


def render_gemini_md(domains: list[str], roles: list[str]) -> str:
    return _env().get_template("gemini-md.j2").render(
        version=VERSION, domains=domains, roles=roles,
    )


def render_gemini_command(role: Role) -> str:
    return _env().get_template("gemini-command.toml.j2").render(
        version=VERSION, role=role,
    )


class GeminiRenderer(Renderer):
    agent = "gemini"

    def compile(self, ctx: RenderContext) -> list[Path]:
        written: list[Path] = []
        rules_dir = ctx.out_dir / ".gemini" / "rules"

        write_file(
            rules_dir / "global.md",
            render_markdown_rule_module(ctx.global_groups, ctx.style, "gemini",
                                        "Imperator Global Rules"),
            written,
        )
        for g in ctx.domain_groups:
            write_file(
                rules_dir / "domains" / f"{g.source}.md",
                render_markdown_rule_module([g], ctx.style, "gemini",
                                            f"Imperator Domain Rules: {g.source}"),
                written,
            )
        for role in ctx.role_defs:
            write_file(
                rules_dir / "roles" / f"{role.name}.md",
                role_instruction_doc(role, ctx.global_groups, ctx.domain_groups,
                                     ctx.style, "gemini"),
                written,
            )

        write_file(ctx.out_dir / "GEMINI.md",
                   render_gemini_md(ctx.domains, ctx.roles), written)

        for role in ctx.role_defs:
            write_file(
                ctx.out_dir / ".gemini" / "commands" / "roles" / f"{role.name}.toml",
                render_gemini_command(role),
                written,
            )

        return written
