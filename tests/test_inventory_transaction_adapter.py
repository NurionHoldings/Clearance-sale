"""Offline transaction boundary tests with a synthetic transactional adapter."""
import unittest

from backend.inventory_concurrency_contract import InventoryConflict, InventoryVersion
from backend.inventory_idempotency_contract import IdempotencyConflict, InventoryCommand
from backend.inventory_transaction_adapter import (
    StoredInventoryReceipt, execute_inventory_transaction,
)


class FakeTransaction:
    def __init__(self):
        self.balance = InventoryVersion("product-1", 10, 1, 3)
        self.receipt = None
        self.writes = []
        self.commits = 0
        self.rollbacks = 0
        self.affected_rows = 1

    def get_receipt(self, seller_id, key):
        return self.receipt

    def get_balance(self, seller_id, product_id):
        return self.balance

    def compare_and_swap(self, seller_id, old, new):
        self.writes.append(("cas", seller_id, old, new))
        return self.affected_rows

    def save_receipt(self, receipt):
        self.writes.append(("receipt", receipt))
        self.receipt = receipt

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class InventoryTransactionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tx = FakeTransaction()
        self.command = InventoryCommand("seller-A", "product-1", "req-1", 3,
                                        delta_reserved=2)

    def test_new_request_cas_then_receipt_then_commit(self):
        response = execute_inventory_transaction(self.command, transaction=self.tx)
        self.assertFalse(response["replayed"])
        self.assertEqual(response["result"], InventoryVersion("product-1", 10, 3, 4))
        self.assertEqual([w[0] for w in self.tx.writes], ["cas", "receipt"])
        self.assertEqual(self.tx.commits, 1)

    def test_identical_retry_does_not_write_again(self):
        execute_inventory_transaction(self.command, transaction=self.tx)
        previous_writes = len(self.tx.writes)
        response = execute_inventory_transaction(self.command, transaction=self.tx)
        self.assertTrue(response["replayed"])
        self.assertEqual(len(self.tx.writes), previous_writes)
        self.assertEqual(self.tx.commits, 1)
        self.assertEqual(self.tx.rollbacks, 1)

    def test_cas_conflict_prevents_receipt_and_commit(self):
        self.tx.affected_rows = 0
        with self.assertRaises(InventoryConflict):
            execute_inventory_transaction(self.command, transaction=self.tx)
        self.assertEqual([w[0] for w in self.tx.writes], ["cas"])
        self.assertIsNone(self.tx.receipt)
        self.assertEqual(self.tx.commits, 0)
        self.assertEqual(self.tx.rollbacks, 1)

    def test_changed_command_same_key_is_rejected(self):
        execute_inventory_transaction(self.command, transaction=self.tx)
        changed = InventoryCommand("seller-A", "product-1", "req-1", 3,
                                   delta_reserved=3)
        with self.assertRaises(IdempotencyConflict):
            execute_inventory_transaction(changed, transaction=self.tx)
        self.assertEqual(self.tx.commits, 1)
        self.assertEqual(self.tx.rollbacks, 1)

    def test_rollback_failure_is_reported(self):
        self.tx.affected_rows = 0

        def broken_rollback():
            raise OSError("database connection lost")

        self.tx.rollback = broken_rollback
        with self.assertRaisesRegex(RuntimeError, "Inventory rollback failed") as caught:
            execute_inventory_transaction(self.command, transaction=self.tx)
        self.assertIsInstance(caught.exception.__cause__, OSError)
        self.assertEqual(self.tx.commits, 0)

    def test_adapter_without_rollback_is_rejected_before_data_access(self):
        self.tx.rollback = None
        with self.assertRaises(TypeError):
            execute_inventory_transaction(self.command, transaction=self.tx)
        self.assertEqual(self.tx.writes, [])
        self.assertEqual(self.tx.commits, 0)


if __name__ == "__main__":
    unittest.main()
