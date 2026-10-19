-- Draft PostgreSQL schema for isolated integration testing only.
-- NOT applied to any database. Review migration, privileges and backup plan first.
CREATE TABLE IF NOT EXISTS inventory_balances (
    seller_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    on_hand BIGINT NOT NULL CHECK (on_hand >= 0),
    reserved BIGINT NOT NULL CHECK (reserved >= 0 AND reserved <= on_hand),
    version BIGINT NOT NULL DEFAULT 0 CHECK (version >= 0),
    PRIMARY KEY (seller_id, product_id)
);

CREATE TABLE IF NOT EXISTS inventory_request_receipts (
    seller_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL,
    fingerprint CHAR(64) NOT NULL,
    product_id TEXT NOT NULL,
    on_hand BIGINT NOT NULL CHECK (on_hand >= 0),
    reserved BIGINT NOT NULL CHECK (reserved >= 0 AND reserved <= on_hand),
    version BIGINT NOT NULL CHECK (version >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (seller_id, idempotency_key),
    FOREIGN KEY (seller_id, product_id)
        REFERENCES inventory_balances (seller_id, product_id)
);
