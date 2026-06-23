---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — Python

## IMP-PY-001 · type-hints · required
Add type hints to function signatures and public APIs.

## IMP-PY-002 · follow-pep8 · required
Follow PEP 8 and the project's formatter (black/ruff). Match existing line length.

## IMP-PY-003 · no-bare-except · required
Never use a bare `except:`. Catch specific exceptions.

## IMP-PY-004 · pathlib-over-os · recommended
Use `pathlib.Path` for filesystem paths instead of string concatenation or `os.path`.

## IMP-PY-005 · f-strings · recommended
Use f-strings for formatting; avoid `%` and `.format()` in new code.

## IMP-PY-006 · context-managers · required
Use context managers (`with`) for files, locks, and connections.
