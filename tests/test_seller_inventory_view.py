import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from seller_inventory_view import InventoryItem, seller_inventory_summary, filter_inventory_rows, seller_dashboard_metrics


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

    def test_inventory_status_filters(self):
        snapshot = seller_inventory_summary([
            InventoryItem("A", "Available", 10, 1),
            InventoryItem("B", "Low", 3, 1),
            InventoryItem("C", "Sold out", 2, 2),
            InventoryItem("D", "Inactive", 10, 0, False),
        ])
        self.assertEqual([r["sku"] for r in filter_inventory_rows(snapshot, "active")], ["A", "B", "C"])
        self.assertEqual([r["sku"] for r in filter_inventory_rows(snapshot, "inactive")], ["D"])
        self.assertEqual([r["sku"] for r in filter_inventory_rows(snapshot, "low_stock", 2)], ["B"])
        self.assertEqual([r["sku"] for r in filter_inventory_rows(snapshot, "out_of_stock")], ["C"])

    def test_invalid_filter_and_threshold(self):
        snapshot = seller_inventory_summary([])
        for status in ("missing", "", None):
            with self.subTest(status=status), self.assertRaises(ValueError):
                filter_inventory_rows(snapshot, status)
        for threshold in (-1, True, 2.5):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                filter_inventory_rows(snapshot, "low_stock", threshold)

    def test_filter_does_not_mutate_snapshot(self):
        snapshot = seller_inventory_summary([InventoryItem("A", "Item", 2, 0)])
        rows = filter_inventory_rows(snapshot)
        rows[0]["available"] = 999
        self.assertEqual(snapshot["items"][0]["available"], 2)

    def test_dashboard_metrics_and_alert_priority(self):
        snapshot = seller_inventory_summary([
            InventoryItem("A", "Healthy", 10, 1),
            InventoryItem("B", "Low", 3, 1),
            InventoryItem("C", "Sold out", 2, 2),
            InventoryItem("D", "Paused", 10, 0, False),
        ])
        metrics = seller_dashboard_metrics(snapshot, low_stock_threshold=2)
        self.assertEqual(metrics["product_count"], 4)
        self.assertEqual(metrics["active_count"], 3)
        self.assertEqual(metrics["inactive_count"], 1)
        self.assertEqual(metrics["available_units"], 11)
        self.assertEqual(metrics["low_stock_count"], 1)
        self.assertEqual(metrics["out_of_stock_count"], 1)
        self.assertEqual([alert["sku"] for alert in metrics["alerts"]], ["C", "B"])

    def test_dashboard_zero_threshold_and_invalid_values(self):
        snapshot = seller_inventory_summary([InventoryItem("A", "Low", 1, 0)])
        self.assertEqual(seller_dashboard_metrics(snapshot, 0)["low_stock_count"], 0)
        for threshold in (-1, True, 1.5):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                seller_dashboard_metrics(snapshot, threshold)

    def test_input_unchanged(self):
        items = [InventoryItem("A", "Item", 4, 1)]
        seller_inventory_summary(items)
        self.assertEqual(items[0].reserved, 1)


if __name__ == "__main__":
    unittest.main()
