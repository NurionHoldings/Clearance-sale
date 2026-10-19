"""Pure inventory idempotency and transaction request contract.

No database, persistence, or HTTP integration. A future adapter MUST enforce a
unique (seller_id, idempotency_key) constraint and atomically store the result
with the inventory CAS update in the same database transaction.
"""
from dataclasses import dataclass
from hashlib import sha256
import json

from .inventory_concurrency_contract import (
    InventoryConflict, InventoryVersion, plan_inventory_change,
)


class IdempotencyConflict(ValueError):
    """An idempotency key was reused for a different inventory operation."""


@dataclass(frozen=True)
class InventoryCommand:
    seller_id: str
    product_id: str
    idempotency_key: str
    expected_version: int
    delta_on_hand: int = 0
    delta_reserved: int = 0


def fingerprint_inventory_command(command):
    """Stable fingerprint; never includes a secret or browser-supplied role."""
    if not isinstance(command, InventoryCommand):
        raise ValueError("Expected inventory command")
    for value in (command.seller_id, command.product_id, command.idempotency_key):
        if not isinstance(value, str) or not value.strip() or len(value) > 128:
            raise ValueError("Missing or oversized inventory command identity")
    for value in (command.expected_version, command.delta_on_hand, command.delta_reserved):
        if type(value) is not int:
            raise ValueError("Inventory command quantities must be integers")
    if command.expected_version < 0:
        raise ValueError("Expected version cannot be negative")
    payload = {
        "seller_id": command.seller_id,
        "product_id": command.product_id,
        "expected_version": command.expected_version,
        "delta_on_hand": command.delta_on_hand,
        "delta_reserved": command.delta_reserved,
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def plan_idempotent_inventory_command(command, *, current, prior_fingerprint=None,
                                      prior_result=None):
    """Plan a new write, or return an identical previously committed result.

    The caller must fetch prior idempotency state under transaction protection.
    Never replay a result from another seller or reuse an unmatched key.
    """
    fingerprint = fingerprint_inventory_command(command)
    if prior_fingerprint is not None:
        if prior_fingerprint != fingerprint or not isinstance(prior_result, InventoryVersion):
            raise IdempotencyConflict("Idempotency key conflict or incomplete prior result")
        if prior_result.product_id != command.product_id:
            raise IdempotencyConflict("Prior result product mismatch")
        return {"replayed": True, "fingerprint": fingerprint, "next_state": prior_result}
    if prior_result is not None:
        raise IdempotencyConflict("Prior result without fingerprint")
    if not isinstance(current, InventoryVersion) or current.product_id != command.product_id:
        raise InventoryConflict("Inventory product mismatch")
    next_state = plan_inventory_change(
        current, expected_version=command.expected_version,
        delta_on_hand=command.delta_on_hand, delta_reserved=command.delta_reserved,
    )
    return {"replayed": False, "fingerprint": fingerprint, "next_state": next_state}
