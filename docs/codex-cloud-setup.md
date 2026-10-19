# OpenAI Codex Cloud integration (phase 2)

## Status
Manual, read-only Codex review workflow staged for review. It **does not** autonomously develop, push commits, merge, or deploy. It inherits the guarded verification workflow from infrastructure PR #3. The workflow only runs once merged into the default branch and manually dispatched.

## Operator actions
1. Review and merge PR #3 (scheduled verification) first, then this PR. Do not merge until workflow permissions and checks are understood.
2. Create a separate OpenAI API project and a scoped API key at https://platform.openai.com/api-keys . ChatGPT subscription access does not substitute for API billing.
3. Configure billing budget and usage alerts for the project.
4. GitHub repository Settings > Secrets and variables > Actions > New repository secret: name OPENAI_API_KEY; paste the key there, never in a commit or chat.
5. Repository Settings > Actions > General: allow approved actions; keep default GITHUB_TOKEN read-only. Require PR review and checks for main.
6. Open Actions > Codex guarded review > Run workflow. Inspect logs and the review artifact. The first run validates connectivity and provider billing.

## Security boundary
- Only workflow_dispatch; no pull_request_target, untrusted forks or user-provided prompts.
- No token persistence in checkout, no repository write permission, Codex :read-only and drop-sudo.
- API key is only passed to the official Codex action. Never echo it.
- No automatic release, merchant activation, payment, production data access or auto-merge.
- Review output may be sensitive: avoid putting secrets or customer data in the repository; artifacts retained 3 days.
- Pin actions to reviewed immutable commit SHAs before production-hardening the workflow.

## Future coding agent
A later, separate workflow can run Codex with :workspace permissions in an isolated job, verify changes and open a PR via a separate least-privileged publisher job. Add task allowlists, cost limits, and mandatory human approval for payments, identity, contracts, settlement and deployment. Never give Codex a write-capable GitHub token or unrestricted sudo.
