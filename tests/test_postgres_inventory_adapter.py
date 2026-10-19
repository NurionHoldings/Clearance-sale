"""PostgreSQL adapter SQL contract tests without a live database."""
import unittest

from backend.inventory_concurrency_contract import InventoryVersion
from backend.inventory_transaction_adapter import StoredInventoryReceipt
from backend.postgres_inventory_adapter import PostgresInventoryTransaction


class FakeCursor:
    def __init__(self, connection):
        self.connection = connection
        self.rowcount = 1
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def execute(self, query, params):
        self.connection.statements.append((query, params))
    def fetchone(self):
        return self.connection.next_row


class FakeConnection:
    autocommit = False
    def __init__(self):
        self.statements = []
        self.next_row = None
        self.commits = 0
        self.rollbacks = 0
    def cursor(self):
        return FakeCursor(self)
    def commit(self):
        self.commits += 1
    def rollback(self):
        self.rollbacks += 1


class PostgresInventoryAdapterTests(unittest.TestCase):
    def setUp(self):
        self.connection = FakeConnection()
        self.adapter = PostgresInventoryTransaction(self.connection)

    def test_read_queries_enforce_seller_scope(self):
        self.connection.next_row = ("product-1", 10, 2, 3)
        self.assertEqual(self.adapter.get_balance("seller-A", "product-1"),
                         InventoryVersion("product-1", 10, 2, 3))
        query, params = self.connection.statements[-1]
        self.assertIn("seller_id=%s", query)
        self.assertIn("FOR UPDATE", query)
        self.assertEqual(params, ("seller-A", "product-1"))

    def test_cas_update_uses_tenant_version_and_prior_quantities(self):
        old = InventoryVersion("product-1", 10, 2, 3)
        new = InventoryVersion("product-1", 10, 3, 4)
        self.assertEqual(self.adapter.compare_and_swap("seller-A", old, new), 1)
        query, params = self.connection.statements[-1]
        self.assertIn("seller_id=%s", query)
        self.assertIn("version=%s", query)
        self.assertEqual(params, (10, 3, 4, "seller-A", "product-1", 3, 10, 2))

    def test_receipt_lookup_and_insert_use_scoped_parameters(self):
        self.connection.next_row = ("abc", "product-1", 10, 3, 4)
        receipt = self.adapter.get_receipt("seller-A", "key-1")
        self.assertEqual(receipt, StoredInventoryReceipt(
            "seller-A", "key-1", "abc", InventoryVersion("product-1", 10, 3, 4)
        ))
        self.assertEqual(self.connection.statements[-1][1], ("seller-A", "key-1"))
        self.adapter.save_receipt(receipt)
        self.assertEqual(self.connection.statements[-1][1][:2], ("seller-A", "key-1"))

    def test_idempotency_lock_is_parameterized_and_transaction_scoped(self):
        self.adapter.acquire_idempotency_lock("seller-A", "key-1")
        query, params = self.connection.statements[-1]
        self.assertIn("pg_advisory_xact_lock", query)
        self.assertIn("%s", query)
        self.assertEqual(params, ("seller-A:key-1",))
        self.assertEqual(self.connection.commits, 0)

    def test_lock_rejected_after_transaction_closed(self):
        self.adapter.rollback()
        with self.assertRaises(RuntimeError):
            self.adapter.acquire_idempotency_lock("seller-A", "key-1")

    def test_transaction_lifecycle_and_autocommit_guard(self):
        self.adapter.rollback()
        self.assertEqual(self.connection.rollbacks, 1)
        with self.assertRaises(RuntimeError):
            self.adapter.get_balance("seller-A", "product-1")
        connection = FakeConnection()
        connection.autocommit = True
        with self.assertRaises(ValueError):
            PostgresInventoryTransaction(connection)


if __name__ == "__main__":
    unittest.main()
