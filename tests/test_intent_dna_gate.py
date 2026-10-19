import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("intent_dna_gate", ROOT / "scripts/intent_dna_gate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class IntentDNAGateTests(unittest.TestCase):
    def test_approved_task(self):
        self.assertEqual(module.validate("seller-dashboard-tests", ["tests/example.py"])["decision"], "ALLOW_PROPOSAL")
    def test_unknown_task(self):
        self.assertEqual(module.validate("deploy-production", [])["decision"], "HOLD")
    def test_protected_file(self):
        self.assertEqual(module.validate("inventory-invariant-tests", [".github/workflows/deploy.yml"])["decision"], "HOLD")
    def test_traversal(self):
        self.assertEqual(module.validate("inventory-invariant-tests", ["tests/../config/secrets"])["decision"], "HOLD")

if __name__ == "__main__":
    unittest.main()
