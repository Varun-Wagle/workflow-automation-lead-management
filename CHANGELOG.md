# Changelog

All notable project changes will be documented here.

This project uses a release-oriented changelog. Unreleased work is recorded under `Unreleased`; versioned entries are added when a release is created.

## Unreleased

### Added
- Initial repository documentation.
- Proposed system architecture for n8n/PostgreSQL, workflow boundaries, deployment, security, observability, and recovery.
- ADR-001 proposing the n8n/PostgreSQL integration boundary and deferring a separate FastAPI service.
- Draft relational data model with entity relationships, constraints, transaction boundaries, and notification outbox.
- Draft process design covering the normal lead-intake path, duplicate and ambiguity handling, assignment, notification states, failure recovery, human review, and acceptance scenarios.
- Draft business case for the fictional ApexFlow Solutions scenario.
- Decision log template.
- Safe default `.gitignore` and `.env.example`.
