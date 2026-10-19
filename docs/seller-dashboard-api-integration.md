# Seller dashboard API integration contract

Draft design only. No live route, authentication service, or database is connected.

## Proposed endpoint

GET /api/seller/dashboard

Authentication middleware must establish a verified server-side session. The
server resolves the seller membership from a trusted store. Do not accept
browser-provided seller ownership as proof of authorization.

The endpoint must invoke the existing seller_dashboard_read_response boundary.
Return its JSON snapshot only after seller authorization and tenant-scoped
inventory validation. Return a generic error response on denial. Disable
response caching. Allow GET only; never expose inventory mutation methods.

## Deployment gate

Add tests for unauthorized access, cross-tenant inventory, and error leakage
before attaching a real HTTP route. GitHub Actions remains blocked, so do not
merge this draft PR or deploy without fresh successful checks and approval.
