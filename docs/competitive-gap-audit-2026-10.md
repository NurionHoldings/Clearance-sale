# Competitive benchmark and gap audit — 2026-10-12

## Evidence (official product documentation)
- Shopify multi-location inventory and POS: https://help.shopify.com/en/manual/inventory-and-locations/setup/multi-managed-inventory ; https://www.shopify.com/pos/features
- Shopify staff/order/refund notifications: https://help.shopify.com/en/manual/fulfillment/setup/notifications
- Cafe24 multichannel product/stock automation: https://support.cafe24.com/hc/ko/articles/62707183903897-상품-자동등록-수정-재고-설정하기
- Amazon Seller Central seller app, order/inventory/health: https://sell.amazon.com/tools/seller-central
- Mirakl onboarding/catalog mapping, multi-vendor routing, commission and payouts: https://www.mirakl.com/products/marketplace-platform/ ; https://www.mirakl.com/products/payout/
These are feature comparisons, not claims that Clearance-sale already implements them.

## Product position
Hybrid first-party and seller marketplace, platform-hosted seller-specific storefronts, seller-authorized reconstruction of existing catalog/design, consent-based inventory integration to external source shop, seller-selected approved PG offering, seller mobile alerts. External shop checkout hijacking/forced redirection is explicitly out of scope. Six categories retain their defined order.

## Critical gaps and gates
| Priority | Capability | Acceptance gate |
| P0 | Identity/RBAC/tenant isolation | Seller, PG provider, buyer, staff and platform admin access proven in negative tests; deny cross-tenant reads/writes |
| P0 | Financial ledger and settlement | Immutable order/payment/refund/commission snapshots, double-entry-style reconciliation, duplicate webhook/capture tests; merchant-of-record and PG legal review |
| P0 | Inventory safety | SKU/variant mapping, authoritative SoT, atomic reserve or dedicated stock allocation, webhook replay and stale stock fail-closed |
| P0 | Order and fulfillment | Shipping fees, carrier/tracking, partial shipment, cancellation, return/exchange/dispute, customer support case and SLA |
| P0 | Trust & safety | Seller business verification, counterfeit/IP complaints, prohibited listings, moderation audit, product origin/labeling and recalls |
| P0 | Security/privacy | Secure auth/session, encryption, secrets vault, audit logs, privacy retention/deletion, consent versioning, backups/restore, vulnerability/abuse/rate tests |
| P0 | Consumer and tax compliance | Seller identity/merchant-of-record disclosure, terms, privacy policy, electronic commerce notice, tax invoice/receipt obligations reviewed by counsel/accountant |
| P1 | Authorized storefront reconstruction | Rights provenance, source authorization, staging preview, seller approval, clean independent code and asset license audit |
| P1 | Mobile seller operations | Verified paid-order push, stock threshold alerts, in-app dashboard, delivery retry, privacy-safe lock-screen content |
| P1 | Bulk operations | CSV/API import/export, category mapping, option validation, duplicate SKU detection, exception queue |
| P1 | Seller-PG choice | PG company onboarding, published offers, merchant underwriting, server connector certification, changeover preserving existing payment PG |
| P1 | Operational observability | Metrics, tracing, alerting, incident response, backup/restore drill, rollback, admin audit dashboard |
| P2 | Growth | Promotions, coupons, search ranking, seller analytics, abandoned-cart recovery subject to consent |

## Explicit architectural questions before implementation
1. Who is merchant of record for first-party vs third-party seller orders? How are PG funds settled without unauthorized fund custody?
2. Which inventory source guarantees atomic reservation for each seller? If none, require allocated stock.
3. What is the cancellation/refund/returns liability matrix by seller, PG and platform?
4. Which storefront platforms and official APIs are first integration targets? Broad analysis is a goal, not a guarantee of universal migration.
5. What constitutes a publishable seller shop: seller verification, authorized assets, live PG, inventory gate, shipping/returns policies, seller sign-off?

## Suggested execution order
Milestone 0: inspect repo and write current implementation coverage matrix, test baseline and threat model.
Milestone 1: server auth, DB migrations, seller/PG provider onboarding and tenant RBAC.
Milestone 2: hosted seller shop catalog/variants/inventory and source sync mock with concurrency tests.
Milestone 3: cart/order/PG sandbox, refunds and reconciliation.
Milestone 4: mobile PWA alerts, reconstruction pipeline and import preview.
Milestone 5: shipping/returns, trust & safety, legal and financial audit, E2E, limited pilot.

## Release discipline
No live money, seller personal data import, automated deployment, PR merge or claim of production readiness until CI, security, finance and ETERNIAN review plus operator approval. All existing docs/config are design, not proof of implementation.
