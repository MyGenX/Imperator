---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — FastAPI

## IMP-FAS-001 · pydantic-models · required
Define request/response schemas with Pydantic models, not raw dicts.

## IMP-FAS-002 · async-routes · recommended
Use `async def` for routes that perform I/O. Never block the event loop with sync I/O.

## IMP-FAS-003 · dependency-injection · recommended
Use `Depends` for shared logic (auth, DB sessions) instead of duplicating it per route.

## IMP-FAS-004 · explicit-status-codes · recommended
Set explicit `status_code` and use `HTTPException` for error responses.

## IMP-FAS-005 · response-model · recommended
Declare `response_model` to control serialization and hide internal fields.

## IMP-FAS-006 · no-secrets-in-routes · required
Read secrets/config from settings/env, never hard-code them in route handlers.
