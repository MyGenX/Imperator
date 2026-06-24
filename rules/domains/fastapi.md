---
category: domain
domain: fastapi
affects: all-tokens
paths: ["**/*.py"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — FastAPI

**Golden path:** Pydantic models for every request/response, `async def` routes for I/O,
`Depends` for shared concerns (auth, DB sessions, settings), and explicit status codes via
`HTTPException`. Keep business logic in service functions, not in route handlers. Manage
startup/shutdown with the lifespan context and read config from a `Settings` object.

## IMP-FAS-001 · pydantic-models · required
Define request/response schemas as Pydantic models.
- Type request bodies and responses with models, not raw `dict`/`Any`.
- Validate with field types/validators rather than manual checks in the handler.

## IMP-FAS-002 · async-routes · recommended
Use `async def` for I/O routes; never block the event loop.
- Use async DB/HTTP clients; offload unavoidable sync/CPU work to a thread/executor.
```
do:    async def get(id): return await repo.fetch(id)
don't: async def get(id): return requests.get(...)  # blocks the loop
```

## IMP-FAS-003 · dependency-injection · recommended
Share cross-cutting logic via `Depends`.
- Inject DB sessions, the current user, and settings rather than duplicating setup.
- Compose dependencies; keep them small and testable.

## IMP-FAS-004 · explicit-status-codes · required
Return accurate status codes and structured errors.
- Set `status_code` on routes; raise `HTTPException` (or a handler) for errors.
- Use 201 for creates, 204 for empty responses, 4xx for client errors.

## IMP-FAS-005 · response-model · recommended
Declare `response_model` to shape output.
- Control serialization and hide internal/sensitive fields with a response schema.
- Use a separate read-model rather than returning ORM objects directly.

## IMP-FAS-006 · no-secrets-in-routes · required
Read config/secrets from settings, never hard-code.
- Use a pydantic `Settings` (env-backed) injected via `Depends`.
- Never inline tokens, keys, or connection strings in handlers.

## IMP-FAS-007 · lifespan-resources · recommended
Manage shared resources with the lifespan context.
- Open pools/clients on startup and close them on shutdown via `lifespan`.
- Don't create a new DB engine/HTTP client per request.

## IMP-FAS-008 · thin-routes-service-layer · recommended
Keep handlers thin; put logic in a service layer.
- Route parses input, calls a service, maps the result to a response.
- Business rules live in testable functions, not inside the endpoint.

## IMP-FAS-009 · background-tasks · recommended
Offload non-critical work; use a real queue for heavy jobs.
- Use `BackgroundTasks` for light post-response work (emails, audit logs).
- Use a task queue (Celery/RQ/Arq) for long, retryable, or scheduled jobs.

## IMP-FAS-010 · paginate-list-endpoints · required
Bound collection responses.
- Add `limit`/`offset` (or cursor) params with sane defaults and caps.
- Never return an unbounded result set.
