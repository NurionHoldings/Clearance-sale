import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from seller_dashboard_contract import build_seller_dashboard
from seller_inventory_view import InventoryItem


class SellerDashboardContractTests(unittest.TestCase):
    def setUp(self):
        self.items = [
            InventoryItem("A", "Available", 10, 2),
            InventoryItem("B", "Low", 3, 2),
            InventoryItem("C", "Out", 1, 1),
            InventoryItem("D", "Inactive", 9, 0, False),
        ]

    def test_json_compatible_response(self):
        result = build_seller_dashboard(self.items, low_stock_threshold=2)
        self.assertEqual(result["schema_version"], 1)
        self.assertTrue(result["read_only"])
        self.assertEqual(result["visible_count"], 4)
        self.assertEqual(result["metrics"]["out_of_stock_count"], 1)
        self.assertEqual(result["metrics"]["low_stock_count"], 1)
        self.assertEqual(json.loads(json.dumps(result))["products"][0]["sku"], "A")

    def test_filter_keeps_global_metrics(self):
        result = build_seller_dashboard(self.items, status="out_of_stock")
        self.assertEqual(result["visible_count"], 1)
        self.assertEqual(result["products"][0]["sku"], "C")
        self.assertEqual(result["metrics"]["product_count"], 4)

    def test_invalid_filter_rejected(self):
        with self.assertRaises(ValueError):
            build_seller_dashboard(self.items, status="unknown")

    def test_no_input_mutation(self):
        result = build_seller_dashboard(self.items)
        result["products"][0]["available"] = 999
        self.assertEqual(self.items[0].on_hand, 10)


if __name__ == "__main__":
    unittest.main()
