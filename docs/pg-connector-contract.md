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
