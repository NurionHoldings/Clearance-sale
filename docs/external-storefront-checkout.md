# External seller storefront referral-to-checkout integration (PROPOSED)

## Business objective
Seller showcases a small number of products on Clearance-sale and links to a larger catalog on their existing storefront. If the buyer originated from Clearance-sale, route **eligible attributable orders** through the seller's chosen approved PG connector, and record contractual referral commission. This requires seller and storefront operator consent and checkout platform capability; the platform cannot technically force payment on an unrelated or unintegrated website.

## Recommended supported modes
1. SELLER_PLUGIN: install a signed, reviewed plugin on a compatible seller storefront. On landing, exchange a short-lived signed referral token for a server-side attribution record. On checkout, the plugin requests an eligible seller PG payment intent through Clearance-sale. No arbitrary browser injection.
2. HOSTED_CHECKOUT: storefront transfers a server-signed cart snapshot to Clearance-sale checkout. Server revalidates SKU, inventory, price, seller identity, shipping, tax and buyer consent. Return verified payment result to seller store using authenticated webhook.
3. HOSTED_STOREFRONT: optional Clearance-sale-hosted catalog and checkout for sellers without compatible infrastructure.
4. TRACK_ONLY: if technical checkout control is impossible, show referral attribution and settlement reporting only. Do not falsely promise forced PG routing.

## Required integration contract
- Seller explicitly authorizes which domain(s), storefront software, orders and PG connections are in scope.
- Storefront integration adapter has signed release artifacts, least-privilege credentials, opt-in installation and uninstall/rollback.
- Referral token fields: opaque referral_id, seller_id, campaign_id, issued_at, expires_at, nonce, audience and signature. Avoid embedding buyer PII. Validate host domain and prevent open redirects.
- First-party server-side attribution preferred. Cookie consent and privacy notices required where applicable. Cross-domain browser tracking may fail due to privacy controls; never claim 100% attribution.
- Attribution terms define eligible order, window, exclusions, repeat visits, returns, cancellation and disputes; snapshot commission agreement at order creation.
- Do not route an unrelated seller's orders or an order already bound to another PG. Merchant of record and PG contract must support the proposed flow.
- Checkout amount comes from seller server and is revalidated against product/stock/tax/shipping rules. The PG response is server-verified; webhook replay and double capture are prevented.
- Separate payment PG fees, Clearance-sale referral fee, and marketplace sales commission. Avoid double charging and define fee hierarchy.
- Buyer must see actual seller, applicable PG/payment terms and where checkout takes place. No deceptive redirection or payment lock-in.
- External shopping cart mixing referral and non-referral products needs explicit policy and integration capability; unsupported mixed baskets fail safely or split with buyer confirmation.

## Integration lifecycle
Storefront registration -> domain ownership proof -> plugin capability check -> seller consent -> ARKAON compatibility analysis -> adapter proposal -> sandbox end-to-end -> ETERNIAN security/contract audit -> operator approval -> limited rollout -> monitoring/rollback.

## Tests
Signed referral token forgery/expiry/replay, open redirect, cross-seller leakage, same-order duplicate callbacks, tampered cart amount, PG outage, seller changing PG mid-order, refunds to original PG, third-party cookie blocking, plugin uninstall, unauthorized external-domain linking.

## Implementation status
Design only. No external site can be modified, and no external checkout can be forced without installation/consent and compatible APIs.
