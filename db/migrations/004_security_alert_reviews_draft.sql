-- DRAFT ONLY: independent administrator alert review state.
-- Do not apply to production without database privileges, backup and review.
BEGIN;
CREATE TABLE IF NOT EXISTS seller_security_alert_reviews (
    bucket_digest char(64) PRIMARY KEY
        CHECK (bucket_digest ~ '^[0-9a-f]{64}$'),
    state text NOT NULL DEFAULT 'open'
        CHECK (state IN ('open', 'reviewing', 'resolved')),
    version bigint NOT NULL DEFAULT 1 CHECK (version >= 1),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS seller_security_alert_reviews_state_idx
    ON seller_security_alert_reviews (state, updated_at DESC);
COMMIT;
