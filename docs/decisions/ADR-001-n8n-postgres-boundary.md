# ADR-001: n8n and PostgreSQL Integration Boundary

- **Status:** Proposed
- **Date:** 2026-10-24
- **Decision owners:** Project maintainer
- **Related documents:** `docs/system-architecture.md`, `docs/data-model.md`, `docs/process-design.md`

## Context

The lead-management MVP needs workflow orchestration, durable business records, duplicate protection, atomic assignment updates, reliable notification retries, and a recoverable outbox. A decision is required on whether n8n should own all logic and write directly to PostgreSQL, or whether a separate API/service should sit between the workflow and database.

## Options considered

### Option A — n8n nodes write directly to PostgreSQL

**Advantages**
- Fewest components and simplest local setup.
- Demonstrates core workflow automation skills.
- Simple reads and single-row operations are straightforward.

**Disadvantages**
- Multi-step operations spread across nodes are difficult to make atomic.
- Workflow exports can become hard to maintain if business rules and SQL are scattered.
- Repeated SQL and transaction assumptions can lead to inconsistent behavior.

### Option B — n8n plus PostgreSQL with versioned SQL functions/controlled transaction operations

**Advantages**
- Keeps orchestration in n8n and durable state in PostgreSQL.
- Allows database constraints to enforce identity and uniqueness.
- Groups multi-row invariants into explicit atomic operations.
- Avoids introducing an additional runtime service for the MVP.

**Disadvantages**
- Requires SQL discipline and tests for database functions/migrations.
- Complex logic in SQL can become harder to maintain if it grows unchecked.
- Requires careful parameter passing and least-privilege credentials.

### Option C — n8n calls a dedicated FastAPI service, which owns business logic and database access

**Advantages**
- Clear API/service boundary; easier to share logic across multiple clients.
- Python business logic and typed schemas may be easier to unit test.
- Database credentials can be kept out of n8n.

**Disadvantages**
- Adds a deployable service, API contract, health checks, logs, and another failure mode.
- More infrastructure than currently justified by the single-system MVP.
- Risks turning a workflow-automation project into an oversized application before requirements demand it.

## Decision

**Propose Option B for the MVP.**

Use n8n to orchestrate workflow stages and interact with PostgreSQL through parameterized queries for simple operations and versioned SQL functions/controlled transaction operations for atomic multi-row changes. PostgreSQL constraints are authoritative for uniqueness and referential integrity. Use a durable notification outbox so provider failures do not erase business state.

Do not attempt to simulate a transaction by placing unrelated Postgres nodes in sequence. A database transaction must be contained within a verified transaction boundary (for example, one SQL function call or a database operation that explicitly manages its transaction).

## Consequences

- Schema changes must be versioned migrations in Git.
- SQL functions/operations require unit or integration tests against PostgreSQL.
- n8n database credentials must be least-privilege and externalized.
- The outbox dispatcher must separate claim, send, and outcome persistence.
- Notification delivery cannot be assumed exactly-once; unknown outcomes require reconciliation.
- If multiple clients, richer authorization, reusable public APIs, or complex shared domain logic emerge, reassess Option C and introduce FastAPI only with an explicit ADR update.

## Revisit triggers

Revisit this decision if:
- business rules become too complex or duplicated across n8n workflows;
- several independent clients need the same API;
- database credentials should not be held by the orchestrator;
- testability/security review shows direct DB operations are insufficient;
- transaction and recovery requirements cannot be implemented cleanly with controlled SQL operations.
