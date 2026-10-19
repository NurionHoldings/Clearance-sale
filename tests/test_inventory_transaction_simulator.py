"""Offline integration tests for staged inventory commit and rollback."""
import unittest

from backend.inventory_concurrency_contract import InventoryConflict, InventoryVersion
from backend.inventory_idempotency_contract import InventoryCommand
from backend.inventory_transaction_adapter import execute_inventory_transaction
from backend.inventory_transaction_simulator import SimulatedStore


class InventoryTransactionSimulatorTests(unittest.TestCase):
    def setUp(self):
        self.initial = InventoryVersion("product-1", 10, 1, 3)
        self.store = SimulatedStore({("seller-A", "product-1"): self.initial})
        self.command = InventoryCommand("seller-A", "product-1", "req-1", 3,
                                        delta_reserved=2)

    def test_commit_and_identical_retry(self):
        first = execute_inventory_transaction(self.command, transaction=self.store.begin())
        self.assertFalse(first["replayed"])
        self.assertEqual(self.store.balances[("seller-A", "product-1")].reserved, 3)
        self.assertEqual(len(self.store.receipts), 1)
        retry = execute_inventory_transaction(self.command, transaction=self.store.begin())
        self.assertTrue(retry["replayed"])
        self.assertEqual(len(self.store.receipts), 1)

    def test_rollback_discards_staged_write(self):
        tx = self.store.begin()
        next_state = InventoryVersion("product-1", 10, 3, 4)
        self.assertEqual(tx.compare_and_swap("seller-A", self.initial, next_state), 1)
        tx.rollback()
        self.assertEqual(self.store.balances[("seller-A", "product-1")], self.initial)
        self.assertEqual(self.store.receipts, {})

    def test_stale_version_fails_without_partial_commit(self):
        execute_inventory_transaction(self.command, transaction=self.store.begin())
        stale = InventoryCommand("seller-A", "product-1", "req-2", 3,
                                 delta_reserved=1)
        with self.assertRaises(InventoryConflict):
            execute_inventory_transaction(stale, transaction=self.store.begin())
        self.assertEqual(len(self.store.receipts), 1)

    def test_cross_seller_does_not_read_other_inventory(self):
        foreign = InventoryCommand("seller-B", "product-1", "req-1", 3,
                                   delta_reserved=2)
        with self.assertRaises(InventoryConflict):
            execute_inventory_transaction(foreign, transaction=self.store.begin())
        self.assertNotIn(("seller-B", "req-1"), self.store.receipts)


if __name__ == "__main__":
    unittest.main()
