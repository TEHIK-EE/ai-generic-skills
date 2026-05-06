---
trigger: always_on
---

# DATABASE

## Migrations

* All schema changes are made **through migration files** — not manually in the database
* Migration tools: Flyway, Liquibase (Java), Alembic (Python), Prisma Migrate (Node.js), etc.
* Migration files are **under version control** together with the application code
* Migration file naming: `V<version>__<description>.sql` (e.g. `V003__add_approval_status_column.sql`)
* **Migrations must be backwards-compatible** between each release — upgrading the application and the database must be independent
* **Migrations must be idempotent** — the same script must be safe to run multiple times

```sql
-- Good: idempotent DDL statements
CREATE TABLE IF NOT EXISTS users (...);
ALTER TABLE reports ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_reports_submitted_by ON reports(submitted_by);

-- Bad: not idempotent
CREATE TABLE users (...);
ALTER TABLE reports ADD COLUMN submitted_at TIMESTAMPTZ;
```

### Backwards-compatible migration pattern

```
Release N:   Add column (nullable, with a default value)
Release N+1: Backfill data, add NOT NULL constraint
Release N+2: Drop old column (if needed)
```

## Naming conventions

* **Tables:** `snake_case`, plural, in English (`users`, `report_submissions`, `approval_events`)
* **Columns:** `snake_case`, in English (`created_at`, `submitted_by`, `is_active`)
* **Primary key:** always `id` (UUID v7 preferred — timestamp-based, sortable, better index performance; not a sequence, not UUID v4)
* **Foreign key:** `<referenced_table_singular>_id` (e.g. `user_id`, `report_id`)
* **Indexes:** `idx_<table>_<columns>` (e.g. `idx_reports_submitted_by`)
* **Constraints:** `uq_<table>_<columns>`, `fk_<table>_<referenced>`, `chk_<table>_<description>`
* **Views:** `v_<description>` (e.g. `v_pending_approvals`)

## Audit fields

Every mutable table must include:

```sql
created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
created_by  UUID        NOT NULL REFERENCES users(id),
updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
updated_by  UUID        NOT NULL REFERENCES users(id),
```

* `updated_at` is updated automatically via a trigger

```sql
-- PostgreSQL: universal updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to each table:
CREATE TRIGGER trg_<table>_updated_at
  BEFORE UPDATE ON <table>
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

## Indexes

* **Mandatory index:** on all foreign key columns
* **Recommended:** on all columns used in `WHERE`, `ORDER BY`, `GROUP BY` for frequent queries
* Before adding an index, measure query performance (`EXPLAIN ANALYZE`)
* Indexes are expensive — every update/delete updates all affected indexes

## Query optimization

* **N+1 problem:** use JOINs or ORM eager loading (`include`/`joinFetch`)
* **Pagination:** use cursor-based pagination for large datasets (not OFFSET with large values)
* **Large operations:** `bulk insert/update` in a single transaction (not in a loop one row at a time)
* **Query monitoring:** configure slow query logging in all environments

## Transactions

* All related write operations in one transaction
* Transaction scope: keep as small as possible (do not hold tables locked for long)
* Prefer optimistic locking (version column) over pessimistic (`SELECT FOR UPDATE`) where possible

## Sensitive data

* Personal data (per GDPR): identify, document, and protect
* Passwords: **never** stored in plaintext in the database (hash in the application layer)
* PII (first/last name, national ID, email): consider application-level encryption
* Database connection string password: environment variables only, not in code

## Backups

* Production database backup: at least once daily, retain for at least 30 days
* Backup restore is tested regularly (at least once per quarter)
* Point-in-time recovery (PITR) available in production

## Soft Delete vs Hard Delete

Decide at project level whether to use **soft delete** (logical deletion) or **hard delete** (physical deletion):

### Soft delete (preferred in regulatory contexts)

```sql
ALTER TABLE reports ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL;
CREATE INDEX IF NOT EXISTS idx_reports_deleted_at ON reports(deleted_at) WHERE deleted_at IS NULL;
```

* For queries on non-deleted rows, **always** add `WHERE deleted_at IS NULL`
* Use ORM global filters (e.g. Prisma middleware, Hibernate `@Where`, SQLAlchemy events)
* Unique constraints: use a partial unique index (`WHERE deleted_at IS NULL`)
* **Required** when audit trail / GDPR requirements apply

### Hard delete

* Use only when data **does not need to be retained** (e.g. temporary data, sessions)
* Use `ON DELETE CASCADE` with care — document what gets deleted

## Connection pooling

* **Always** use a connection pool — ❌ not a new connection for every query
* Pool configuration:
  * `min`: 2–5 connections (keeps connections alive)
  * `max`: 10–20 connections (depends on service load and database limits)
  * `idleTimeout`: 30s (releases idle connections)
  * `connectionTimeout`: 5s (max wait for a new connection)
* Monitor pool usage (active/waiting connections) — see `observability.md`
* **Connection leak detection:** alert when a connection is held >60s

## Data retention

* Define a **data retention policy** for each table
* GDPR: retention period for personal data must be documented and justified
* Expired data: delete automatically (cron job / scheduled task) or archive
* Log tables: rotate or archive (e.g. entries older than 90 days)

## Prohibited practices

* ❌ Manual schema changes in the production database (bypassing migrations)
* ❌ `SELECT *` in production queries — list columns explicitly
* ❌ Business logic in database triggers/procedures (except `updated_at` updates)
* ❌ Hardcoded connection strings in code
* ❌ One database user for all applications — separate users and permissions per application
* ❌ Database connections without a connection pool in production
