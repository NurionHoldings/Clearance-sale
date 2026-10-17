# Seller mobile sales and inventory notifications

Status: operator-required capability, specification only. No live push infrastructure is deployed.

## Goal
Every approved seller can view up-to-date **Clearance-sale sales and stock status** on their phone, and opt into immediate alerts for material events. The authoritative values are seller-scoped backend order/payment and inventory ledgers, not demo browser localStorage.

## Event triggers
- PAYMENT_CONFIRMED (verified server-side PG confirmation): new paid order, items, quantity, amount, action link.
- PAYMENT_CANCELLED / REFUND_CONFIRMED: update net sales and order state.
- INVENTORY_LOW / OUT_OF_STOCK / RESTOCKED: per-variant configurable threshold, stock state transitions.
- INVENTORY_SYNC_FAILED / STALE / RECOVERED: original-store connection health and fail-closed selling state.
- Optional daily summary: orders, gross paid sales, refunds, net paid sales, items sold, stock exceptions.

## Delivery architecture
- Payment/inventory transaction commits an outbox event; worker delivers after commit. Never send on unverified client checkout success.
- Seller account owns notification preferences and one or more registered devices; authenticated device registration, token rotation, revocation and logout invalidation.
- Mobile responsive seller dashboard plus installable PWA with permission-based Web Push (service worker, VAPID and push subscription). Support platform/browser limitations, including iOS install/permission requirements; no promise of delivery to all devices or exact zero-latency.
- SMS/Kakao business notifications only via approved providers and templates, explicit applicable consents, per-message costs and fallback rules. Avoid duplicate notifications across retries.
- Seller-only access with tenant isolation; no customer name/address/phone or payment credentials in lock-screen push. Sensitive details require authenticated app access.
- Push worker: durable queue, idempotent event key, exponential backoff, dead-letter and audit logs, delivery states SENT/FAILED/ACKED where available. Browser push acceptance is not proof of user viewing.
- Threshold deduplication and cooldown prevent repeated low-stock spam; stock recovery resets warning.
- Realtime authenticated dashboard updates through SSE/WebSocket or bounded polling; show 'last updated' and sync freshness; stock source of truth remains inventory integration policy.
- Revenue figures distinguish paid gross, cancelled/refunded and net amounts. Seller settlement receivable is separate from gross revenue.

## Proposed entities
`seller_notification_preferences` (seller_id, event_type, push_enabled, fallback_channel, threshold, quiet_hours)
`seller_push_subscriptions` (seller_id, user_id, endpoint_hash, encrypted_subscription, device_label, revoked_at)
`seller_notification_events` (seller_id, source_event_id, event_type, payload_redacted, created_at)
`seller_notification_deliveries` (event_id, channel, attempt, status, next_attempt_at)
`seller_stock_alert_thresholds` (seller_id, variant_id, low_stock_qty, cooldown)

## Acceptance and safety tests
- Paid-order alert only after verified PG confirmation; duplicate webhooks cause one logical alert.
- Two seller accounts never see each other's orders, counts, stock or device subscriptions.
- Logout/revocation stops new delivery to that device.
- Refund updates daily net figures without double counting.
- Low-stock crossing triggers once per state transition; recovered stock clears alert.
- External inventory outage creates sync failure warning and safe selling status.
- Web Push unsupported/permission denied handled without blocking seller dashboard.
- ETERNIAN audit and operator approval before live rollout.
