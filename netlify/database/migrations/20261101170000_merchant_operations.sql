CREATE TABLE ops_write_lock (id integer PRIMARY KEY CHECK(id=1));
INSERT INTO ops_write_lock VALUES(1);
CREATE TABLE ops_merchants (
 id uuid PRIMARY KEY, owner_id text NOT NULL UNIQUE, data jsonb NOT NULL,
 verified boolean NOT NULL DEFAULT false, payout_reference text,
 revision integer NOT NULL DEFAULT 1, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_contract_previews (
 id uuid PRIMARY KEY, merchant_id uuid NOT NULL REFERENCES ops_merchants(id), actor_id text NOT NULL,
 payload jsonb NOT NULL, document_text text NOT NULL, document_hash text NOT NULL, created_at timestamptz NOT NULL
);
CREATE TABLE ops_contracts (
 id uuid PRIMARY KEY, merchant_id uuid NOT NULL REFERENCES ops_merchants(id),
 version integer NOT NULL, status text NOT NULL CHECK(status IN ('issued','signed','void')),
 payload jsonb NOT NULL, document_text text NOT NULL, document_hash text NOT NULL,
 provider_signature jsonb NOT NULL, merchant_signature jsonb, signed_hash text,
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(merchant_id,version)
);
CREATE TABLE ops_read_receipts (
 id uuid PRIMARY KEY, contract_id uuid NOT NULL REFERENCES ops_contracts(id),
 actor_id text NOT NULL, document_hash text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_evidence (
 id uuid PRIMARY KEY, name text NOT NULL, mime text NOT NULL, data bytea NOT NULL,
 sha256 text NOT NULL, actor_id text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_ledger (
 id uuid PRIMARY KEY, contract_id uuid NOT NULL REFERENCES ops_contracts(id),
 kind text NOT NULL CHECK(kind IN ('sale','refund')), parent_id uuid REFERENCES ops_ledger(id),
 provider text NOT NULL, reference text NOT NULL, gross bigint NOT NULL CHECK(gross>0),
 shipping bigint NOT NULL CHECK(shipping>=0 AND shipping<=gross), pg_fee bigint NOT NULL,
 confirmed_at timestamptz NOT NULL, evidence_id uuid NOT NULL REFERENCES ops_evidence(id),
 status text NOT NULL CHECK(status IN ('pending','verified')), verified_by text,
 created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(provider,reference),
 CHECK((kind='sale' AND parent_id IS NULL AND pg_fee>=0) OR (kind='refund' AND parent_id IS NOT NULL))
);
CREATE TABLE ops_batches (
 id uuid PRIMARY KEY, contract_id uuid NOT NULL REFERENCES ops_contracts(id),
 status text NOT NULL CHECK(status IN ('draft','reviewed','approved','requested','cancelled')),
 snapshot jsonb NOT NULL, content_hash text NOT NULL, approval jsonb,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_batch_lines (
 ledger_id uuid PRIMARY KEY REFERENCES ops_ledger(id), batch_id uuid NOT NULL REFERENCES ops_batches(id)
);
CREATE TABLE ops_reviews (
 id uuid PRIMARY KEY, batch_id uuid NOT NULL REFERENCES ops_batches(id),
 content_hash text NOT NULL, report jsonb NOT NULL, ai_note jsonb, actor_id text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_payout_requests (
 id uuid PRIMARY KEY, batch_id uuid NOT NULL UNIQUE REFERENCES ops_batches(id),
 amount bigint NOT NULL CHECK(amount>0), payee jsonb NOT NULL, content_hash text NOT NULL,
 requested_by text NOT NULL, status text NOT NULL DEFAULT 'requested' CHECK(status='requested'),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE ops_audit (
 seq bigserial PRIMARY KEY, actor_id text NOT NULL, action text NOT NULL, entity_id uuid NOT NULL,
 digest text NOT NULL, previous_hash text NOT NULL, event_hash text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
