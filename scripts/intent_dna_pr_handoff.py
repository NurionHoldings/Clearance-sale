#!/usr/bin/env python3
"""Offline approval ledger and PR handoff manifest; never opens a PR."""
import argparse
import hashlib
import json
from pathlib import Path
from intent_dna_review_gate import inspect

def prepare(audit_path, patch_path, commit, operator, approval_id):
    review = inspect(audit_path, patch_path, commit)
    if review["decision"] != "READY_FOR_HUMAN_REVIEW":
        return {"status": "HOLD", "reasons": review["errors"]}
    if not operator.strip() or not approval_id.strip():
        return {"status": "HOLD", "reasons": ["Operator identity and approval ID required"]}
    audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "status": "READY_FOR_MANUAL_PR",
        "repository": "NurionHoldings/Clearance-sale",
        "task": audit["task"],
        "base_commit": commit,
        "operator": operator,
        "approval_id": approval_id,
        "patch_sha256": hashlib.sha256(Path(patch_path).read_bytes()).hexdigest(),
        "auto_create_pr": False,
        "auto_merge": False,
        "auto_deploy": False,
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True)
    parser.add_argument("--patch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--approval-id", required=True)
    parser.add_argument("--output", default="intent-dna-pr-handoff.json")
    args = parser.parse_args()
    result = prepare(args.audit, args.patch, args.commit, args.operator, args.approval_id)
    if result["status"] == "READY_FOR_MANUAL_PR":
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["status"] == "READY_FOR_MANUAL_PR" else 1)
