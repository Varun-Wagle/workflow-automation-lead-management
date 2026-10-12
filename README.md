# Lead Management & Sales Follow-up Automation

A portfolio project exploring how workflow automation can improve lead intake, qualification, assignment, acknowledgement, and follow-up for a fictional B2B SaaS company.

> **Project status:** Discovery and requirements definition  
> **Current release:** Not released  
> **Scenario:** Fictional company — ApexFlow Solutions

## Business problem

Manual lead handling can result in delayed responses, duplicate records, inconsistent qualification, missed follow-ups, incorrect assignments, and limited operational visibility.

This project will incrementally design, build, test, and document an automation system that addresses those problems. The implementation will prioritize explicit business rules, reliable data handling, observable execution, and appropriate human oversight.

## Project objectives

- Standardize lead intake and validation.
- Detect likely duplicate submissions.
- Apply transparent qualification and scoring rules.
- Assign leads according to a documented policy.
- Coordinate customer acknowledgement and internal notifications.
- Schedule follow-ups and record workflow activity.
- Handle integration failures and exceptional cases safely.
- Demonstrate the system with reproducible tests and documentation.

## Planned technology direction

- **n8n** — workflow orchestration
- **PostgreSQL** — structured lead and operational data
- **Docker** — reproducible local development
- **REST APIs and webhooks** — system integration
- **Python** — custom logic where needed
- **Git and GitHub** — version control and documentation
- **AI API (optional)** — narrowly scoped assistance such as drafting or classifying text, with validation and fallback paths

Technology choices will be confirmed against the requirements. This project aims to use free-tier or self-hosted tools where practical; free-tier availability and limits will be checked before implementation.

## Project roadmap

1. [Business case](docs/business-case.md)
2. Requirements and acceptance criteria
3. AS-IS / TO-BE process design
4. Architecture and data model
5. MVP implementation
6. Functional and failure-path testing
7. Error handling, logging, and operational guidance
8. Demonstration, documentation, and release

## Scope discipline

Features will be evaluated for business value, necessity, complexity, risk, and learning value. Useful features may be deferred rather than expanding the MVP without control.

## Repository structure

```text
docs/
  business-case.md
  decisions/
workflows/
scripts/
tests/
config/
```

Directories will gain implementation files as the project needs them; empty directories are not committed just to reserve space.

## Project integrity

ApexFlow Solutions is fictional. Any sample leads and metrics used in demonstrations will be synthetic. No real customer data, API keys, passwords, or access tokens should be committed.

This is a learning and portfolio project. A successful local demonstration is not, by itself, a claim of production deployment or measured business impact.

## Current status

The repository is at the business-case stage. Requirements, architecture, implementation, test results, and performance claims will be updated as they are actually completed.
