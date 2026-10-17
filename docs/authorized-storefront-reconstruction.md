# ARKAON authorized storefront reconstruction — proposal

## Decision
Seller may opt to authorize ARKAON to inspect the seller's existing storefront and reconstruct an independently operated seller shop **inside Clearance-sale**. The destination uses Clearance-sale product, cart, order and seller-selected PG checkout; no external checkout dependency. This supplements, rather than reverses, the hosted-only storefront decision.

## Authorization and rights
- Seller signs scoped import consent identifying source domains, admin authority, import scope, permissible APIs, ownership/license of photos/text/branding and revocation/retention terms.
- Verify seller control of source domain and authority to export. Do not assume seller owns a licensed hosted theme, proprietary storefront code, third-party photography, reviews or customer records.
- Prefer official platform APIs, owner-provided exports (CSV/JSON/images), or authorized accessible public pages. Respect API terms and rate limits. No access-control bypass, credential harvesting or anti-bot circumvention.
- Do not copy customers, orders, passwords, payment data, or personal information into the new store by default. Handle any permitted personal-data migration as a separately reviewed workflow.
- Rebuild page layout with original code and approved assets; avoid unlicensed pixel-perfect cloning. Record provenance and license evidence per imported asset.

## Workflow
1. Seller enters source URL, platform type, signed authorization, scope and asset rights.
2. ARKAON produces compatibility and licensing assessment; classify official API, export, approved HTML analysis, or unsupported HOLD.
3. Import into quarantine staging; validate file types, malware, HTML/script injection, image ownership, duplicates, SKUs, stock, variants, prices, tax/shipping and prohibited products.
4. Generate a seller-specific theme and normalized product catalog in a **draft hosted shop** with provenance map and before/after preview. Never execute source scripts in destination.
5. Seller reviews images, prices, inventory, brand, disclosures, shipping/return terms and signs approval.
6. Run storefront mobile/accessibility tests, tenant isolation, order/PG sandbox payment/refund and security checks.
7. ETERNIAN audits evidence; operator approves publication and provides rollback to prior version.
8. Optional incremental product sync only through official authorized APIs with conflict detection; source and destination inventory authority must be explicit.

## Proposed entities
`storefront_import_jobs` (seller_id, source_domain, scope, consent_version, source_platform, state, created_at)
`import_assets` (job_id, source_ref, license_status, digest, approved_by)
`import_products` (job_id, source_sku, destination_sku, conflict_status, validation_result)
`storefront_themes` (seller_id, version, asset_refs, preview_url, approved_at)
`import_audit_events` (job_id, actor, decision, evidence_digest)

State: REQUESTED -> AUTH_VERIFIED -> RIGHTS_REVIEW -> ANALYZING -> STAGING -> SELLER_REVIEW -> SANDBOX_VERIFIED -> ETERNIAN_AUDIT -> APPROVED -> PUBLISHED; FAILED/HOLD/REVOKED supported.

## Acceptance
- Source access and asset rights evidenced.
- No customer/payment secrets ingested.
- Imported catalog passes owner review and stock/price validation.
- Hosted checkout uses selected PG and own seller merchant account; external source remains separate.
- Full test/audit/rollback proof; no auto-publication.

Status: specification only; no real import engine, crawling, theme generation or deployment implemented.
