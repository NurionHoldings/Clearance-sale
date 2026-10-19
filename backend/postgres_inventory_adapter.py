"""PostgreSQL inventory adapter using an injected DB-API connection.

No connection strings, migrations, or production wiring. Caller must supply
an authenticated, authorized seller context and a dedicated connection with
autocommit disabled. Uses parameterized queries and tenant predicates.
"""
from .inventory_concurrency_contract import InventoryVersion
from .inventory_transaction_adapter import StoredInventoryReceipt


class PostgresInventoryTransaction:
    def __init__(self, connection):
        if getattr(connection, "autocommit", None) is not False:
            raise ValueError("PostgreSQL transaction requires autocommit=False")
        self.connection = connection
        self.closed = False

    def _cursor(self):
        if self.closed:
            raise RuntimeError("Transaction already closed")
        return self.connection.cursor()

    def get_receipt(self, seller_id, key):
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT fingerprint, product_id, on_hand, reserved, version "
                "FROM inventory_request_receipts WHERE seller_id=%s AND idempotency_key=%s "
                "FOR UPDATE", (seller_id, key),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        fingerprint, product_id, on_hand, reserved, version = row
        return StoredInventoryReceipt(
            seller_id, key, fingerprint,
            InventoryVersion(str(product_id), on_hand, reserved, version),
        )

    def get_balance(self, seller_id, product_id):
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT product_id, on_hand, reserved, version FROM inventory_balances "
                "WHERE seller_id=%s AND product_id=%s FOR UPDATE",
                (seller_id, product_id),
            )
            row = cursor.fetchone()
        return InventoryVersion(str(row[0]), *row[1:]) if row is not None else None

    def compare_and_swap(self, seller_id, old, new):
        with self._cursor() as cursor:
            cursor.execute(
                "UPDATE inventory_balances SET on_hand=%s, reserved=%s, version=%s "
                "WHERE seller_id=%s AND product_id=%s AND version=%s "
                "AND on_hand=%s AND reserved=%s",
                (new.on_hand, new.reserved, new.version, seller_id,
                 old.product_id, old.version, old.on_hand, old.reserved),
            )
            return cursor.rowcount

    def save_receipt(self, receipt):
        with self._cursor() as cursor:
            cursor.execute(
                "INSERT INTO inventory_request_receipts "
                "(seller_id, idempotency_key, fingerprint, product_id, on_hand, reserved, version) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (receipt.seller_id, receipt.idempotency_key, receipt.fingerprint,
                 receipt.result.product_id, receipt.result.on_hand,
                 receipt.result.reserved, receipt.result.version),
            )

    def commit(self):
        self.connection.commit()
        self.closed = True

    def rollback(self):
        if not self.closed:
            try:
                self.connection.rollback()
            finally:
                self.closed = True
