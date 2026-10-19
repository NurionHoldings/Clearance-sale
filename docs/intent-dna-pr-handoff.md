# intent_DNA manual PR handoff

The handoff utility is an **offline preparation step**, not authorization to merge, publish or deploy.

1. Download the proposal patch and matching intent-dna-audit.json from the same successful GitHub Actions run.
2. Verify the audit's base commit and patch digest. Do not trust filenames or an unverified patch.
3. Record the human operator identifier and an independently issued approval reference.
4. Generate the handoff manifest locally:

```bash
python scripts/intent_dna_pr_handoff.py \
  --audit intent-dna-audit.json \
  --patch proposed.patch \
  --commit VERIFIED_BASE_COMMIT \
  --operator VERIFIED_OPERATOR \
  --approval-id APPROVAL_REFERENCE
```

5. A reviewer must inspect the patch and any target branch differences before manually creating a review PR. Do not apply a patch to a production branch without review.
6. If any artifact is missing or its digest differs, HOLD. Do not create a PR.
7. Never put credentials, customer data, or personal information into audit artifacts.

The generated manifest is a review handoff record, **not cryptographic proof of operator identity or authorization**. GitHub branch protection and authorized repository permissions remain mandatory. This workflow does not grant write access or create PRs automatically.
