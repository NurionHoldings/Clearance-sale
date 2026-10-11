# Seller external-store inventory synchronization — binding design

Status: APPROVED BUSINESS DIRECTION; implementation and production remain HOLD.

## Goal
The seller continues operating their original storefront alongside the Clearance-sale-hosted shop. Inventory for the same physical SKU/variant is synchronized automatically using authorized official APIs/webhooks where supported. Checkout always occurs within the hosted Clearance-sale store using the seller-selected onboarded PG.

## Authority and consistency
- At onboarding, identify a **single inventory source of truth (SoT)** per seller/warehouse/SKU. Default: seller's existing inventory system or original storefront **only when it supports safe reservations/updates**; otherwise require a dedicated stock allocation for Clearance-sale or a supported inventory management integration.
- Maintain explicit `seller_id + external_store_id + external_variant_id ↔ internal_variant_id` mapping, SKU normalization, option/size/color mapping, warehouse and available/reserved/damaged counts.
- Available-to-sell = authoritative on_hand minus reservations minus safety_stock, with nonnegative invariant. Do not equate stale display count with reservable stock.
- External webhook → signature/auth verification → deduplicated durable event inbox → ordered/version-aware processing → reconcile against SoT → update projection.
- Clearance-sale order → atomically reserve stock at SoT (or dedicated allocated stock) BEFORE payment capture; use short-lived holds, idempotency, compensation on payment failure/cancel/timeout, and reconciliation for uncertain outcomes.
- If external platform cannot guarantee atomic reservation, **shared-pool zero-oversell cannot be guaranteed**. Use seller-approved fixed allocation or fail-closed/unpublish until stock can be confirmed.
- Handle returns, cancellation, partial fulfillment, bundles, variants, warehouse transfers, external sales, oversell disputes and manual adjustments. Never blindly increment stock on refund before physical restock approval.
- Schedule polling reconciliation where webhooks unavailable; rate limits, eventual consistency and outage budgets are explicit per connector. Alert on drift and suspend affected SKUs on stale/untrusted stock.
- Seller may inspect stock sync status, mismatches, recent events, last successful sync and request safe resync. Manual overrides require authorized role, reason and immutable audit event.
- Never ingest external shop credentials into ARKAON knowledge; use vault references, scoped tokens, least privilege, encrypted transport and rotation.

## Connector contract (proposed)
```ts
interface InventoryConnector {
  providerId: string;
  capabilities(): Promise<{webhooks:boolean;atomicReservation:boolean;stockWrite:boolean;variantInventory:boolean}>;
  fetchVariants(cursor?:string):Promise<{items:ExternalVariant[];nextCursor?:string}>;
  fetchStock(variantId:string):Promise<{onHand:number;reserved:number;version:string;observedAt:string}>;
  reserve(input:{variantId:string;quantity:number;idempotencyKey:string;expectedVersion?:string}):Promise<{reservationId:string;expiresAt:string}>;
  commitReservation(reservationId:string,orderId:string):Promise<void>;
  releaseReservation(reservationId:string,idempotencyKey:string):Promise<void>;
  verifyWebhook(raw:Uint8Array,headers:Record<string,string>):Promise<VerifiedInventoryEvent>;
}
```
Capability-gate unsupported operations; no simulated success. Where external reserve is unavailable, use dedicated stock allocations, not a fake connector method.

## Proposed data model
`inventory_connections` (seller_id, platform, source_of_truth, status, token_vault_ref, last_verified_at)
`inventory_variant_mappings` (seller_id, external_variant_id, internal_variant_id, warehouse_id, mapping_version)
`inventory_snapshots` (variant_id, on_hand, reserved, safety_stock, source_version, observed_at)
`inventory_reservations` (seller_id, order_id, variant_id, qty, state, external_reservation_ref, expires_at, idempotency_key)
`inventory_events` (connection_id, external_event_id, source_version, received_at, processed_at, outcome)
`inventory_reconciliation_runs` (connection_id, started_at, completed_at, drift_count, action, evidence_digest)

## ARKAON work plan
1. Inspect seller-authorized store API and inventory capabilities; classify ATOMIC_SHARED_STOCK / DEDICATED_ALLOCATION / POLLING_LIMITED / UNSUPPORTED_HOLD.
2. Build sandbox-only adapters and deterministic event/replay tests; do not scrape credentials or bypass storefront terms.
3. Generate seller-facing SKU mapping review, conflict report, stock synchronization dashboard and alert policy.
4. Test concurrent purchases across two storefronts, webhook duplication/out-of-order delivery, external outages, inventory rollback, refunds and reconciliation.
5. Submit implementation PR + test evidence for ETERNIAN audit and operator approval before release.

## Acceptance gates
- Seller-authorized integration, mapping verification, explicit SoT and stock reservation semantics.
- Proved idempotency, concurrent-order safety, compensation and reconciliation; otherwise allocated stock with safety controls.
- Monitoring, operator override logs and rollback tested.
- No claim of universal real-time synchronization where third-party API capability is absent.
