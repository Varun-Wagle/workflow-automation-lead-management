BEGIN;

CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(150) NOT NULL,

    email VARCHAR(254),
    phone VARCHAR(30),

    industry VARCHAR(100),
    company_size VARCHAR(50),
    location VARCHAR(150),

    source VARCHAR(50) NOT NULL DEFAULT 'website',

    status VARCHAR(20) NOT NULL DEFAULT 'new',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium',

    ai_score INTEGER,
    ai_summary TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT leads_company_name_not_blank
        CHECK (length(btrim(company_name)) > 0),

    CONSTRAINT leads_contact_name_not_blank
        CHECK (length(btrim(contact_name)) > 0),

    CONSTRAINT leads_contact_method_required
        CHECK (
            NULLIF(btrim(email), '') IS NOT NULL
            OR NULLIF(btrim(phone), '') IS NOT NULL
        ),

    CONSTRAINT leads_source_not_blank
        CHECK (length(btrim(source)) > 0),

    CONSTRAINT leads_status_valid
        CHECK (
            status IN (
                'new',
                'contacted',
                'qualified',
                'converted',
                'lost'
            )
        ),

    CONSTRAINT leads_priority_valid
        CHECK (priority IN ('low', 'medium', 'high')),

    CONSTRAINT leads_ai_score_valid
        CHECK (ai_score IS NULL OR ai_score BETWEEN 0 AND 100)
);

CREATE INDEX leads_status_created_at_idx
    ON leads (status, created_at DESC);

CREATE INDEX leads_priority_created_at_idx
    ON leads (priority, created_at DESC);

CREATE INDEX leads_location_idx
    ON leads (location);

INSERT INTO schema_migrations (version, description)
VALUES ('002', 'Create leads table');

COMMIT;