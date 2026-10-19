"""Offline-only transactional inventory simulator for tests.

Not a production DB, not durable, not thread-safe, and never for customer data.
A transaction stages writes; commit publishes balance and receipt together.
"""
from .inventory_concurrency_contract import InventoryVersion


class SimulatedStore:
    def __init__(self, balances):
        self.balances = dict(balances)
        self.receipts = {}

    def begin(self):
        return SimulatedTransaction(self)


class SimulatedTransaction:
    def __init__(self, store):
        self.store = store
        self.pending_balance = None
        self.pending_receipt = None
        self.closed = False

    def _check_open(self):
        if self.closed:
            raise RuntimeError("Transaction closed")

    def get_receipt(self, seller_id, key):
        self._check_open()
        return self.store.receipts.get((seller_id, key))

    def get_balance(self, seller_id, product_id):
        self._check_open()
        return self.store.balances.get((seller_id, product_id))

    def compare_and_swap(self, seller_id, old, new):
        self._check_open()
        if not isinstance(old, InventoryVersion) or not isinstance(new, InventoryVersion):
            return 0
        key = (seller_id, old.product_id)
        if self.store.balances.get(key) != old or new.product_id != old.product_id:
            return 0
        if self.pending_balance is not None:
            raise RuntimeError("Only one inventory update per transaction")
        self.pending_balance = (key, old, new)
        return 1

    def save_receipt(self, receipt):
        self._check_open()
        key = (receipt.seller_id, receipt.idempotency_key)
        if self.pending_balance is None or key in self.store.receipts:
            raise RuntimeError("Missing update or duplicate receipt")
        if self.pending_balance[0] != (receipt.seller_id, receipt.result.product_id):
            raise RuntimeError("Receipt does not match staged inventory update")
        self.pending_receipt = (key, receipt)

    def commit(self):
        self._check_open()
        if self.pending_balance is None or self.pending_receipt is None:
            raise RuntimeError("Incomplete transaction")
        key, old, new = self.pending_balance
        receipt_key, receipt = self.pending_receipt
        if self.store.balances.get(key) != old or receipt_key in self.store.receipts:
            raise RuntimeError("Concurrent change or duplicate receipt")
        self.store.balances[key] = new
        self.store.receipts[receipt_key] = receipt
        self.closed = True

    def rollback(self):
        self._check_open()
        self.pending_balance = None
        self.pending_receipt = None
        self.closed = True
