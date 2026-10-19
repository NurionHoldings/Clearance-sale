import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inventory_rules", ROOT / "backend/inventory_rules.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryRulesTests(unittest.TestCase):
    def test_available_quantity(self):
        self.assertEqual(inventory.available_quantity(10, 3), 7)

    def test_reserve_and_release(self):
        reserved = inventory.reserve(10, 3, 5)
        self.assertEqual(reserved, 8)
        self.assertEqual(inventory.release(10, reserved, 2), 6)

    def test_insufficient_stock(self):
        with self.assertRaises(ValueError):
            inventory.reserve(10, 8, 3)

    def test_invalid_inventory(self):
        for on_hand, reserved in [(-1, 0), (1, -1), (1, 2)]:
            with self.subTest(on_hand=on_hand, reserved=reserved):
                with self.assertRaises(ValueError):
                    inventory.available_quantity(on_hand, reserved)

    def test_invalid_requested_quantity(self):
        for requested in (0, -1, True, 1.5):
            with self.subTest(requested=requested):
                with self.assertRaises((ValueError, TypeError)):
                    inventory.reserve(10, 0, requested)

    def test_stock_adjustment_respects_reservations(self):
        self.assertEqual(inventory.validate_inventory_adjustment(10, 3, -7), 3)
        self.assertEqual(inventory.validate_inventory_adjustment(10, 3, 5), 15)
        with self.assertRaises(ValueError):
            inventory.validate_inventory_adjustment(10, 3, -8)

    def test_stock_adjustment_rejects_invalid_delta(self):
        for delta in (True, 1.5, "2", None):
            with self.subTest(delta=delta), self.assertRaises(TypeError):
                inventory.validate_inventory_adjustment(10, 3, delta)
        with self.assertRaises(ValueError):
            inventory.validate_inventory_adjustment(2, 3, 1)

    def test_release_cannot_exceed_reserved(self):
        with self.assertRaises(ValueError):
            inventory.release(10, 2, 3)


if __name__ == "__main__":
    unittest.main()
