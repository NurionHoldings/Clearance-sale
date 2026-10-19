-- DRAFT ONLY. Distributed login throttling using PostgreSQL atomic UPSERT.
-- Apply only after database review; never run automatically.
BEGIN;
CREATE TABLE IF NOT EXISTS seller_login_attempt_buckets (
    bucket_digest char(64) PRIMARY KEY
        CHECK (bucket_digest ~ '^[0-9a-f]{64}$'),
    window_start timestamptz NOT NULL,
    attempts integer NOT NULL CHECK (attempts BETWEEN 1 AND 100000),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS seller_login_attempt_buckets_expiry_idx
    ON seller_login_attempt_buckets (window_start);
COMMIT;
