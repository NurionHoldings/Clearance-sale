-- DRAFT ONLY: seller identity and server-side session schema.
-- Never apply to production without a reviewed migration, RLS and backups.
-- Independent of 001_inventory_contract_draft.sql; no automatic execution.
BEGIN;

CREATE TABLE IF NOT EXISTS seller_accounts (
    user_id uuid PRIMARY KEY,
    password_hash text NOT NULL CHECK (length(password_hash) BETWEEN 20 AND 512),
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'suspended')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS seller_organizations (
    seller_id uuid PRIMARY KEY,
    display_name varchar(200) NOT NULL CHECK (length(btrim(display_name)) > 0),
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'suspended')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS seller_memberships (
    user_id uuid NOT NULL REFERENCES seller_accounts(user_id) ON DELETE RESTRICT,
    seller_id uuid NOT NULL REFERENCES seller_organizations(seller_id) ON DELETE RESTRICT,
    role text NOT NULL CHECK (role IN ('viewer', 'manager', 'owner')),
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'active', 'revoked')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, seller_id)
);

CREATE INDEX IF NOT EXISTS seller_memberships_seller_idx
    ON seller_memberships (seller_id, status);

CREATE TABLE IF NOT EXISTS seller_sessions (
    session_id uuid PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES seller_accounts(user_id) ON DELETE CASCADE,
    token_digest char(64) NOT NULL UNIQUE
        CHECK (token_digest ~ '^[0-9a-f]{64}$'),
    expires_at timestamptz NOT NULL,
    revoked_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT seller_session_expiry_check CHECK (expires_at > created_at),
    CONSTRAINT seller_session_revocation_check
        CHECK (revoked_at IS NULL OR revoked_at >= created_at)
);

CREATE INDEX IF NOT EXISTS seller_sessions_user_idx
    ON seller_sessions (user_id, expires_at);

COMMIT;
