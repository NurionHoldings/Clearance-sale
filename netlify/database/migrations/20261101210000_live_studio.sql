CREATE TABLE live_studios (
 id uuid PRIMARY KEY, name text NOT NULL, description text NOT NULL, address text NOT NULL,
 equipment jsonb NOT NULL, buffer_minutes integer NOT NULL CHECK(buffer_minutes BETWEEN 0 AND 180),
 active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE live_bookings (
 id uuid PRIMARY KEY, studio_id uuid NOT NULL REFERENCES live_studios(id), merchant_id uuid NOT NULL REFERENCES ops_merchants(id),
 contract_id uuid NOT NULL REFERENCES ops_contracts(id), starts_at timestamptz NOT NULL, ends_at timestamptz NOT NULL,
 purpose text NOT NULL, status text NOT NULL CHECK(status IN ('requested','quoted','confirmed','rejected','cancelled','completed')),
 quote_won bigint CHECK(quote_won>=0), quote_note text, quote_version integer NOT NULL DEFAULT 0,
 accepted_quote jsonb, decision_note text, created_at timestamptz NOT NULL DEFAULT now(), CHECK(ends_at>starts_at)
);
CREATE UNIQUE INDEX live_booking_no_duplicate ON live_bookings(merchant_id,studio_id,starts_at) WHERE status IN ('requested','quoted','confirmed');
CREATE TABLE live_broadcasts (
 id uuid PRIMARY KEY, booking_id uuid NOT NULL UNIQUE REFERENCES live_bookings(id),
 title text NOT NULL, description text NOT NULL, youtube_id text NOT NULL DEFAULT '', products jsonb NOT NULL DEFAULT '[]',
 host_name text NOT NULL DEFAULT '', producer text NOT NULL DEFAULT '', replay_allowed boolean NOT NULL DEFAULT false,
 status text NOT NULL CHECK(status IN ('draft','scheduled','live','ended','cancelled')),
 checklist jsonb NOT NULL DEFAULT '{}', verification jsonb, revision integer NOT NULL DEFAULT 1,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX live_booking_calendar ON live_bookings(studio_id,starts_at,ends_at) WHERE status='confirmed';
