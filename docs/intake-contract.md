# Lead Intake API Contract

**Project ID:** WA-001  
**Document ID:** API-001  
**Version:** 0.1.0  
**Status:** Proposed MVP contract — not implemented or tested  
**Scenario:** Fictional B2B SaaS company, ApexFlow Solutions  
**Last updated:** 2026-10-24

> This contract defines the first version of the lead-intake boundary. It is a design artifact, not evidence of a deployed endpoint. All example data is synthetic.

## 1. Purpose and boundary

The intake endpoint accepts one source submission, validates its envelope and fields, and durably registers that submission in PostgreSQL. It does **not** promise that contact resolution, opportunity creation, qualification, assignment, or notification delivery has completed when it responds.

**Proposed endpoint:** `POST /webhook/v1/leads`  
**Content type:** `application/json`  
**Contract version:** `schema_version: 1`

The exact n8n webhook path may need a deployment-specific prefix. The externally documented route must remain versioned and stable once published.

## 2. Authentication and transport

- Require HTTPS at any non-local deployment boundary.
- For the initial demonstration, protect the webhook with a shared secret header such as `X-Intake-Token`; store the secret in n8n credentials or environment configuration, never in Git.
- Compare secrets safely and reject missing or invalid credentials before processing the body.
- Do not include the token or authorization headers in execution logs, error responses, or database event metadata.
- Keep the endpoint private/local during development unless an explicit protected test setup is required.
- Rate limiting and request-size limits should be applied at the ingress boundary where available.

Authentication mechanism details must be confirmed against the actual n8n deployment before implementation.

## 3. Request schema

### 3.1 Example request

```json
{
  "schema_version": 1,
  "source": "website_form",
  "source_event_key": "webform-submission-10001",
  "contact": {
    "name": "Aarav Mehta",
    "company": "Northstar Analytics",
    "email": "aarav@example.test",
    "phone": null
  },
  "inquiry": {
    "product_interest": "Workflow Automation",
    "company_size": "11-50",
    "message": "We want to automate inbound lead routing."
  },
  "communication": {
    "email_acknowledgement_allowed": false
  }
}
```

The `.test` email domain is reserved for testing. Do not use real personal data in repository examples.

### 3.2 Field definitions

| Field | Type | Required | Rules |
|---|---|---:|---|
| `schema_version` | integer | Yes | Must equal `1` for this contract |
| `source` | string | Yes | Trimmed, lowercase source identifier; must be in the configured source allowlist |
| `source_event_key` | string | Yes | 1–128 characters; stable for retries of the same source event; opaque, case-sensitive identifier |
| `contact` | object | Yes | Must contain at least one usable contact channel as defined below |
| `contact.name` | string or null | No | Trimmed; if supplied, must not be blank |
| `contact.company` | string or null | No | Trimmed; if supplied, must not be blank |
| `contact.email` | string or null | Conditionally | If supplied, must pass basic syntax validation and be normalized for comparison |
| `contact.phone` | string or null | Conditionally | If supplied, must be normalized only when confidently parseable; preserve no guessed country code |
| `inquiry` | object | Yes | May contain optional inquiry details |
| `inquiry.product_interest` | string or null | No | Trimmed; if supplied, must not be blank |
| `inquiry.company_size` | string or null | No | Optional descriptive value; controlled categories may be introduced later |
| `inquiry.message` | string or null | No | Trimmed; enforce a configured maximum length before persistence |
| `communication.email_acknowledgement_allowed` | boolean | No | Missing means `false`; `true` is not proof of legally sufficient consent by itself and is honored only under the approved communication policy |

**Usable contact channel rule:** at least one of `contact.email` or `contact.phone` must be present and non-blank. An invalid supplied email or phone must not be silently discarded if that leaves no usable channel.

Unknown top-level and nested fields should be rejected in contract version 1 rather than silently ignored. This makes producer/consumer drift visible. If a future source needs additional fields, update the contract and versioning policy intentionally.

### 3.3 Normalization and fingerprinting

- Trim leading/trailing whitespace from user-facing text fields.
- Normalize email for matching using a documented conservative policy; do not apply provider-specific transformations such as removing dots or plus-tags.
- Normalize phone only when a reliable parsing context exists; do not invent a country code.
- Keep the original event key exactly as supplied after validation; do not derive it from email, phone, or message text.
- Compute a deterministic payload fingerprint from the validated, normalized business payload, excluding server-generated timestamps, correlation IDs, authentication data, and transport metadata.
- Canonicalize object key order and null/omitted optional-field handling consistently before hashing.
- Store the fingerprint with the submission. The same source/key with the same fingerprint is a replay; the same source/key with a different fingerprint is an integrity conflict requiring investigation, not an overwrite.

The fingerprint algorithm and canonicalization must be implemented once and covered by tests before it is relied upon.

## 4. Required idempotency behavior

The database constraint `UNIQUE (source, source_event_key)` is the final authority. An n8n pre-check alone is insufficient because concurrent requests can race.

1. A new key is registered in one short transaction.
2. A repeated key with a matching fingerprint returns the existing submission reference and current intake/processing status; it must not create another submission or repeat downstream side effects.
3. A repeated key with a different fingerprint returns a conflict and creates or exposes an actionable integrity event/review path. It must not silently replace the original payload.
4. If the database commit result is uncertain due to a connection failure, do not claim success. The client retries with the **same** key; the database then determines whether the original transaction committed.
5. Different keys from the same contact represent distinct submissions. Contact identity alone does not imply that two inquiries are the same opportunity.

## 5. Response contract

All responses use JSON. The endpoint must not expose SQL details, stack traces, credentials, or raw internal provider errors.

### 5.1 New submission durably registered — `202 Accepted`

Return only after the submission registration transaction commits.

```json
{
  "request_id": "0d4d1b15-4f5b-4e6b-b8e1-9a7d7e8c1001",
  "submission_id": "7e8ad0ef-3e32-4d61-8b6c-22d5e7c01001",
  "status": "accepted",
  "processing_status": "pending"
}
```

`request_id` is a server-generated correlation identifier. `submission_id` is the durable database identifier. The response confirms intake registration only; it does not assert that the lead has been qualified, assigned, or contacted.

### 5.2 Matching replay — `200 OK`

```json
{
  "request_id": "4baf8a12-40d3-4cc3-93cb-11a3f9c01002",
  "submission_id": "7e8ad0ef-3e32-4d61-8b6c-22d5e7c01001",
  "status": "duplicate",
  "processing_status": "pending"
}
```

Return the existing submission ID and its current status. Do not repeat business effects. The example status is illustrative; implementation must return the persisted status.

### 5.3 Invalid request — `400 Bad Request` or `422 Unprocessable Content`

- Use `400` for malformed JSON or an unreadable request body.
- Use `422` for a parseable JSON body that violates the schema or field rules.

```json
{
  "request_id": "server-generated-correlation-id",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request does not match the lead intake contract.",
    "fields": [
      {
        "field": "contact",
        "reason": "At least one valid email or phone number is required."
      }
    ]
  }
}
```

Return safe field paths and reason codes, not the submitted values.

### 5.4 Authentication failure — `401 Unauthorized` or `403 Forbidden`

Return a generic error. Do not disclose whether a particular secret or source identifier is valid.

### 5.5 Event-key payload conflict — `409 Conflict`

```json
{
  "request_id": "server-generated-correlation-id",
  "error": {
    "code": "IDEMPOTENCY_KEY_PAYLOAD_MISMATCH",
    "message": "This source event key is already registered with a different payload."
  }
}
```

Do not update the existing submission. Persist an operational event or review task when the database is available.

### 5.6 Retryable intake failure — `503 Service Unavailable`

Use when the service cannot confirm durable registration, including a database outage or an uncertain commit outcome. A response must not claim the submission was accepted. Include a reasonable `Retry-After` header when the deployment can provide one.

```json
{
  "request_id": "server-generated-correlation-id",
  "error": {
    "code": "INTAKE_TEMPORARILY_UNAVAILABLE",
    "message": "The submission could not be confirmed. Retry using the same source event key."
  }
}
```

Do not return raw database exceptions. A client should retry the same logical event with the same `source_event_key`, never generate a new key just because the request timed out.

### 5.7 Additional ingress responses

- `413 Content Too Large` when the configured request-size limit is exceeded.
- `429 Too Many Requests` when rate limiting is enabled.
- `500 Internal Server Error` only for an unexpected failure that cannot be safely classified; return a generic body and log sanitized diagnostics with the request ID.

## 6. Intake transaction and response timing

The synchronous intake path is deliberately narrow:

1. Authenticate and parse the request.
2. Validate schema and normalize fields.
3. Generate a request/correlation ID and deterministic fingerprint.
4. Attempt idempotent submission registration in PostgreSQL.
5. Commit the transaction.
6. Return `202` for a new durable registration or `200` for a matching replay.

Downstream processing is asynchronous or separately resumed from durable state. Do not perform email sends, AI calls, salesperson assignment, or long-running work before returning the intake response.

If downstream work needs a durable queue signal, create it transactionally with the submission or make pending work discoverable by a reliable database-backed polling/reconciliation process. Do not depend solely on an in-memory n8n execution continuing after the response.

## 7. Security and data minimization

- Do not log full request bodies by default.
- Redact email, phone, inquiry text, authentication headers, and secrets from routine error messages.
- Persist only fields needed for the approved workflow.
- Keep credentials and local environment files out of Git.
- Use synthetic values in examples, screenshots, and tests.
- The optional acknowledgement flag defaults to false. It does not authorize marketing follow-ups or override applicable communication/privacy requirements.
- Retention, deletion, and consent policy remain explicit business/legal decisions; this contract does not claim regulatory compliance.

## 8. Acceptance tests

The contract is ready for implementation when tests verify at least:

1. Valid request with email registers once and returns `202` after commit.
2. Valid request with phone only registers once if phone normalization/validation succeeds.
3. Missing both email and phone is rejected.
4. Malformed JSON returns `400`; schema errors return `422`.
5. Unsupported schema version and unknown fields are rejected.
6. Missing/invalid authentication is rejected without writing a submission.
7. Same source/key and same normalized payload returns the existing submission without repeating side effects.
8. Same source/key and changed business payload returns `409` and does not overwrite the original.
9. Concurrent identical requests produce one durable submission.
10. Two different event keys for the same contact are not automatically collapsed into one submission.
11. Database unavailable before confirmed commit returns retryable failure and never returns accepted.
12. Retry after an uncertain commit uses the same key and resolves to either the existing submission or a new single registration.
13. Response bodies and logs do not expose secrets, SQL, stack traces, or full contact details.
14. `email_acknowledgement_allowed` omitted or false does not enqueue an acknowledgement.
15. `202` does not imply downstream processing or message delivery has completed.

## 9. Decisions still required before implementation

- Confirm the actual n8n webhook URL/path and supported authentication mechanism.
- Select the payload fingerprint algorithm and exact canonicalization rules.
- Finalize maximum request and inquiry-message sizes.
- Confirm allowed `source` values and how source keys are generated by each producer.
- Confirm whether the first MVP accepts phone-only contacts and which phone parsing region applies, if any.
- Approve the communication/acknowledgement policy before enabling any outbound acknowledgement.
- Select the database transaction/function interface used by n8n for registration.
- Choose whether rate limiting is handled by a reverse proxy, hosting layer, or another component.

## 10. Traceability

This contract refines the webhook and idempotency behavior described in `docs/requirements.md`, `docs/process-design.md`, `docs/data-model.md`, and `docs/system-architecture.md`.

**Next implementation milestone:** implement the first versioned PostgreSQL migration for the intake persistence boundary, then test uniqueness, fingerprint conflicts, concurrent replay, and commit-failure behavior in an isolated development database. Do not connect the public-facing webhook until those database invariants are verified.
