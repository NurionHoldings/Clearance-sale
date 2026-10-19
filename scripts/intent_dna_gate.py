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
    """Read Git porcelain -z safely, including spaces and rename source paths."""
    data = subprocess.check_output(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT,
    )
    entries = data.split(b"\\0")
    paths = []
    i = 0
    while i < len(entries):
        record = entries[i]
        i += 1
        if not record:
            continue
        status = record[:2].decode("ascii", errors="replace")
        path = record[3:].decode("utf-8", errors="surrogateescape")
        if path != ".github/codex/change-prompt.md":
            paths.append(path)
        if "R" in status or "C" in status:
            if i >= len(entries) or not entries[i]:
                raise ValueError("Incomplete git rename/copy record")
            source = entries[i].decode("utf-8", errors="surrogateescape")
            i += 1
            if source != ".github/codex/change-prompt.md":
                paths.append(source)
    return paths

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True)
    parser.add_argument("--check-changes", action="store_true")
    args = parser.parse_args()
    result = validate(args.task, changed_paths() if args.check_changes else [])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["decision"] == "ALLOW_PROPOSAL" else 1)
