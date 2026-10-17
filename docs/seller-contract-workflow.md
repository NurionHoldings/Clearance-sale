# Seller membership, listing and contract workflow

## Roles
- Visitor/buyer: browse, authenticated purchase after checkout rollout.
- Seller: authenticated own-profile and own-products CRUD; cannot approve self or edit others.
- Operator: review seller business verification and product moderation; no unlogged financial term changes.
- Contract manager: negotiate and approve seller commission and PG allocation within delegated limits.
- Finance: reconciliation and settlement with maker-checker approval.
- Auditor: read-only immutable audit evidence.

## Onboarding
APPLIED → IDENTITY_REVIEW → CONTRACT_REVIEW → PG_REVIEW → APPROVED; rejection or suspension requires reason and audit event. Verify business identity, legal seller of record, settlement account and authorized representative through approved processes. Seller cannot publish until APPROVED.

## Contracts
Store seller ID, contract version, signed document digest, signature/evidence reference, commission basis (gross/net, discounts, VAT, shipping), effective period, PG provider(s), PG cost responsibility, settlement cycle, reserve/chargeback rules, refund obligations and termination provisions. Preserve prior versions and per-order contract snapshot. Commission is negotiated, not a universal default.

## Product registration
Category must be one of the six ordered categories in `config/marketplace-policy.json`. Require title, photos, description, condition (new/used/refurbished), brand/trademark authorization where applicable, stock, option/SKU, price, shipping/returns, seller ID and moderation status. Apparel and shoes require size/variant fields; helmets/protective rider equipment require relevant safety and certification review. Club-branded merchandise requires trademark/authorization checks.

## Implementation gates
This repository is currently a static demo. Real signup/login, RBAC, product storage, contract signing, PG transactions and seller settlements require a backend, database, authorization, audit and tests. Never use localStorage as authentication or contract authority.
