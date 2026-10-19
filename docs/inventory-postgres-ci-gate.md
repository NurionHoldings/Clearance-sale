# PostgreSQL inventory CI execution gate

The inventory PostgreSQL integration job runs against a **disposable PostgreSQL
16 service** on the GitHub Actions runner. It never requires production DB
credentials. Its URL must resolve to loopback and the database name must contain
`test`, `ci`, or `scratch`.

## Current verification blocker

On 2026-10-19, workflow run 39235487707 was marked failed, but its job
118003420142 exposed **zero step summaries** and its log archive was
unavailable (404 BlobNotFound). This is **not evidence of a failing test**.
Earlier GitHub Actions runs were blocked by account billing. Confirm billing
status and runner availability before diagnosing application code.

1. In GitHub organization/account Billing, resolve the payment/usage issue.
2. Open the draft PR #5 Actions checks and rerun the latest failed workflows.
3. Require the PostgreSQL integration job to execute **all seven** tests with
   no skips; verify the browser and offline safety checks as well.
4. Review logs for a test assertion failure only if the runner actually starts.
5. Keep PR draft and do not merge/deploy until all required checks are green
   and an authorized human approves the release.

The SQL in `db/migrations/001_inventory_contract_draft.sql` remains a
**review-only** migration. No production schema has been applied. Tenant
authorization, DB grants/RLS, identity-type compatibility, operational
migration rollback and backups still need review before production use.
