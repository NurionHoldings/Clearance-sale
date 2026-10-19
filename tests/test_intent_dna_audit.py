import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("intent_dna_audit", ROOT / "scripts/intent_dna_audit.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class IntentDNAAuditTests(unittest.TestCase):
    def test_hold_has_no_patch(self):
        record = module.build_record("seller-dashboard-tests", "HOLD", "abc123")
        self.assertEqual(record["decision"], "HOLD")
        self.assertIsNone(record["patch_sha256"])
        self.assertTrue(record["human_approval_required"])
        self.assertFalse(record["auto_deploy"])
        self.assertFalse(record["auto_merge"])

    def test_patch_hash_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            patch = Path(directory) / "proposal.patch"
            patch.write_bytes(b"test patch")
            first = module.build_record("inventory-invariant-tests", "ALLOW_PROPOSAL", "abc123", patch)
            second = module.build_record("inventory-invariant-tests", "ALLOW_PROPOSAL", "abc123", patch)
            self.assertEqual(first, second)
            self.assertEqual(len(first["patch_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
