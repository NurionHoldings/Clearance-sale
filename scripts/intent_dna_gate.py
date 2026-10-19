#!/usr/bin/env python3
"""Offline fail-closed intent_DNA task and change gate."""
import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/intent-dna-policy.json"

def validate(task: str, paths: list[str]) -> dict:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    spec = policy["allowed_tasks"].get(task)
    errors = []
    if not spec:
        errors.append("Unapproved task")
    if policy["release"]["auto_merge"] or policy["release"]["auto_deploy"]:
        errors.append("Automatic production mutation prohibited")
    if not policy["release"]["requires_human_approval"]:
        errors.append("Human approval required")
    if spec:
        for path in paths:
            normalized = path.replace("\\", "/")
            if normalized.startswith("/") or ".." in Path(normalized).parts or not any(normalized.startswith(prefix) for prefix in spec["paths"]):
                errors.append(f"Out-of-scope path: {path}")
    return {"task": task, "decision": "ALLOW_PROPOSAL" if not errors else "HOLD", "risk": spec["risk"] if spec else "unknown", "errors": errors, "requires_human_approval": True}

def changed_paths() -> list[str]:
    output = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True)
    paths = []
    for line in output.splitlines():
        status, path = line[:2], line[3:]
        if path == ".github/codex/change-prompt.md":
            continue  # checked separately against the approved SHA256
        if " -> " in path:
            paths.extend(path.split(" -> ", 1))
        else:
            paths.append(path)
    return paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--check-changes", action="store_true")
    args = parser.parse_args()
    result = validate(args.task, changed_paths() if args.check_changes else [])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["decision"] == "ALLOW_PROPOSAL" else 1)
