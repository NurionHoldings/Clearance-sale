#!/usr/bin/env python3
"""Fail-closed, offline review of Codex proposal artifacts before manual PR creation."""
import argparse
import hashlib
import json
from pathlib import Path

def inspect(audit_path, patch_path, expected_commit):
    errors = []
    try:
        audit = json.loads(Path(audit_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"decision": "HOLD", "errors": [f"Invalid audit record: {type(exc).__name__}"]}
    required = {
        "schema_version": 1,
        "project": "Clearance-sale",
        "decision": "ALLOW_PROPOSAL",
        "human_approval_required": True,
        "auto_merge": False,
        "auto_deploy": False,
        "commit": expected_commit,
    }
    for key, expected in required.items():
        if audit.get(key) != expected:
            errors.append(f"Invalid {key}")
    try:
        patch = Path(patch_path).read_bytes()
    except OSError:
        patch = b""
    if not patch:
        errors.append("Missing or empty patch")
    elif audit.get("patch_sha256") != hashlib.sha256(patch).hexdigest():
        errors.append("Patch digest mismatch")
    return {"decision": "READY_FOR_HUMAN_REVIEW" if not errors else "HOLD", "errors": errors}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True)
    parser.add_argument("--patch", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    result = inspect(args.audit, args.patch, args.commit)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["decision"] == "READY_FOR_HUMAN_REVIEW" else 1)
