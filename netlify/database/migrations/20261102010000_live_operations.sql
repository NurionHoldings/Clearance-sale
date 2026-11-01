-- Persist external operations before calling the gateway; retries reuse the same order/key.
CREATE TABLE live_invoices (
 id uuid PRIMARY KEY,
 booking_id uuid NOT NULL REFERENCES live_bookings(id),
 order_id text NOT NULL UNIQUE,
 amount_won bigint NOT NULL CHECK(amount_won > 0 AND amount_won <= 100000000),
 quote_version integer NOT NULL,
 quote_snapshot jsonb NOT NULL,
 mode text NOT NULL CHECK(mode IN ('test','live')),
 status text NOT NULL CHECK(status IN ('created','confirming','paid','refund_pending','refunded','void')),
 payment_key text UNIQUE,
 provider_status text,
 receipt_url text,
 approved_at timestamptz,
 refund_reason text,
 last_checked_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX live_one_active_invoice ON live_invoices(booking_id) WHERE status<>'void';
ALTER TABLE live_broadcasts ADD COLUMN provider_check jsonb;
