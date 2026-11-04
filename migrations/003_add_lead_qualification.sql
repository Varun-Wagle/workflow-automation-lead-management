ALTER TABLE leads
    ADD COLUMN interested_product VARCHAR(100),
    ADD COLUMN message TEXT,
    ADD COLUMN rule_score INTEGER,
    ADD COLUMN qualification_updated_at TIMESTAMPTZ;

ALTER TABLE leads
    ADD CONSTRAINT leads_rule_score_range_check
    CHECK (rule_score IS NULL OR rule_score BETWEEN 0 AND 100);

INSERT INTO schema_migrations (version, description)
VALUES ('003', 'Add lead qualification fields and rule score constraint');