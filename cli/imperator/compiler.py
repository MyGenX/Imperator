"""Project compilation: load rules, then dispatch to the agent's renderer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .catalog import AGENTS
from .loader import filter_by_agent, find_root, load_domains, load_global, load_roles
from .renderers import RENDERERS, RenderContext
from .renderers.commands import write_agent_commands


def compile_project(domains, roles, style="compact", out_dir=".",
                    agent="claude-code", root: Optional[Path] = None):
    """Compile a project's ruleset into the selected agent's native modular layout.

    Returns the list of written Paths.
    """
    if agent not in AGENTS:
        raise ValueError(f"Unknown agent '{agent}'. Choices: {', '.join(AGENTS)}")

    root = root or find_root()

    global_groups = filter_by_agent(load_global(root), agent)
    domain_groups = filter_by_agent(load_domains(domains, root), agent)
    role_defs = load_roles(roles, root)

    ctx = RenderContext(
        out_dir=Path(out_dir),
        domains=list(domains),
        roles=[r.name for r in role_defs],
        role_defs=role_defs,
        global_groups=global_groups,
        domain_groups=domain_groups,
        style=style,
    )
    written = RENDERERS[agent].compile(ctx)
    written += write_agent_commands(agent, ctx.out_dir, root)
    return written
