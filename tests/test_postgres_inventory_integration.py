"""Opt-in PostgreSQL integration tests against a disposable test database.

Never use a production database. Set INVENTORY_TEST_DATABASE_URL to an isolated
PostgreSQL database that can be fully modified. No implicit DB connections.
"""
import os
from pathlib import Path
import unittest
from uuid import uuid4

URL = os.environ.get("INVENTORY_TEST_DATABASE_URL")
try:
    import psycopg
except ImportError:
    psycopg = None

from backend.inventory_concurrency_contract import InventoryConflict, InventoryVersion
from backend.inventory_idempotency_contract import InventoryCommand
from backend.inventory_transaction_adapter import execute_inventory_transaction
from backend.postgres_inventory_adapter import PostgresInventoryTransaction

SCHEMA = Path(__file__).resolve().parents[1] / "db/migrations/001_inventory_contract_draft.sql"


@unittest.skipUnless(URL and psycopg, "Requires psycopg and explicit disposable INVENTORY_TEST_DATABASE_URL")
class PostgresInventoryIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.connection = psycopg.connect(URL, autocommit=False)
        with cls.connection.cursor() as cur:
            cur.execute("SELECT current_database()")
            name = cur.fetchone()[0].lower()
        cls.connection.rollback()
        if not any(word in name for word in ("test", "ci", "scratch")):
            cls.connection.close()
            raise RuntimeError("Refusing non-test database name")
        schema = SCHEMA.read_text(encoding="utf-8")
        # The migration draft contains BEGIN/COMMIT; run it on a fresh
        # connection and avoid an already-open read transaction.
        with cls.connection.cursor() as cur:
            cur.execute(schema)
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def setUp(self):
        self.seller = str(uuid4())
        self.product = str(uuid4())
        self.key = "request-" + str(uuid4())
        with self.connection.cursor() as cur:
            cur.execute(
                "INSERT INTO inventory_balances(seller_id,product_id,on_hand,reserved,version) "
                "VALUES (%s,%s,10,1,3)", (self.seller, self.product),
            )
        self.connection.commit()

    def tearDown(self):
        self.connection.rollback()
        with self.connection.cursor() as cur:
            cur.execute("DELETE FROM inventory_request_receipts WHERE seller_id=%s", (self.seller,))
            cur.execute("DELETE FROM inventory_balances WHERE seller_id=%s", (self.seller,))
        self.connection.commit()

    def test_commit_and_retry(self):
        command = InventoryCommand(self.seller, self.product, self.key, 3, delta_reserved=2)
        first = execute_inventory_transaction(
            command, transaction=PostgresInventoryTransaction(self.connection)
        )
        self.assertFalse(first["replayed"])
        second = execute_inventory_transaction(
            command, transaction=PostgresInventoryTransaction(self.connection)
        )
        self.assertTrue(second["replayed"])
        self.assertEqual(second["result"].reserved, 3)

    def test_stale_version_and_overreservation_rejected(self):
        for command in (
            InventoryCommand(self.seller, self.product, self.key, 2, delta_reserved=1),
            InventoryCommand(self.seller, self.product, self.key, 3, delta_reserved=100),
        ):
            with self.assertRaises(InventoryConflict):
                execute_inventory_transaction(
                    command, transaction=PostgresInventoryTransaction(self.connection)
                )
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT reserved,version FROM inventory_balances "
                "WHERE seller_id=%s AND product_id=%s", (self.seller, self.product)
            )
            self.assertEqual(cur.fetchone(), (1, 3))
        self.connection.rollback()

    def test_same_key_different_payload_is_rejected(self):
        from backend.inventory_idempotency_contract import IdempotencyConflict
        first = InventoryCommand(self.seller, self.product, self.key, 3, delta_reserved=1)
        execute_inventory_transaction(first, transaction=PostgresInventoryTransaction(self.connection))
        changed = InventoryCommand(self.seller, self.product, self.key, 3, delta_reserved=2)
        with self.assertRaises(IdempotencyConflict):
            execute_inventory_transaction(changed, transaction=PostgresInventoryTransaction(self.connection))
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT reserved, version FROM inventory_balances "
                "WHERE seller_id=%s AND product_id=%s", (self.seller, self.product)
            )
            self.assertEqual(cur.fetchone(), (2, 4))
        self.connection.rollback()

    def test_competing_stale_version_fails_without_receipt(self):
        first = InventoryCommand(self.seller, self.product, self.key, 3, delta_reserved=1)
        execute_inventory_transaction(first, transaction=PostgresInventoryTransaction(self.connection))
        stale_key = "stale-" + str(uuid4())
        stale = InventoryCommand(self.seller, self.product, stale_key, 3, delta_reserved=1)
        with self.assertRaises(InventoryConflict):
            execute_inventory_transaction(stale, transaction=PostgresInventoryTransaction(self.connection))
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT count(*) FROM inventory_request_receipts "
                "WHERE seller_id=%s AND idempotency_key=%s", (self.seller, stale_key)
            )
            self.assertEqual(cur.fetchone()[0], 0)
        self.connection.rollback()

    def test_unique_receipt_key_constraint(self):
        from backend.inventory_transaction_adapter import StoredInventoryReceipt
        receipt = StoredInventoryReceipt(
            self.seller, self.key, "f" * 64,
            InventoryVersion(self.product, 10, 1, 3),
        )
        first = PostgresInventoryTransaction(self.connection)
        first.save_receipt(receipt)
        first.commit()
        second = PostgresInventoryTransaction(self.connection)
        with self.assertRaises(psycopg.errors.UniqueViolation):
            second.save_receipt(receipt)
        second.rollback()

    def test_two_connections_compete_for_same_version(self):
        """Two independent connections must not both commit a stale version."""
        import threading
        first_started = threading.Event()
        second_started = threading.Event()
        results = []
        failures = []

        def worker(request_key, ready, other_ready):
            connection = psycopg.connect(URL, autocommit=False)
            try:
                ready.set()
                if not other_ready.wait(timeout=10):
                    raise TimeoutError("Second transaction did not start")
                command = InventoryCommand(
                    self.seller, self.product, request_key, 3, delta_reserved=1
                )
                try:
                    outcome = execute_inventory_transaction(
                        command, transaction=PostgresInventoryTransaction(connection)
                    )
                    results.append(outcome)
                except InventoryConflict:
                    failures.append("stale")
            finally:
                connection.close()

        left = threading.Thread(target=worker, args=("left-" + self.key, first_started, second_started))
        right = threading.Thread(target=worker, args=("right-" + self.key, second_started, first_started))
        left.start()
        right.start()
        left.join(timeout=15)
        right.join(timeout=15)
        self.assertFalse(left.is_alive() or right.is_alive(), "Database contention timed out")
        self.assertEqual(len(results), 1)
        self.assertEqual(failures, ["stale"])
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT reserved, version FROM inventory_balances "
                "WHERE seller_id=%s AND product_id=%s", (self.seller, self.product)
            )
            self.assertEqual(cur.fetchone(), (2, 4))
        self.connection.rollback()

    def test_database_rejects_invalid_balance(self):
        with self.assertRaises(psycopg.errors.CheckViolation):
            with self.connection.cursor() as cur:
                cur.execute(
                    "UPDATE inventory_balances SET reserved=11 "
                    "WHERE seller_id=%s AND product_id=%s", (self.seller, self.product)
                )
        self.connection.rollback()


if __name__ == "__main__":
    unittest.main()
