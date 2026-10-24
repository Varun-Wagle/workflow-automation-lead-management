-- Smoke-test queries for migration 001.
-- Run only against a disposable database where migration 001 is applied.
-- This script uses a transaction and rolls back all test rows.
-- Execute with: psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f tests/sql/001_submissions_smoke_test.sql

BEGIN;

DO $$
DECLARE
    v_source text := 'website_form';
    v_event_key text := 'smoke-test-event-001';
    v_submission_id uuid;
    v_count integer;
BEGIN
    -- Valid insert should generate UUIDs and default timestamps/status.
    INSERT INTO submissions (
        source,
        source_event_key,
        payload_fingerprint,
        schema_version
    )
    VALUES (
        v_source,
        v_event_key,
        repeat('a', 64),
        1
    )
    RETURNING id INTO v_submission_id;

    IF v_submission_id IS NULL THEN
        RAISE EXCEPTION 'Expected generated submission UUID';
    END IF;

    SELECT count(*) INTO v_count
    FROM submissions
    WHERE source = v_source
      AND source_event_key = v_event_key
      AND status = 'pending'
      AND correlation_id IS NOT NULL
      AND received_at IS NOT NULL;

    IF v_count <> 1 THEN
        RAISE EXCEPTION 'Expected exactly one correctly defaulted submission; found %', v_count;
    END IF;

    -- Duplicate source/event key must be rejected by the database.
    BEGIN
        INSERT INTO submissions (
            source,
            source_event_key,
            payload_fingerprint,
            schema_version
        )
        VALUES (
            v_source,
            v_event_key,
            repeat('a', 64),
            1
        );
        RAISE EXCEPTION 'Expected duplicate source/event key to fail';
    EXCEPTION
        WHEN unique_violation THEN
            NULL; -- Expected outcome.
    END;

    -- Invalid fingerprint must be rejected.
    BEGIN
        INSERT INTO submissions (
            source,
            source_event_key,
            payload_fingerprint,
            schema_version
        )
        VALUES (
            v_source,
            'smoke-test-invalid-fingerprint',
            'not-a-sha256-fingerprint',
            1
        );
        RAISE EXCEPTION 'Expected invalid fingerprint to fail';
    EXCEPTION
        WHEN check_violation THEN
            NULL; -- Expected outcome.
    END;

    -- Invalid status must be rejected.
    BEGIN
        INSERT INTO submissions (
            source,
            source_event_key,
            payload_fingerprint,
            status,
            schema_version
        )
        VALUES (
            v_source,
            'smoke-test-invalid-status',
            repeat('b', 64),
            'sent',
            1
        );
        RAISE EXCEPTION 'Expected invalid status to fail';
    EXCEPTION
        WHEN check_violation THEN
            NULL; -- Expected outcome.
    END;
END
$$;

ROLLBACK;
