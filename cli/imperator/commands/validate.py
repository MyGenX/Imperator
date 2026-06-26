"""imperator validate — structurally check rule sources and the ID registry.

Exit codes:
  0  no errors (warnings allowed)
  1  one or more errors, or registry drift
"""

from __future__ import annotations

import sys

from .. import validator
from ..loader import find_root


def cmd_validate(args):
    root = find_root()

    if getattr(args, "write_registry", False):
        path = validator.write_registry(root)
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"✓ wrote rule-ID registry: {rel} ({validator.build_registry(root)['count']} rules)")
        # Still surface structural problems so a write can't hide a broken tree.

    problems = validator.validate_repo(root)
    if not getattr(args, "no_registry_check", False) and not getattr(args, "write_registry", False):
        problems += validator.check_registry(root)

    errors = [p for p in problems if p.level == "error"]
    warnings = [p for p in problems if p.level == "warning"]

    for p in problems:
        print(p, file=sys.stderr if p.level == "error" else sys.stdout)

    count = validator.build_registry(root)["count"]
    if errors:
        print(f"\n✗ validate: {len(errors)} error(s), {len(warnings)} warning(s) "
              f"across {count} rules", file=sys.stderr)
        sys.exit(1)

    suffix = f" ({len(warnings)} warning(s))" if warnings else ""
    print(f"\n✓ validate: {count} rules, all checks passed{suffix}")
