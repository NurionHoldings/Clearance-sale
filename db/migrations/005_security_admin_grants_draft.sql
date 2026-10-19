-- DRAFT ONLY. Separate security administrator grants from seller memberships.
-- Never execute automatically; review migrations and grant assignment first.
BEGIN;
CREATE TABLE IF NOT EXISTS security_admin_grants (
    user_id uuid PRIMARY KEY REFERENCES seller_accounts(user_id) ON DELETE CASCADE,
    role text NOT NULL CHECK (role = 'security_admin'),
    active boolean NOT NULL DEFAULT false,
    granted_at timestamptz NOT NULL DEFAULT now(),
    revoked_at timestamptz,
    CHECK (NOT active OR revoked_at IS NULL)
);
CREATE INDEX IF NOT EXISTS security_admin_grants_active_idx
    ON security_admin_grants (active) WHERE active = true;
COMMIT;
