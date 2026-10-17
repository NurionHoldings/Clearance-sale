# PG provider-neutral connector contract (design, not live integration)

## Goal
Allow competing approved PGs to offer checkout and settlement services without tying marketplace order state to a single provider. Do not route live money until provider-specific contractual and technical review is complete.

## Interfaces
```ts
type PaymentIntent = { orderId:string; amountKRW:number; currency:"KRW"; sellerOfRecordId:string; merchantAccountId:string; idempotencyKey:string };
type VerifiedPayment = { providerId:string; providerTransactionId:string; orderId:string; amountKRW:number; status:"AUTHORIZED"|"PAID"|"CANCELLED"|"PARTIALLY_REFUNDED"|"REFUNDED"; verifiedAt:string };
interface PGConnector {
  readonly providerId:string;
  createPayment(input:PaymentIntent):Promise<{checkoutToken:string;expiresAt:string}>;
  confirmPayment(input:{orderId:string;providerPaymentId:string;expectedAmountKRW:number;idempotencyKey:string}):Promise<VerifiedPayment>;
  fetchPayment(providerPaymentId:string):Promise<VerifiedPayment>;
  refund(input:{providerPaymentId:string;amountKRW:number;reason:string;idempotencyKey:string}):Promise<VerifiedPayment>;
  verifyWebhook(rawBody:Uint8Array,headers:Record<string,string>):Promise<{eventId:string;payment:VerifiedPayment}>;
  capabilities():Promise<{partialRefund:boolean;submerchantPayout:boolean;escrow:boolean;methods:string[]}>;
}
```

## Registry & selection
- Provider onboarding: application → legal/technical review → sandbox tests → operator approval → production credential provisioning.
- Provider offers stored by effective period, fee terms, payment methods, refund support, settlement schedule and service level; no hard-coded preferred PG.
- Show only providers contractually eligible for the specific seller-of-record, product and transaction type. Customer choice may be offered among eligible providers; no misleading 'lowest fee' claim without normalized pricing.
- Lock provider and merchant account on payment intent. Never switch provider after authorization without cancelling/recreating the intent and explicit buyer consent.
- Platform direct sale and third-party marketplace transactions must keep legal seller, merchant-of-record, tax invoice, refund liability and payout responsibilities distinct.

## Invariants
1. Server-side amount and seller-of-record are authoritative; client amount is untrusted.
2. Verify provider credentials, webhook signature/authenticity, event freshness, event uniqueness, order mapping, currency and amount; confirm with provider server-side before PAID.
3. Unique constraints: (provider_id, provider_transaction_id), (provider_id, webhook_event_id), (order_id, payment_attempt_id), refund idempotency.
4. Never treat webhook receipt as sufficient proof of payment; reconcile against provider API and internal immutable ledger.
5. Refund/partial refund cannot exceed captured remaining amount. Payout excludes unsettled, refunded or disputed balances.
6. Encrypt secrets at rest; no secrets or customer payment data in frontend, GitHub or ARKAON shared knowledge.
7. Fail closed on unavailable provider and record retryable reconciliation tasks; use transactional outbox for external side effects.
8. Contract commission versions are effective-dated and snapshotted per order; PG cost, marketplace commission, seller proceeds and taxes are separate accounting dimensions.
9. Multi-seller basket requires legal and PG support review before split payments or payouts.
10. No live checkout until security, contract, financial reconciliation, refund and failure-injection tests PASS.

## Provider adapters proposed
- `toss-payments`: sandbox adapter after contract and API specification review.
- `nhn-kcp`: REST and payout capabilities evaluated separately; certificate/private key custody required.
- `kg-inicis`: candidate; official product-specific APIs and merchant agreements require verification.
- `mock`: deterministic test-only adapter, never production enabled.

## Evidence for ARKAON
Each adapter must ship capability manifest, versioned spec references, contract eligibility, test vectors, webhook replay tests, timeout/retry tests, refund and reconciliation proofs, and ETERNIAN review packet.

## Status
Specification only. No real PG connector or payment processing is implemented.


## Seller-selected PG — binding product decision (2026-10)
- **The seller, not the platform, selects a PG from the approved provider registry.** The platform acts as a technical integration broker, subject to applicable contractual permissions. Platform operators may approve connector security/compliance but may not silently override the seller's choice.
- Seller portal displays comparable provider terms with effective dates, eligibility, supported payment methods, fees and settlement conditions. Figures must be provider-confirmed and labeled when indicative.
- Seller initiates connection to selected provider, completes the PG's own merchant agreement and underwriting, then authorizes a merchant-account binding. Never treat clicking a provider as PG approval.
- Store `seller_pg_connections(seller_id, provider_id, merchant_account_ref, status, effective_at, verified_at, credential_reference, terms_version)`. Suggested states: `SELECTED -> CONTRACT_PENDING -> PG_REVIEW -> CREDENTIALS_PENDING -> TESTING -> ACTIVE`, plus `SUSPENDED/REVOKED/FAILED`.
- Each seller listing/order resolves the **seller's active PG connection**; platform direct-sale orders use the platform's own separate PG merchant connection. Reject checkout if connection inactive or payment method unsupported.
- Seller may request PG change, but it takes effect only for new payment intents after validation; existing orders/refunds stay pinned to their original provider and merchant account.
- Platform commission agreement remains separate from seller-PG fees and settlement agreement. Never assume the platform is entitled to intercept seller proceeds or conduct submerchant payouts.
- Multi-seller cart: separate orders and payment attempts per legal seller/PG unless a specifically reviewed PG product supports a lawful multi-merchant flow.
- The PG connector directory is open to qualified providers under published, non-discriminatory technical onboarding requirements; security, compliance and capability review remain mandatory.
