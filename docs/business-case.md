# Lead Management & Sales Follow-up Automation — Business Case

**Project ID:** WA-001  
**Document version:** 0.1.0  
**Status:** Draft  
**Scenario:** B2B SaaS lead management  
**Primary objective:** Improve lead-processing efficiency, response consistency, and sales visibility.

## 1. Executive summary

ApexFlow Solutions is a fictional B2B SaaS company providing workflow automation and business-process software to small and medium-sized businesses.

The company receives prospective-customer inquiries through website forms, product demonstration requests, marketing campaigns, and other channels. Its assumed current process depends heavily on manual work: recording lead information, qualifying prospects, assigning salespeople, sending acknowledgements, scheduling follow-ups, and updating records.

This creates opportunities for delayed responses, duplicate records, inconsistent qualification, missed follow-ups, incorrect assignments, and incomplete reporting.

This project proposes an incremental workflow automation system for lead intake, validation, duplicate detection, qualification, assignment, communications, follow-up scheduling, and operational recordkeeping.

n8n is the proposed primary orchestration platform. Data storage, integrations, and AI assistance will be selected after requirements analysis. AI may assist with tasks such as interpreting free-text inquiries or drafting emails, but consequential decisions will use explicit rules and appropriate human oversight rather than relying exclusively on an AI-generated judgment.

The system will be developed as a minimum viable product (MVP) before any larger enhancements are adopted.

## 2. Business context

ApexFlow receives inquiries from prospects interested in its products and services. Each inquiry may differ in commercial value, urgency, completeness, and fit.

Examples include:
- A small business asking about a basic automation package.
- A growing company requesting a product demonstration.
- A larger organization describing a complex, multi-department requirement.
- A prospect submitting a second inquiry because an earlier request has not received a response.

As inquiry volume increases, a predominantly manual process becomes harder to operate consistently. The company needs a standard process for routine administration while preserving human judgment where it is needed.

## 3. Current process (AS-IS)

The assumed process is:

1. A prospect submits a website form.
2. The submission is recorded in a spreadsheet or similar system.
3. A sales employee checks for new inquiries.
4. The employee reviews the available information.
5. The employee assesses the prospect and urgency.
6. A salesperson is selected.
7. The prospect is contacted.
8. Follow-up activities are managed manually.
9. The lead status is updated.
10. Management periodically reviews records and prepares reports.

This is a fictional scenario. Its exact process, volumes, and performance characteristics would need validation in a real consulting engagement.

## 4. Business problems

### 4.1 Delayed lead processing
New inquiries may wait until an employee checks the system, delaying acknowledgement and initial contact.

### 4.2 Inconsistent qualification
Different employees may assess similar inquiries differently when standardized qualification criteria are absent.

### 4.3 Duplicate records
A prospect may submit multiple inquiries or use different channels, causing the same prospect to be treated as multiple leads.

### 4.4 Missed follow-ups
Follow-up depends on employees remembering to act and maintaining accurate records. Prospects who do not respond may not receive an appropriate follow-up.

### 4.5 Incorrect or unavailable assignment
A lead may be assigned to someone who is unavailable, lacks relevant expertise, or has excessive workload.

### 4.6 Limited operational visibility
Managers may struggle to see lead volumes, qualification status, response times, overdue follow-ups, pipeline progress, and workflow failures.

### 4.7 Limited failure visibility
A workflow may fail to update a record, send a notification, or schedule a follow-up without being noticed promptly.

## 5. Proposed process (TO-BE)

The proposed workflow will:

1. Receive a lead submission.
2. Validate and normalize submitted information.
3. Identify incomplete or invalid submissions.
4. Detect potential duplicates.
5. Create or update the appropriate lead record.
6. Apply deterministic qualification and scoring rules.
7. Use AI assistance only where it offers demonstrable value.
8. Assign the lead to an eligible salesperson.
9. Send appropriate acknowledgement and internal notifications.
10. Schedule follow-up activities.
11. Detect relevant customer responses and update status where supported.
12. Escalate overdue actions according to defined rules.
13. Record important events, statuses, and failures.
14. Provide basic operational metrics.

Successful processing, recoverable errors, permanent failures, and cases requiring human intervention must be distinguishable.

## 6. Stakeholders

### External
- **Prospective customers:** expect timely, relevant communication and appropriate handling of their information.

### Internal
- **Salespeople:** need accurate lead details, appropriate assignments, and useful follow-up reminders.
- **Sales managers:** monitor workload, distribution, response times, follow-up compliance, and sales performance.
- **Marketing:** may use source and qualification data to assess campaign effectiveness.
- **Business leadership:** evaluates operational efficiency, commercial contribution, and ROI.
- **Sales Operations / Revenue Operations:** supports data quality, process consistency, and reporting.

### Technical
- **Automation administrator or developer:** maintains workflows, integrations, configuration, and error handling.
- **IT or security personnel:** may oversee access controls, credential management, data protection, and integration security.

## 7. Business objectives

The system should aim to:

1. Reduce manual lead-intake and record-management effort.
2. Improve the consistency of qualification.
3. Reduce duplicate lead creation.
4. Improve acknowledgement and response times.
5. Reduce missed or overdue follow-ups.
6. Improve assignment accuracy.
7. Provide visibility into lead-processing status.
8. Detect and communicate workflow failures.
9. Maintain a useful history of lead activities.
10. Support decisions with reliable operational reporting.

The objectives will be translated into measurable acceptance criteria during requirements analysis. No percentage improvement or financial benefit is assumed at this stage.

## 8. Candidate success metrics

| Metric | Purpose |
|---|---|
| Lead processing time | Time required to process a new inquiry |
| First acknowledgement time | Delay between submission and acknowledgement |
| Duplicate detection rate | Effectiveness of identifying likely duplicate submissions |
| Follow-up completion rate | Whether scheduled follow-ups occur as intended |
| Assignment accuracy | Whether leads are routed to eligible salespeople |
| Workflow success rate | Proportion of executions completed successfully |
| Exception resolution time | Time required to resolve failures |
| Manual intervention rate | Frequency of human intervention |
| Lead-status completeness | Whether important records have current statuses |

A baseline should be established before making claims about improvements. Where possible, measurements should be derived from execution records and timestamps.

## 9. Proposed technology direction

- **n8n:** workflow orchestration.
- **PostgreSQL:** structured lead and operational data, if justified by the design.
- **Docker:** reproducible local development and deployment.
- **REST APIs and webhooks:** integration between services.
- **Python:** custom processing where workflow nodes and expressions are insufficient.
- **Git and GitHub:** version control, documentation, and portfolio.
- **Email integration:** customer acknowledgement and internal notifications.
- **AI API (optional):** limited qualification assistance or email drafting.

A suitable free-tier or self-hosted AI service may be evaluated. Current availability, limits, and integration requirements must be checked before use. The final architecture will follow requirements analysis rather than being assumed in advance.

## 10. Human oversight

Human review may be needed when:
- Qualification is uncertain.
- AI output conflicts with deterministic rules.
- The available data is insufficient for a reliable decision.
- No eligible salesperson can be found.
- A prospect asks a question requiring commercial judgment.
- An integration failure prevents safe processing.
- Company policy requires approval for a communication.

Routine, low-risk tasks may be automated with suitable safeguards. Automation should not remove human accountability where judgment is necessary.

## 11. Initial scope

### Candidate MVP capabilities
- Receive submissions through a webhook.
- Validate and normalize lead data.
- Generate a unique lead identifier.
- Detect duplicates using documented matching rules.
- Store lead records.
- Apply deterministic scoring rules.
- Assign leads using a simple, configurable policy.
- Send customer acknowledgement emails.
- Notify the assigned salesperson.
- Record processing status and relevant events.
- Handle common validation and integration failures.
- Provide setup and operational documentation.

The precise MVP boundary will be confirmed in the requirements document.

### Candidate future enhancements
- AI-assisted qualification.
- AI-generated email drafts.
- Human approval with a configurable timeout.
- Availability-aware, workload-aware, or round-robin assignment.
- CRM integration.
- Multi-stage follow-up sequences.
- Customer-response detection.
- SLA monitoring and escalation.
- Management dashboards and advanced reporting.
- More sophisticated duplicate resolution.
- Additional lead sources.

These capabilities are candidates, not automatic commitments for the first release.

## 12. Assumptions and constraints

### Assumptions
- ApexFlow Solutions is fictional and is used to model a realistic business scenario.
- The first implementation focuses on website-generated leads.
- Development and testing begin in a controlled environment.
- Qualification criteria can be expressed as explicit business rules.
- A suitable database and email integration will be available.
- Human intervention remains available for exceptional cases.

### Constraints
- Prefer free-tier or self-hosted tools when practical.
- External services can impose API limits, authentication requirements, and availability constraints.
- Local development alone does not establish production readiness.
- AI output may be inaccurate and must be validated before consequential use.
- Personal information must be handled appropriately.
- Scope must remain feasible to implement, test, document, and demonstrate.

## 13. Initial risk register

| Risk | Potential consequence | Initial mitigation |
|---|---|---|
| Duplicate webhook delivery | Duplicate records or communications | Idempotent processing and database constraints |
| Invalid input | Incomplete or incorrect records | Validation and explicit rejection/review paths |
| Incorrect scoring | Misprioritized leads | Transparent rules and review mechanisms |
| Salesperson unavailable | Delayed follow-up | Eligibility checks and reassignment path |
| Email delivery failure | Prospect not acknowledged | Track delivery status where available and alert on failure |
| Database failure | Processing interruption | Controlled retries and recovery procedures |
| AI service failure | Qualification or drafting unavailable | Deterministic fallback where appropriate |
| Excessive notifications | Important alerts are ignored | Notification thresholds and escalation rules |
| Repeated email delivery | Poor customer experience | Idempotency and communication-state tracking |
| Sensitive data exposure | Privacy or security incident | Access controls and data minimization |

## 14. Expected business value

Potential benefits include reduced manual administration, more consistent lead handling, stronger follow-up discipline, and improved operational visibility.

Actual impact depends on lead volume, existing process efficiency, implementation quality, and employee adoption. Financial savings, conversion improvements, and performance gains will not be claimed without supporting measurements.

## 15. Definition of project success

The agreed release should:
- Implement the approved requirements.
- Process valid submissions correctly.
- Handle duplicates according to documented rules.
- Preserve lead records reliably.
- Perform defined assignment and notification actions.
- Handle expected failures safely.
- Prevent unintended duplicate processing and communications.
- Produce useful operational records.
- Pass documented functional and failure-path tests.
- Be installable and demonstrable using documented instructions.
- Include architecture documentation, test evidence, version history, and a reproducible demonstration.

## 16. Next steps

The next artifacts will define:
1. Functional and non-functional requirements.
2. Detailed AS-IS and TO-BE process specifications.
3. Business rules and acceptance criteria.
4. MVP boundary and release plan.
5. Technical architecture and data model.

This business case will be revised as the requirements and design become clearer.
