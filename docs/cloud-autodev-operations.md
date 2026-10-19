# Cloud automatic development — phase 1
## Implemented
GitHub-hosted scheduled verification runs twice daily and on pull requests targeting main. It runs available Python unit tests, syntax checks and verifies production release gates. No customer data, payment, or deployment is touched.

## Not yet implemented
An autonomous coding agent is **not** installed or authorized by this workflow. Recurring verification alone does not write features, create PRs or complete the marketplace. An agent requires an explicit provider, secure credentials, spending limit, isolated execution environment and an audited task queue.

## Required operator setup
1. Repository Settings > Actions > General: enable GitHub Actions and allow the approved actions.
2. Merge the infrastructure PR after review. Actions defined on a feature branch may not be scheduled until they exist on the default branch.
3. Configure branch protection, required test checks, least-privilege tokens, concurrency and budget alerts.
4. Choose an AI coding agent provider and set its credentials via GitHub Actions secrets or a cloud secret manager. Never paste secrets in issues, logs or code.
5. Approve bounded work items in issues with clear acceptance criteria and implement agent workflow in a separate reviewed PR.

## Safety
Do not auto-merge changes touching payments, authentication, seller identity, contracts, personal data, settlements or deployment. Never allow an AI-generated PR to bypass CI, branch protection or operator approval. Scheduled tasks do not imply continuous unattended execution. Never grant an agent unrestricted admin rights.

## Mandatory operator blocker — GitHub Actions billing (2026-10-19)
- **Status: BLOCKED / operator action required.** GitHub Actions run pages show: `We are having a problem billing your account. Please update your payment method...`.
- **Operator next action:** check the NurionHoldings organization billing settings and payment method or outstanding charges; do not share payment details in repository issues or chat.
- **After billing is resolved:** rerun the failed `Codex offline safety checks` and `Cloud development verification` jobs on PR #5; inspect their actual logs and require both checks to pass.
- **Release gate:** no merge, production deployment, or claim of CI success while the checks remain blocked or failing. Continue only isolated offline/read-only development.
- **Do not confuse this with** the earlier Python syntax-check command defect, which was separately corrected in commit `d5e7edb2dbab2d4c9abff7a6dd92f4e81726a08e`.
