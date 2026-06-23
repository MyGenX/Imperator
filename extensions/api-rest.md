---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — REST API Design

## IMP-API-001 · noun-resources · required
Name endpoints after plural nouns (`/users/{id}`), not verbs (`/getUser`).

## IMP-API-002 · correct-http-methods · required
Use the right verb: GET (read), POST (create), PUT/PATCH (update), DELETE (remove).

## IMP-API-003 · meaningful-status-codes · required
Return accurate status codes (200/201/204/400/401/403/404/409/422/500), not just 200/500.

## IMP-API-004 · consistent-error-shape · recommended
Return errors in a consistent JSON shape with a code and message.

## IMP-API-005 · validate-input · required
Validate and sanitize all input at the boundary before use.

## IMP-API-006 · paginate-collections · recommended
Paginate list endpoints; never return unbounded collections.

## IMP-API-007 · version-the-api · recommended
Version the API (e.g. `/v1/`) so breaking changes don't break existing clients.
