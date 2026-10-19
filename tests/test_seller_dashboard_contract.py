import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from seller_dashboard_contract import build_seller_dashboard, validate_product_registration_draft, preview_product_registration
from seller_inventory_view import InventoryItem


class SellerDashboardContractTests(unittest.TestCase):
    def setUp(self):
        self.items = [
            InventoryItem("A", "Available", 10, 2),
            InventoryItem("B", "Low", 3, 2),
            InventoryItem("C", "Out", 1, 1),
            InventoryItem("D", "Inactive", 9, 0, False),
        ]

    def test_product_registration_draft_is_normalized_and_json_safe(self):
        draft = validate_product_registration_draft(sku=" A ", name=" Sample ", price_won=12000, on_hand=5, reserved=2)
        self.assertEqual(draft["sku"], "A")
        self.assertEqual(draft["name"], "Sample")
        self.assertEqual(draft["available"], 3)
        self.assertTrue(draft["read_only"])
        self.assertEqual(json.loads(json.dumps(draft))["price_won"], 12000)

    def test_registration_draft_rejects_invalid_prices(self):
        for price in (-1, True, 1.5, "12000", None, 1_000_000_001):
            with self.subTest(price=price), self.assertRaises(ValueError):
                validate_product_registration_draft(sku="A", name="Sample", price_won=price, on_hand=1)

    def test_registration_draft_rejects_invalid_inventory(self):
        for on_hand, reserved in ((-1, 0), (2, 3), (True, 0), (1, True), (1_000_001, 0)):
            with self.subTest(on_hand=on_hand, reserved=reserved), self.assertRaises(ValueError):
                validate_product_registration_draft(sku="A", name="Sample", price_won=0, on_hand=on_hand, reserved=reserved)

    def test_registration_preview_rejects_duplicate_sku(self):
        result = preview_product_registration(self.items, sku=" A ", name="New", price_won=5000, on_hand=2)
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"], [{"field": "sku", "code": "duplicate_sku"}])
        self.assertIsNone(result["product"])

    def test_registration_preview_accepts_unique_sku_without_mutation(self):
        result = preview_product_registration(self.items, sku=" E ", name="New", price_won=5000, on_hand=2)
        self.assertTrue(result["valid"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["product"]["sku"], "E")
        self.assertEqual(len(self.items), 4)

    def test_registration_preview_invalid_fields_and_snapshot_fail_closed(self):
        invalid = preview_product_registration(self.items, sku="E", name="New", price_won=-1, on_hand=2)
        self.assertEqual(invalid["errors"][0]["field"], "price_won")
        invalid_snapshot = preview_product_registration(None, sku="E", name="New", price_won=1, on_hand=2)
        self.assertEqual(invalid_snapshot["errors"][0]["code"], "invalid_snapshot")

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
