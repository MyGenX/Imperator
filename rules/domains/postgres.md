---
category: domain
domain: postgres
affects: all-tokens
paths: ["**/*.sql", "**/migrations/**", "**/models/**"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — PostgreSQL (+ Prisma / SQLAlchemy)

**Golden path:** All schema changes via migrations; all queries parameterized (or through
the ORM). Enforce integrity in the database (`NOT NULL`, FKs, unique constraints), index
the columns you filter/join on, and wrap multi-step writes in transactions. Select only
the columns you need and avoid N+1 access patterns. Use a connection pool.

## IMP-PG-001 · parameterized-queries · required
Never build SQL from string interpolation.
- Use bound parameters or the ORM's query API for all user-influenced values.
```
do:    cur.execute("SELECT * FROM users WHERE id = %s", (id,))
don't: cur.execute(f"SELECT * FROM users WHERE id = {id}")
```

## IMP-PG-002 · migrations-only · required
Change schema only through migrations.
- Use the migration tool (Alembic/Prisma Migrate/etc.); never alter the live schema by hand.
- One logical change per migration; never edit a migration that has shipped.

## IMP-PG-003 · index-hot-columns · recommended
Index foreign keys and frequently filtered/joined columns.
- Add indexes for FKs and columns used in `WHERE`/`JOIN`/`ORDER BY` hot paths.
- Use composite indexes matching real query predicates; don't over-index write-heavy tables.

## IMP-PG-004 · transactions-for-multistep · required
Make multi-step writes atomic.
- Wrap related writes in one transaction so they commit or roll back together.
- Keep transactions short; don't do network/IO calls mid-transaction.

## IMP-PG-005 · no-select-star · recommended
Select only the columns you need.
- List explicit columns instead of `SELECT *` (stable shape, less I/O).

## IMP-PG-006 · avoid-n-plus-one · required
Don't fan out one-query-per-row.
- Use joins, `IN`, or eager loading (`include` / `selectinload`/`joinedload`).
- Watch ORM lazy relationships inside loops.

## IMP-PG-007 · enforce-constraints · required
Put integrity rules in the schema, not just app code.
- Use `NOT NULL`, `UNIQUE`, `CHECK`, and foreign keys with deliberate `ON DELETE` behavior.
- Let the database be the last line of defense for data correctness.

## IMP-PG-008 · connection-pooling · required
Use a connection pool; don't connect per request.
- Configure a pool (app pool or PgBouncer) with sane size/timeouts.
- Always release/return connections (context managers / session scope).

## IMP-PG-009 · explain-slow-queries · recommended
Validate query plans for hot or slow paths.
- Use `EXPLAIN (ANALYZE)` to confirm indexes are used and avoid seq scans on big tables.

## IMP-PG-010 · safe-migrations · recommended
Write migrations that don't lock prod.
- Prefer additive, backward-compatible steps; backfill in batches.
- Create indexes `CONCURRENTLY` on large tables; avoid long table rewrites in one shot.
