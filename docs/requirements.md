# Requirements Specification — Lead Management & Sales Follow-up Automation

**Project ID:** WA-001  
**Document ID:** REQ-001  
**Version:** 0.1.0  
**Status:** Draft for review  
**Scenario:** Fictional B2B SaaS company — ApexFlow Solutions  
**Last updated:** 2026-10-24

> This document defines intended behavior, not completed implementation. Requirements and priorities may change after process design and technical feasibility review. All examples use synthetic data.

## 1. Purpose

Translate the business case into testable requirements for a lead-management automation system. The system should reduce repetitive administration while preserving reliable data handling, appropriate human oversight, and visibility into failures.

## 2. Scope and release approach

### 2.1 MVP objective

Demonstrate a reliable end-to-end flow for receiving a lead submission, validating it, preventing repeated processing of the same submission, storing a lead/opportunity record, applying transparent rules, assigning an eligible salesperson, sending an approved acknowledgement and internal notification, and recording outcomes.

### 2.2 Candidate MVP capabilities

- Webhook-based intake with schema validation.
- Submission idempotency.
- Contact and opportunity concepts kept distinct.
- Conservative duplicate detection.
- PostgreSQL persistence and integrity constraints.
- Deterministic qualification/priority rules.
- Basic salesperson eligibility and workload-aware assignment.
- Approved acknowledgement and internal notification.
- Notification status tracking and bounded retry behavior.
- Basic operational logs and actionable error reporting.
- Functional tests, failure-path tests, setup documentation, and synthetic demo data.

### 2.3 Later enhancements

- AI-assisted contextual qualification and evaluation dataset.
- Clarification conversations and AI-assisted summaries.
- CRM integration and multiple lead sources.
- Incoming reply detection and conversation-aware follow-up cancellation.
- Advanced availability/working-hours/workload integrations.
- SLA dashboards and periodic reconciliation.
- Configurable retention and deletion-request orchestration across connected systems.
- Advanced reporting and management dashboard.

A later-phase item is not a promise of implementation in the MVP. Requirements may be re-prioritized after the architecture and delivery effort are understood.

## 3. Terms and domain concepts

- **Submission:** One form event or inbound request received from a source.
- **Contact:** A person or business contact who can submit multiple inquiries.
- **Opportunity:** A distinct business requirement or potential sale associated with a contact.
- **Interaction:** An inbound or outbound communication associated with a contact and, where known, an opportunity.
- **Idempotency:** Reprocessing the same logical event does not repeat completed business effects.
- **Lead score:** A numerical assessment based on defined evidence and rules.
- **Priority:** An operational category derived from scoring and policy.
- **Acknowledgement:** A factual, approved confirmation that an inquiry was received; not a substantive sales promise.
- **Human review:** A task assigned to an authorized person when automated processing cannot safely or reliably resolve a case.

## 4. Stakeholders

- Prospective customers.
- Salespeople.
- Sales managers.
- Marketing / Sales Operations.
- Business leadership.
- Automation administrator or developer.
- IT/security personnel where applicable.

## 5. Functional requirements

Priority definitions:
- **P0:** Required for the MVP's core workflow.
- **P1:** Important reliability or operational capability; include in the MVP when feasible.
- **P2:** Planned enhancement, not required for the first working release.

### 5.1 Intake and validation

#### FR-001 — Receive lead submissions (P0)
The system shall expose a defined intake interface for receiving lead submissions through a webhook.

**Acceptance criteria**
- A valid test payload is accepted and processing begins.
- The input contract and supported fields are documented.
- The system records an identifiable processing outcome.
- The response to the sender is consistent with the intake contract and does not falsely imply that all downstream work has completed if it has not.

#### FR-002 — Validate and normalize input (P0)
The system shall validate the payload structure, required fields, field types, and supported formats before normal processing.

**Acceptance criteria**
- A valid payload proceeds to the next stage.
- A malformed payload is rejected or quarantined according to the documented policy.
- Missing optional fields do not automatically invalidate a submission.
- Validation failures are recorded without exposing secrets or unnecessary personal data in logs.

#### FR-003 — Handle incomplete but usable submissions (P1)
The system shall distinguish between unusable submissions and submissions that are valid but lack enough information for confident qualification.

**Acceptance criteria**
- A missing optional field does not block intake.
- An unusable contact method or malformed payload follows a documented failure path.
- A vague but usable inquiry can be stored with a status indicating clarification is needed.
- The system does not invent requirements or send an unsupported summary.
- Clarification messaging uses approved templates in the initial implementation.

### 5.2 Identity, duplicates, and persistence

#### FR-004 — Generate stable identifiers (P0)
The system shall assign stable unique identifiers to submissions, contacts, and opportunities as applicable.

**Acceptance criteria**
- Each persisted entity has an identifier.
- Relationships between a contact, opportunity, submission, and interaction can be traced.
- Identifiers do not depend solely on a person's email address.

#### FR-005 — Prevent duplicate event processing (P0)
The system shall use a stable source submission ID or idempotency key when available, and enforce uniqueness at the persistence layer for the selected idempotency key.

**Acceptance criteria**
- Replaying the same submission does not create a second opportunity or repeat completed side effects.
- Concurrent attempts to register the same idempotency key cannot create duplicate event records.
- The system can distinguish a previously processed event from a new submission.
- The idempotency strategy and its retention period are documented.

#### FR-006 — Match contacts and opportunities separately (P0)
The system shall not treat matching email addresses as proof that two inquiries are the same opportunity.

**Acceptance criteria**
- A repeated event is handled by the idempotency mechanism.
- A known contact may have multiple distinct opportunities.
- A possible opportunity match can be linked to an existing opportunity only when defined matching criteria support that action.
- Ambiguous matches are flagged for review rather than automatically merged.
- Matching signals and their limitations are documented.

#### FR-007 — Persist lead and processing state (P0)
The system shall persist the contact/opportunity information and processing state required by the approved data model.

**Acceptance criteria**
- A successfully processed submission can be retrieved.
- The record contains its current status and relevant timestamps.
- Assignment and priority changes can be traced.
- A notification failure does not cause the lead to be created again.
- Database constraints protect required relationships and uniqueness invariants.

#### FR-008 — Handle concurrent writes safely (P0)
The system shall rely on database constraints and appropriate transactional operations for critical uniqueness and state changes, not only on a preceding workflow check.

**Acceptance criteria**
- Concurrent duplicate registration attempts result in one logical submission record.
- A uniqueness conflict is handled as an expected outcome, not an unhandled crash.
- The workflow can safely determine whether to continue, return an existing result, or flag an unexpected conflict.

### 5.3 Qualification and priority

#### FR-009 — Apply deterministic qualification rules (P0)
The system shall apply explicit, versioned business rules to the available lead data.

**Acceptance criteria**
- Rules and score contributions are documented.
- The result includes a score or classification and the rule-based reasons supporting it.
- Missing evidence is not silently treated as a positive signal.
- The same input and rule version produce the same rule-based result.

#### FR-010 — Keep qualification, priority, and assignment distinct (P0)
The system shall represent qualification outcome, operational priority, and salesperson assignment as separate decisions or fields.

**Acceptance criteria**
- A qualified lead is not automatically assumed to be high priority.
- Assignment does not change the recorded qualification evidence.
- Each decision can be inspected independently.

#### FR-011 — Provide an uncertainty path (P1)
When available data is insufficient for a reliable automated decision, the system shall use a defined fallback such as requesting clarification, assigning a provisional status, or creating a review task.

**Acceptance criteria**
- Uncertainty is represented explicitly.
- The system does not invent budget, urgency, authority, or requirements.
- The fallback action is determined by documented rules.
- Cases requiring review remain visible until resolved.

#### FR-012 — Support AI-assisted contextual qualification (P2)
A later version may use an AI model to interpret free-text requirements and identify supporting evidence, likely service category, missing information, and uncertainty.

**Acceptance criteria for the later phase**
- AI output follows a validated structured schema.
- The model is instructed to distinguish evidence from inference.
- AI output is not treated as ground truth or used as the sole basis for a consequential decision.
- AI failure or invalid output has a defined fallback.
- Performance is evaluated against a labelled test dataset before operational use.
- False-high, false-low, disagreement, and review rates are measured.

#### FR-013 — Resolve rule/AI disagreement safely (P2)
When AI-assisted interpretation is introduced, the system shall apply a documented decision policy for agreement, disagreement, and uncertainty.

**Acceptance criteria for the later phase**
- A model's self-reported confidence alone is not treated as calibrated probability.
- Material disagreement invokes the defined fallback policy.
- The policy balances missed opportunities, false prioritization, response time, and review workload.
- Human review is targeted to unresolved or high-impact cases rather than every lead.
- Policy changes are versioned and evaluated against the test dataset.

### 5.4 Salesperson assignment

#### FR-014 — Check salesperson eligibility (P0)
The system shall select only from salespeople who meet the configured eligibility and availability conditions.

**Acceptance criteria**
- Ineligible or unavailable salespeople are excluded.
- The eligibility criteria are configurable and documented.
- If no eligible salesperson exists, the lead remains safely stored and unassigned.
- The system alerts the configured responsible team or manager when assignment cannot be completed.

#### FR-015 — Select among eligible candidates (P1)
When multiple candidates are eligible, the system shall apply a documented selection policy, initially using a simple workload-aware method.

**Acceptance criteria**
- The same eligible-candidate data and policy produce a predictable selection, subject to tie-breaking rules.
- Workload is defined using an explicit metric.
- The selected salesperson and assignment timestamp are recorded.
- The reason for selection is inspectable.

#### FR-016 — Record assignment history (P1)
The system shall preserve material assignment changes rather than silently overwriting history.

**Acceptance criteria**
- Initial assignment and reassignment are recorded.
- Each event identifies the previous and new assignee where applicable, timestamp, and reason.
- Relevant assignees are notified according to policy.

#### FR-017 — Reassign when eligibility changes (P2)
A later version may re-evaluate active assignments when a salesperson becomes unavailable.

**Acceptance criteria for the later phase**
- The system re-evaluates eligibility using current configured data.
- A suitable candidate is selected using the approved policy.
- If no suitable candidate exists, the lead is escalated for manual reassignment.
- Reassignment does not erase the original assignment history.
- Repeated reassignment is controlled to avoid assignment churn.

### 5.5 Customer acknowledgement and notifications

#### FR-018 — Send approved acknowledgements (P0)
The system shall send an approved, factual acknowledgement for submissions that meet the defined communication conditions.

**Acceptance criteria**
- The message confirms receipt without making unsupported claims about price, delivery, or solution suitability.
- The destination and content are validated according to policy.
- The communication outcome is recorded.
- Acknowledgement behavior for incomplete submissions is defined separately.

#### FR-019 — Notify the assigned salesperson (P0)
The system shall notify the assigned salesperson of a new assignment through the selected channel.

**Acceptance criteria**
- The notification identifies the lead/opportunity reference, priority, and assignee.
- The notification includes only the personal information necessary for the recipient's task.
- The notification result is recorded.
- An unassigned lead follows the documented escalation path.

#### FR-020 — Track notification state independently (P0)
The system shall track notification processing separately from lead persistence and lead status.

**Acceptance criteria**
- A lead can be successfully stored while a notification is pending or failed.
- Retrying a notification does not recreate the lead.
- The system records notification type, related entity, attempt count, timestamps, status, and an appropriate error category.
- Logs avoid unnecessary sensitive content.

#### FR-021 — Retry recoverable notification failures (P1)
The system shall retry eligible transient failures using bounded retries and delays.

**Acceptance criteria**
- Retry limits and delay policy are configurable.
- Permanent failures such as invalid recipients are not retried indefinitely.
- Rate-limit responses are handled according to service guidance where available.
- Exhausted retries produce a visible failed state and an alert or review task.
- Unknown delivery outcomes are distinguished from confirmed failures where the integration allows this.

#### FR-022 — Prevent duplicate communications (P1)
The system shall use notification identifiers, durable state, and available provider capabilities to reduce duplicate communications.

**Acceptance criteria**
- Reprocessing a completed notification does not intentionally send it again.
- A timeout with an unknown provider outcome follows a documented reconciliation or review policy.
- The system does not claim exactly-once delivery where the external provider cannot guarantee it.

### 5.6 Replies and follow-up

#### FR-023 — Maintain follow-up state (P2)
A later version shall track scheduled follow-ups and their relationship to the relevant opportunity or conversation.

**Acceptance criteria for the later phase**
- Follow-up status and scheduled time are stored.
- The system can identify pending, sent, cancelled, and failed follow-ups.
- Follow-ups are bounded by a documented sequence and stop policy.

#### FR-024 — Respond to customer replies (P2)
A later version shall detect incoming replies where supported by the email or CRM integration and associate them with the relevant contact and opportunity.

**Acceptance criteria for the later phase**
- A reply is recorded as an interaction.
- Pending automated follow-ups for the relevant conversation are paused or cancelled according to policy.
- An incoming reply does not automatically cancel follow-ups for unrelated opportunities belonging to the same contact.
- The assigned salesperson is notified when human action is needed.
- Ambiguous reply-to-opportunity matching is flagged rather than guessed.

#### FR-025 — Respect observable manual communication (P2)
A later version shall pause or revise scheduled automated follow-ups when a supported integration or explicit user action records that manual communication has begun.

**Acceptance criteria for the later phase**
- The system documents which signals count as manual contact.
- Before sending a scheduled follow-up, the workflow checks current conversation state.
- A state change between scheduling and sending is handled safely.
- The system does not assume that unobserved communication occurred.

### 5.7 Monitoring, privacy, and data lifecycle

#### FR-026 — Record workflow outcomes (P0)
The system shall record sufficient operational information to diagnose normal and failed processing.

**Acceptance criteria**
- Each processing attempt can be correlated with a submission and relevant entity.
- Important stages have observable outcomes.
- Errors have a category and actionable context.
- Logs exclude credentials and minimize personal data.
- Sensitive values are not exposed in routine team notifications.

#### FR-027 — Alert on unresolved failures (P1)
The system shall notify an appropriate operator or team when a failure cannot be recovered automatically or when a required action remains unresolved.

**Acceptance criteria**
- Alert thresholds and recipients are configurable.
- Alerts contain enough context to investigate without unnecessarily exposing personal information.
- The alert itself has an observable outcome where supported.

#### FR-028 — Define retention and deletion handling (P2)
A later version shall implement a configurable data-retention and deletion-request process based on an approved policy.

**Acceptance criteria for the later phase**
- A request can be recorded, tracked, and associated with its scope and status.
- The applicable policy determines verification, restrictions, retention exceptions, and completion steps.
- The system does not impose an arbitrary universal 30- or 60-day delay.
- Connected systems, logs, and backups are considered in the documented process.
- Completion or a documented exception is recorded.
- The project does not claim legal compliance without appropriate policy and legal review.

## 6. Non-functional requirements

### NFR-001 — Reliability
Critical state changes must be durable. Expected failures must produce a defined state and recovery path rather than silent data loss.

### NFR-002 — Idempotency and concurrency
The system must protect critical uniqueness invariants against repeated and concurrent requests using persistence-layer guarantees where appropriate.

### NFR-003 — Security
Secrets must be stored outside committed source files. Access to databases, workflow administration, and connected services must be limited to necessary permissions.

### NFR-004 — Privacy and data minimization
Only information necessary for the defined business purpose should be collected, stored, logged, and sent through notifications. Demonstrations must use synthetic data.

### NFR-005 — Maintainability
Workflow names, node labels, configuration, business rules, and documentation must be understandable to another developer. Complex decisions should not be hidden in opaque expressions.

### NFR-006 — Observability
Operators must be able to determine whether a submission was accepted, processed, rejected, delayed, or failed and identify the next recovery action.

### NFR-007 — Testability
Business rules and important failure paths must be testable using repeatable synthetic fixtures. AI-assisted features must have an evaluation set if introduced.

### NFR-008 — Portability
A developer should be able to reproduce the local environment using documented configuration and the selected container setup, subject to external account and credential requirements.

### NFR-009 — Cost awareness
The design should prefer free-tier or self-hosted components when suitable, while documenting relevant usage limits, operational costs, and trade-offs.

### NFR-010 — Performance
The system should measure processing and acknowledgement latency. Numeric performance targets will be set after the expected workload and local baseline are established; no unsupported throughput claim is made at this stage.

### NFR-011 — Recovery
Retries must be bounded. Failed or ambiguous operations must remain visible and must not trigger unsafe repeated side effects.

### NFR-012 — Auditability
Material changes to priority, assignment, and processing state must have traceable timestamps and reasons appropriate to the system's scope.

## 7. Core business rules to define before implementation

The following values and policies remain open and must be resolved in process design:

1. Which fields are required for a usable submission versus optional for qualification?
2. Which lead statuses and opportunity statuses are valid?
3. What constitutes a duplicate submission, contact, or opportunity?
4. What matching evidence is sufficient to link a new inquiry to an existing opportunity?
5. Which deterministic criteria contribute to the score, and how are score bands mapped to priority?
6. What workload metric and tie-breaker are used for assignment?
7. Which acknowledgement templates and channels are approved?
8. What retry count, delay, and terminal failure policy apply to each integration?
9. What follow-up sequence and stop conditions apply in the later phase?
10. What retention and deletion policy applies to each category of stored data?

These policies must not be invented silently during implementation.

## 8. MVP acceptance test outline

At minimum, the MVP test suite should cover:

- Valid submission.
- Malformed payload.
- Missing optional field.
- Missing or invalid contact method.
- Same submission replayed sequentially.
- Same idempotency key submitted concurrently.
- Existing contact with a distinct new opportunity.
- Ambiguous possible duplicate.
- Deterministic scoring boundary cases.
- No eligible salesperson.
- Multiple eligible salespeople and workload tie.
- Lead persistence succeeds but notification fails.
- Recoverable notification failure and retry exhaustion.
- Notification outcome unknown after timeout.
- Reprocessing after a partial failure.
- Secret values are not included in logs or repository files.

Tests must record expected and actual outcomes. Passing results should only be reported after the tests have been executed.

## 9. Traceability

Each requirement ID should be traceable to:
- A business problem or objective.
- One or more process steps.
- An implementation component.
- Acceptance tests.
- Documentation or demonstration evidence.

A later traceability matrix will connect these artifacts.

## 10. Open decisions and next artifact

The following are intentionally not fully specified yet:
- Detailed AS-IS and TO-BE process steps.
- Exact field schema and status transitions.
- Duplicate-matching policy.
- Score thresholds and assignment policy.
- Integration choices and notification semantics.
- Retry/backoff configuration.
- MVP release boundary after feasibility review.

**Next artifact:** `docs/process-design.md`, documenting process states, decision points, exception paths, and the MVP versus later-phase workflow.
