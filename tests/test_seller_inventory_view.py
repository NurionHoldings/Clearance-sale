import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from seller_inventory_view import InventoryItem, seller_inventory_summary


class SellerInventoryViewTests(unittest.TestCase):
    def test_summary_and_stable_order(self):
        items = [
            InventoryItem("B", "Second", 8, 3),
            InventoryItem("A", "First", 10, 2),
        ]
        result = seller_inventory_summary(items)
        self.assertEqual(result["product_count"], 2)
        self.assertEqual(result["active_count"], 2)
        self.assertEqual(result["available_units"], 13)
        self.assertEqual([row["sku"] for row in result["items"]], ["A", "B"])

    def test_inactive_item_not_sellable(self):
        result = seller_inventory_summary([InventoryItem("A", "Hidden", 10, 1, False)])
        self.assertEqual(result["available_units"], 0)
        self.assertEqual(result["items"][0]["on_hand"], 10)

    def test_duplicate_sku_rejected(self):
        with self.assertRaises(ValueError):
            seller_inventory_summary([InventoryItem("A", "One", 1, 0), InventoryItem("A", "Two", 2, 0)])

    def test_invalid_inventory_rejected(self):
        with self.assertRaises(ValueError):
            seller_inventory_summary([InventoryItem("A", "Invalid", 1, 2)])

    def test_input_unchanged(self):
        items = [InventoryItem("A", "Item", 4, 1)]
        seller_inventory_summary(items)
        self.assertEqual(items[0].reserved, 1)


if __name__ == "__main__":
    unittest.main()
