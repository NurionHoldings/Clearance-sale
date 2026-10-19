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
