"""Transactional inventory adapter protocol; no database connection.

Production adapters MUST use a single DB transaction, unique seller-scoped
idempotency key, row locking or atomic CAS, and rollback on any failure.
"""
from dataclasses import dataclass

from .inventory_concurrency_contract import InventoryVersion, require_compare_and_swap_result
from .inventory_idempotency_contract import (
    IdempotencyConflict, fingerprint_inventory_command,
    plan_idempotent_inventory_command,
)


@dataclass(frozen=True)
class StoredInventoryReceipt:
    seller_id: str
    idempotency_key: str
    fingerprint: str
    result: object


def execute_inventory_transaction(command, *, transaction):
    """Execute through an injected trusted transactional adapter.

    Adapter methods: get_receipt(seller_id, key), get_balance(seller_id,
    product_id), compare_and_swap(seller_id, old, new), save_receipt(receipt),
    commit(). The adapter must guarantee atomicity and rollback on failure.
    This function MUST run only after authentication and write authorization.
    """
    fingerprint = fingerprint_inventory_command(command)
    rollback = getattr(transaction, "rollback", None)
    if not callable(rollback):
        raise TypeError("Transactional adapter must support rollback")
    try:
        return _execute_inventory_transaction(command, transaction, fingerprint)
    except Exception:
        rollback()
        raise


def _execute_inventory_transaction(command, transaction, fingerprint):
    receipt = transaction.get_receipt(command.seller_id, command.idempotency_key)
    if receipt is not None:
        if (not isinstance(receipt, StoredInventoryReceipt)
                or receipt.seller_id != command.seller_id
                or receipt.idempotency_key != command.idempotency_key
                or receipt.fingerprint != fingerprint
                or not isinstance(receipt.result, InventoryVersion)
                or receipt.result.product_id != command.product_id):
            raise IdempotencyConflict("Conflicting or invalid stored receipt")
        transaction.rollback()  # End the read-only replay transaction.
        return {"replayed": True, "result": receipt.result}

    current = transaction.get_balance(command.seller_id, command.product_id)
    planned = plan_idempotent_inventory_command(command, current=current)
    require_compare_and_swap_result(
        transaction.compare_and_swap(command.seller_id, current, planned["next_state"])
    )
    transaction.save_receipt(StoredInventoryReceipt(
        seller_id=command.seller_id,
        idempotency_key=command.idempotency_key,
        fingerprint=fingerprint,
        result=planned["next_state"],
    ))
    transaction.commit()
    return {"replayed": False, "result": planned["next_state"]}
