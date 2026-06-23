---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — PostgreSQL (+ Prisma / SQLAlchemy)

## IMP-PG-001 · parameterized-queries · required
Always use parameterized queries or the ORM. Never build SQL via string interpolation.

## IMP-PG-002 · migrations-only · required
Change schema only through migrations. Never edit the database schema manually.

## IMP-PG-003 · index-foreign-keys · recommended
Add indexes for foreign keys and columns used in frequent `WHERE`/`JOIN` clauses.

## IMP-PG-004 · transactions-for-multistep · required
Wrap multi-step writes in a transaction so they commit or roll back atomically.

## IMP-PG-005 · no-select-star · recommended
Select only the columns you need rather than `SELECT *`.

## IMP-PG-006 · avoid-n-plus-one · required
Avoid N+1 queries — use joins, `include`, or `selectinload`/`joinedload`.
