# Seller security CI gate

The draft PR runs `.github/workflows/seller-security-offline.yml` against
nine isolated unittest modules. This is a Python-only, network-free check
covering identity resolution, seller membership, cross-tenant inventory scope,
default-deny inventory mutations, safe public errors, bounded diagnostics and
reporter failure handling.

The workflow fails if any test fails, any test is skipped, or fewer than 20
tests execute. This is a floor, not an exact count; new tests can be added
without weakening the gate. No database credentials or production access are
required.

## Before merging

1. Restore GitHub Actions runner execution if billing prevents jobs starting.
2. Confirm the seller security workflow is green on the final PR commit.
3. Confirm the PostgreSQL integration, browser E2E and existing offline
   verification workflows are green on that same commit.
4. Configure repository branch protection / rulesets to require the relevant
   checks. Merely naming a job "required" does not enforce branch protection.
5. Obtain explicit human approval before merging or deploying.

This workflow does not authenticate a real user, configure an HTTP endpoint,
enable inventory writes, connect a production database, or deploy anything.

## Regression review (2026-10-19)

The cross-tenant session test previously expected the internal
`InventoryScopeError`, although the public dashboard boundary intentionally
maps it to `SellerAccessDenied("Seller dashboard unavailable")` and removes the
original exception cause. The test now checks the public security contract.
This is a source-level correction, **not** a claim that CI passed. Recent
GitHub Actions jobs showed zero executed steps; runner/billing remediation and
fresh green checks remain prerequisites for merge.
