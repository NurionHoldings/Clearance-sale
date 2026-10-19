# Seller inventory: demo-to-production architecture (design only)

Status: **DESIGN / NOT IMPLEMENTED / NOT DEPLOYED**. The current seller dashboard is local mock data, without authentication, network calls, persistence, payment, or real seller actions. No production credentials or migrations are introduced here.

## Trust boundary and identity

- Authenticate with a server-side session (HttpOnly, Secure, SameSite cookie) and CSRF protection for state-changing operations. Enforce MFA for privileged operator accounts.
- Derive `seller_id` exclusively from the verified server session and current membership. Never trust a seller ID, role, inventory owner, or price supplied by a browser.
- Require explicit authorization for every product, inventory, reservation, order, and export operation; default-deny inactive sellers and cross-tenant access. Audit privilege changes.
- Keep operator, seller, and customer roles separate. A seller may manage only their own catalog. Operator overrides need a distinct audited path.

## Proposed relational model (subject to review)

- `sellers(id, status, created_at)`
- `seller_memberships(user_id, seller_id, role, status)`
- `products(id, seller_id, sku, name, price_won, active, version, created_at, updated_at)`; unique constraint on `(seller_id, sku)` after defining SKU normalization and case policy.
- `inventory_balances(product_id, on_hand, reserved, version, updated_at)`; check `on_hand >= 0 AND reserved >= 0 AND reserved <= on_hand`.
- `inventory_movements(id, product_id, actor_id, reason, delta_on_hand, delta_reserved, idempotency_key, created_at)`; immutable audit trail, with unique idempotency scope.
- `orders` and `order_items` must be designed separately with payment and settlement review; not part of this phase.

## Read API (proposed, not active)

`GET /api/seller/inventory?status=all&search=&sort=sku_asc&page_size=25&cursor=...`

- Resolve tenant from session; query only its products; enforce page size and allowlisted sort/filter names.
- Return versioned schema, server-derived available quantities and snapshot timestamp. No secrets, other sellers' data, or hidden operator fields.
- Prefer stable keyset pagination with deterministic tie-breaking, server-side search, and bounded response size. Add rate limiting and request tracing.

## Mutations (not active)

- Product registration: validated server-side; unique SKU enforced by database transaction, not preview-only duplicate check.
- Inventory adjustment/reservation/release: atomic transaction with row lock or compare-and-swap version, constraints, idempotency key, and audit event. Never allow negative available stock.
- Order/payment integrations require separate provider validation, webhook signature verification, replay protection, reconciliation, refunds, and operator approval.
- Export/download endpoints need tenant scoping, size limits, escaping of spreadsheet formula injection, and explicit authorization.

## Release gates

1. Review requirements, privacy/retention, threat model, schema migration/rollback, backups, and access policies.
2. Add isolated DB integration tests for tenant isolation, duplicate SKU race, concurrent reservations, idempotent retries, and authorization failures.
3. Test accessibility/mobile workflows, logging redaction, rate limits, and failure/recovery.
4. Configure GitHub branch protection with mandatory CI and independent approval; **resolve the current GitHub Actions billing blocker first**.
5. Stage behind disabled-by-default feature flag, verify with synthetic data, and obtain explicit operator approval before production rollout.

## Intent_DNA acceptance criteria

- **Intent:** seller can view their own inventory, never another seller's.
- **Data:** one authoritative balance, auditable movements, no browser-supplied authority.
- **Safety:** preview remains read-only until authenticated backend, DB transactions, and release gates are independently verified.
- **Evidence:** failing security/concurrency tests block release; absence of CI execution is not success.
