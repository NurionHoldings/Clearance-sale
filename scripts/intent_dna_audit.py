#!/usr/bin/env python3
"""Create a deterministic, secret-free intent_DNA audit record."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_record(task, decision, commit, patch_file=None):
    policy = (ROOT / "config/intent-dna-policy.json").read_bytes()
    record = {
        "schema_version": 1,
        "project": "Clearance-sale",
        "task": task,
        "decision": decision,
        "commit": commit,
        "policy_sha256": hashlib.sha256(policy).hexdigest(),
        "patch_sha256": None,
        "human_approval_required": True,
        "auto_merge": False,
        "auto_deploy": False,
    }
    if patch_file is not None and Path(patch_file).is_file():
        record["patch_sha256"] = hashlib.sha256(Path(patch_file).read_bytes()).hexdigest()
    return record

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--decision", choices=("HOLD", "ALLOW_PROPOSAL"), required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--patch")
    parser.add_argument("--output", default="intent-dna-audit.json")
    args = parser.parse_args()
    record = build_record(args.task, args.decision, args.commit, args.patch)
    Path(args.output).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Audit record written: {args.output}")
