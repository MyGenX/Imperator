---
category: domain
domain: python
affects: all-tokens
paths: ["**/*.py"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — Python

**Golden path:** Python 3.10+, fully type-hinted, formatted and linted with `ruff`
(or `black` + `ruff`). Prefer the standard library; use `pathlib` for paths, `logging`
over `print`, context managers for resources, and `dataclasses`/`pydantic` for structured
data. Keep functions small and pure where practical; push side effects to the edges.

## IMP-PY-001 · type-hints · required
Type-hint every function signature and public attribute.
- Annotate parameters and return types; use `X | None` for optionals (3.10+).
- Prefer precise types (`Sequence`, `Mapping`, `Protocol`) over bare `list`/`dict`/`Any`.
- Treat the codebase as if a type checker (`mypy`/`pyright`) runs in CI.

## IMP-PY-002 · follow-formatter · required
Match the project's formatter and linter; don't hand-format.
- Follow `ruff`/`black` output and the configured line length — don't fight it.
- Keep imports ordered/grouped (stdlib, third-party, local) as the tool expects.

## IMP-PY-003 · no-bare-except · required
Catch specific exceptions; never swallow everything.
- Catch the narrowest exception type that you can actually handle.
- Re-raise or wrap with context; never silently `pass` on an exception.
```
do:    except (KeyError, ValueError) as e: raise ConfigError(...) from e
don't: except: pass
```

## IMP-PY-004 · pathlib-over-os · recommended
Use `pathlib.Path` for filesystem work.
- Build paths with `/` and `Path` methods, not string concatenation or `os.path.join`.
- Use `Path.read_text()`/`write_text()` for simple file I/O.

## IMP-PY-005 · f-strings · recommended
Format with f-strings in new code.
- Use f-strings over `%` and `str.format()`.
- Exception: logging — use `%`-style lazy args (`logger.info("x=%s", x)`), not f-strings.

## IMP-PY-006 · context-managers · required
Manage resources with `with`.
- Wrap files, locks, sockets, and DB sessions/connections in context managers.
- Don't rely on the garbage collector to close resources.

## IMP-PY-007 · no-mutable-default-args · required
Never use a mutable default argument.
- Default to `None` and create the container inside the function.
```
do:    def f(items: list[int] | None = None): items = items or []
don't: def f(items: list[int] = []):
```

## IMP-PY-008 · structured-data-types · recommended
Model structured data with classes, not loose dicts.
- Use `@dataclass` (or `pydantic.BaseModel` at boundaries) for records passed around.
- Reserve dicts for genuinely dynamic key/value data.

## IMP-PY-009 · logging-not-print · recommended
Use `logging`, not `print`, in library/app code.
- Get a module logger (`logging.getLogger(__name__)`); choose appropriate levels.
- `print` is only for CLIs/scripts whose job is to write to stdout.

## IMP-PY-010 · docstrings-public-api · recommended
Document public modules, classes, and functions.
- One-line summary; note non-obvious args, return values, and raised exceptions.
- Skip docstrings that merely repeat the signature.

## IMP-PY-011 · comprehensions-over-loops · optional
Prefer comprehensions/generators for simple transforms.
- Use a comprehension when it stays readable; fall back to a loop when logic is complex.
- Use generators (`(... for ...)`) for large or streamed sequences to save memory.
