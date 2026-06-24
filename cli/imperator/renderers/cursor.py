"""Cursor native modular layout: .cursor/rules/*.mdc (no flat .cursorrules)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..catalog import VERSION
from ..parser import Role, RuleGroup
from .base import (RenderContext, Renderer, _env, role_instruction_doc,
                   rules_block, write_file)


def render_cursor_rule_file(groups: list[RuleGroup], style: str, *,
                            title: str, description: str,
                            globs: Optional[list[str]] = None,
                            always_apply: bool = False) -> str:
    body = rules_block(groups, style)
    return _env().get_template("cursor-rule.mdc.j2").render(
        version=VERSION, style=style, title=title, description=description,
        globs=globs or [], always_apply=always_apply, body=body,
    )


def render_cursor_role_rule(role: Role, global_groups: list[RuleGroup],
                            domain_groups: list[RuleGroup], style: str) -> str:
    body = role_instruction_doc(role, global_groups, domain_groups, style, "cursor")
    return _env().get_template("cursor-role.mdc.j2").render(
        version=VERSION, role=role, body=body,
    )


class CursorRenderer(Renderer):
    agent = "cursor"

    def compile(self, ctx: RenderContext) -> list[Path]:
        written: list[Path] = []
        rules_dir = ctx.out_dir / ".cursor" / "rules"

        write_file(
            rules_dir / "global.mdc",
            render_cursor_rule_file(
                ctx.global_groups, ctx.style,
                title="Imperator Global Rules",
                description="Always-on Imperator rules for this repository.",
                always_apply=True,
            ),
            written,
        )

        for g in ctx.domain_groups:
            write_file(
                rules_dir / "domains" / f"{g.source}.mdc",
                render_cursor_rule_file(
                    [g], ctx.style,
                    title=f"Imperator Domain Rules: {g.source}",
                    description=f"Imperator {g.source} domain rules for matching files.",
                    globs=g.paths,
                ),
                written,
            )

        for role in ctx.role_defs:
            write_file(
                rules_dir / "roles" / f"{role.name}.mdc",
                render_cursor_role_rule(role, ctx.global_groups, ctx.domain_groups, ctx.style),
                written,
            )

        return written
