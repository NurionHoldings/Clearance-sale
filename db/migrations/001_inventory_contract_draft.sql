-- Development proposal only. Do not apply to production without review.
-- PostgreSQL 15+; parent seller/product tables and authorization/RLS
-- policies must be designed and installed before operational use.
BEGIN;

CREATE TABLE IF NOT EXISTS inventory_balances (
    seller_id uuid NOT NULL,
    product_id uuid NOT NULL,
    on_hand bigint NOT NULL DEFAULT 0 CHECK (on_hand >= 0),
    reserved bigint NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
    CONSTRAINT inventory_balances_reserved_check CHECK (reserved <= on_hand),
    PRIMARY KEY (seller_id, product_id)
);

CREATE TABLE IF NOT EXISTS inventory_request_receipts (
    seller_id uuid NOT NULL,
    idempotency_key varchar(128) NOT NULL,
    fingerprint char(64) NOT NULL,
    product_id uuid NOT NULL,
    on_hand bigint NOT NULL CHECK (on_hand >= 0),
    reserved bigint NOT NULL CHECK (reserved >= 0),
    version bigint NOT NULL CHECK (version >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT inventory_receipts_reserved_check CHECK (reserved <= on_hand),
    CONSTRAINT inventory_receipts_balance_fk
        FOREIGN KEY (seller_id, product_id)
        REFERENCES inventory_balances (seller_id, product_id),
    PRIMARY KEY (seller_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS inventory_receipts_product_idx
    ON inventory_request_receipts (seller_id, product_id, created_at);

COMMIT;
