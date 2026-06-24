"""imperator stats — estimate generated modular output size."""

from __future__ import annotations

from tempfile import TemporaryDirectory
from pathlib import Path

from .. import engine
from ..config import load_config


def cmd_stats(args):
    config = load_config()
    domains = config.get("domains", [])
    roles = config.get("roles", [])
    style = config.get("style", "compact")
    agent = config.get("agent", "claude-code")

    print("\n👑 Imperator — Stats\n" + "─" * 48)
    print(f"  Agent   : {agent} (modular)")
    print(f"  Style   : {style}")
    print(f"  Domains : {', '.join(domains) if domains else 'none'}")
    print(f"  Roles   : {', '.join(roles) if roles else 'none'}")
    print()

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        written = engine.compile_project(
            domains, roles, style=style, out_dir=root, agent=agent,
        )
        total = 0
        print("  Generated files:")
        for path in sorted(written):
            text = path.read_text(encoding="utf-8")
            total += len(text)
            rel = path.relative_to(root).as_posix()
            print(f"    {rel:<42} {len(text):>6} chars  ≈ "
                  f"{engine.estimate_tokens(text):>5} tokens")

    print()
    print(f"  Total generated context: {total} chars  ≈ "
          f"{engine.estimate_tokens('x' * total):>5} tokens")
    print("  Modular agents load only the native files their tool includes for a task.\n")
