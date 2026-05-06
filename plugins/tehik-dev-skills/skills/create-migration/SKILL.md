---
name: create-migration
description: "Use when creating, reviewing, or modifying database migration scripts. Triggers on: adding/dropping/renaming columns or tables, schema changes, Flyway/Liquibase/Alembic/Prisma migration files, adding indexes or constraints, or any request involving SQL DDL. Produces idempotent, backward-compatible migrations with audit columns and proper index coverage."
---

# Create a database migration

This workflow helps create database schema changes while ensuring compatibility, idempotency (safe to run twice on error), and safety.

## Required inputs

Before starting, confirm:
- **Migration name** — used to derive the filename (e.g. `add_user_roles`, `create_orders_table`)
- **Target table(s)** — which tables are being created, altered, or dropped
- **Database system** — PostgreSQL, MySQL, SQLite, etc.
- **Migration tool** — Flyway, Liquibase, Alembic, Prisma, or other
- **Rollback expected** — does the project expect a down/undo migration alongside the forward migration?

## Step 1 — Gather context

- Look for project documentation about the database and migration conventions. Check `README.md`, `docs/`, `CONTRIBUTING.md`, existing migration files, and any rules files (`database.md`, `idempotency.md`, or similar) — but do not assume any specific filename exists.
- Determine which database is in use (PostgreSQL, MySQL, etc.) and which migration tool (Flyway, Liquibase, Alembic, Prisma, etc.).
- Identify the next migration filename or version number (e.g. `V005__add_user_roles.sql` or the appropriate timestamp) by inspecting existing migration files.
- Confirm whether a rollback/down migration is expected by the project (Flyway undo scripts, Alembic `downgrade`, Liquibase rollback).

## Step 2 — Draft the migration script

- Add the following at the top to prevent cascading outages if a lock cannot be acquired quickly (or the equivalent for the target database):

```sql
SET lock_timeout = '2s';
```

- All **DDL** (Data Definition Language) operations (CREATE, ALTER, DROP) must be **idempotent**, preferably using `IF NOT EXISTS` or `IF EXISTS` where the database engine supports it.
- Indexes must also be idempotent. Use the appropriate pattern for the target database:

```sql
-- Idempotent index creation (PostgreSQL 9.5+)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Concurrent index creation (cannot use IF NOT EXISTS before Postgres 12)
CREATE INDEX CONCURRENTLY idx_orders_user_id ON orders(user_id);
```

  `CREATE INDEX CONCURRENTLY` cannot use `IF NOT EXISTS` in older Postgres versions; wrap with a conditional when targeting those.
- The migration must preserve **backward compatibility** with the previous API version. Do not drop or change critical columns without a deprecation phase where the API supports both new and old fields.
- Add required **audit columns** to new mutable tables (`created_at`, `created_by`, `updated_at`, `updated_by`).
- Foreign-key columns must have mandatory **indexes** alongside them.
- **Adding NOT NULL columns to large tables** causes a full table rewrite (PostgreSQL pre-11) or a costly scan. Use a two-phase approach: (1) add the column as nullable, (2) backfill existing rows, (3) add the NOT NULL constraint in a follow-up migration or after the backfill completes.
- **Never** create a migration that processes large data row-by-row in a long transaction with locks. Long-running data migrations must be solved at the application level in a batched manner.

## Step 3 — Review and validate

- Present the drafted code and briefly explain:
  - Why the migration is needed.
  - Whether it blocks or locks database tables (e.g. building a large index). Use `CREATE INDEX CONCURRENTLY` when appropriate (PostgreSQL).
  - Why the solution is idempotent.
  - Whether a rollback migration is included or not, and why.
- **Wait for user confirmation** before creating any files.

## Step 4 — Create the migration

- Create the file in the correct project directory only after the user has confirmed.
- If a rollback migration is needed, create it alongside the forward migration.
- Give the user instructions to run the migration in the development environment for a test run.
