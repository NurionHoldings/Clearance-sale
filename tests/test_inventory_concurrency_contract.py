"""Offline tests for optimistic inventory updates; no database access."""
import unittest

from backend.inventory_concurrency_contract import (
    InventoryConflict, InventoryVersion, plan_inventory_change,
    require_compare_and_swap_result,
)


class InventoryConcurrencyContractTests(unittest.TestCase):
    def setUp(self):
        self.current = InventoryVersion("product-1", 10, 3, 4)

    def test_reservation_increments_version_without_mutating_input(self):
        next_state = plan_inventory_change(
            self.current, expected_version=4, delta_reserved=2
        )
        self.assertEqual(next_state, InventoryVersion("product-1", 10, 5, 5))
        self.assertEqual(self.current, InventoryVersion("product-1", 10, 3, 4))

    def test_stale_version_and_oversell_are_rejected(self):
        for changes in [
            {"expected_version": 3, "delta_reserved": 1},
            {"expected_version": 4, "delta_reserved": 8},
            {"expected_version": 4, "delta_on_hand": -8},
            {"expected_version": 4, "delta_reserved": -4},
        ]:
            with self.subTest(changes=changes), self.assertRaises(InventoryConflict):
                plan_inventory_change(self.current, **changes)

    def test_reject_boolean_fractional_and_invalid_snapshot(self):
        for changes in [
            {"expected_version": True},
            {"expected_version": 4, "delta_reserved": 1.5},
            {"expected_version": 4, "delta_on_hand": False},
        ]:
            with self.subTest(changes=changes), self.assertRaises(InventoryConflict):
                plan_inventory_change(self.current, **changes)
        with self.assertRaises(InventoryConflict):
            plan_inventory_change(InventoryVersion("product-1", 2, 3, 0),
                                  expected_version=0)

    def test_compare_and_swap_must_affect_exactly_one_row(self):
        self.assertTrue(require_compare_and_swap_result(1))
        for count in (0, 2, -1, True, None, "1"):
            with self.subTest(count=count), self.assertRaises(InventoryConflict):
                require_compare_and_swap_result(count)


if __name__ == "__main__":
    unittest.main()
