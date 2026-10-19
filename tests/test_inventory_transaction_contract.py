"""Offline inventory transaction contract tests."""
import unittest

from backend.inventory_concurrency_contract import InventoryConflict, InventoryVersion
from backend.inventory_idempotency_contract import InventoryCommand, IdempotencyConflict
from backend.inventory_transaction_contract import (
    StoredCommandReceipt, plan_transaction, validate_transaction_write,
)


class InventoryTransactionContractTests(unittest.TestCase):
    def setUp(self):
        self.command = InventoryCommand("seller-A", "product-1", "key-1", 2, delta_reserved=1)
        self.current = InventoryVersion("product-1", 8, 2, 2)

    def test_new_transaction_receipt_and_replay(self):
        plan = plan_transaction(self.command, current=self.current)
        receipt = validate_transaction_write(plan, affected_rows=1)
        self.assertEqual(receipt.result, InventoryVersion("product-1", 8, 3, 3))
        replay = plan_transaction(self.command, current=None, receipt=receipt)
        self.assertTrue(replay["replayed"])
        self.assertEqual(replay["next_state"], receipt.result)
        with self.assertRaises(InventoryConflict):
            validate_transaction_write(replay, affected_rows=1)

    def test_cas_failure_and_ambiguous_rows_are_rejected(self):
        plan = plan_transaction(self.command, current=self.current)
        for rows in (0, 2, None, True):
            with self.subTest(rows=rows), self.assertRaises(InventoryConflict):
                validate_transaction_write(plan, affected_rows=rows)

    def test_key_collision_and_malformed_receipt_fail_closed(self):
        plan = plan_transaction(self.command, current=self.current)
        receipt = validate_transaction_write(plan, affected_rows=1)
        changed = InventoryCommand("seller-A", "product-1", "key-1", 2, delta_reserved=2)
        with self.assertRaises(IdempotencyConflict):
            plan_transaction(changed, current=None, receipt=receipt)
        with self.assertRaises(IdempotencyConflict):
            plan_transaction(self.command, current=None, receipt="bad")


if __name__ == "__main__":
    unittest.main()
