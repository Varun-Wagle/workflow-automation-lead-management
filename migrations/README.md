# Database Migration Workflow

**Project ID:** WA-001  
**Status:** Initial migration convention — proposed, not yet executed  
**Last updated:** 2026-10-24

## 1. Purpose

Store schema changes as ordered SQL migration files so a fresh database can be built reproducibly and later changes can be reviewed in Git.

## 2. Directory convention

```text
migrations/
  README.md
  001_create_submissions.sql
```

New migration files use the next zero-padded sequence and a short snake_case description, for example `002_create_contacts.sql`. Once a migration has been applied to any shared or persistent environment, do not edit it; add a new migration to change the schema.

## 3. Initial migration

`001_create_submissions.sql` creates:
- `schema_migrations`: records successfully applied migration versions;
- `submissions`: the durable record of each inbound source event;
- a unique constraint on `(source, source_event_key)`;
- check constraints for normalized source, event-key length, SHA-256 fingerprint shape, allowed processing status, positive schema version, and timestamp consistency;
- indexes for status-based work discovery and correlation-ID lookup.

The migration is wrapped in a transaction. The migration ledger row is inserted only in the same transaction as the schema creation, so a failed migration should not leave a recorded success.

PostgreSQL 13 or later is the initial target because the schema uses built-in `gen_random_uuid()`. No extension is required for this UUID function on the supported baseline.

## 4. Apply to a disposable development database

Run from the repository root after confirming that `DATABASE_URL` points only to a local/disposable development database:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/001_create_submissions.sql
```

On PowerShell, set the variable first:

```powershell
$env:DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/lead_automation_dev"
psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f migrations/001_create_submissions.sql
```

Replace the placeholder connection details with local credentials. Do not commit connection strings or passwords. If using Docker Compose, run the command from a host with `psql` installed or execute `psql` inside the PostgreSQL container; the exact service name depends on the eventual Compose file.

Verify the ledger and table:

```sql
SELECT version, description, applied_at
FROM schema_migrations
ORDER BY version;

\d+ submissions
```

Expected ledger entry: version `001`. The schema should include the primary key, uniqueness and check constraints, and the two indexes listed in the migration.

## 5. Migration operating rules

1. Back up data before applying migrations to any persistent environment.
2. Confirm the target database before running a migration.
3. Apply migrations in ascending order and stop on the first error.
4. Never run a migration twice as a normal workflow; check `schema_migrations` first.
5. Never use `CREATE TABLE IF NOT EXISTS` to hide unexpected schema drift.
6. Do not modify an already-applied migration; create a new numbered migration.
7. Do not add destructive rollback statements to a routine forward migration. Any rollback/recovery procedure should be separately reviewed and tested against disposable data.
8. Run schema and behavior tests before connecting n8n.
9. Do not report a migration as applied or tested until the command has actually been executed against PostgreSQL.

## 6. Current limitations

This is an initial migration convention, not a full migration runner. It does not yet validate file checksums, automatically discover unapplied migrations, or manage rollback. Those features are unnecessary for the first small slice and can be introduced if migration volume or team workflow justifies them.

The current migration intentionally does not create contacts, opportunities, notification outbox tables, or foreign keys to tables that do not exist yet. Those belong in subsequent migrations.
