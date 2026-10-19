"""Database-independent optimistic inventory update contract.

A future SQL adapter must execute compare-and-swap within one transaction:
UPDATE inventory_balances SET on_hand=?, reserved=?, version=version+1
WHERE product_id=? AND version=?; require exactly one affected row.
This module does not connect to a database or perform mutations.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryVersion:
    product_id: str
    on_hand: int
    reserved: int
    version: int


class InventoryConflict(ValueError):
    """The inventory version is stale or an operation is invalid."""


def plan_inventory_change(current, *, expected_version, delta_on_hand=0, delta_reserved=0):
    """Compute an immutable next version; reject stale, invalid or unsafe writes."""
    if not isinstance(current, InventoryVersion):
        raise InventoryConflict("Invalid inventory snapshot")
    if not isinstance(current.product_id, str) or not current.product_id.strip():
        raise InventoryConflict("Invalid product identity")
    for value in (current.on_hand, current.reserved, current.version,
                  expected_version, delta_on_hand, delta_reserved):
        if type(value) is not int:
            raise InventoryConflict("Inventory values and versions must be integers")
    if current.on_hand < 0 or current.reserved < 0 or current.reserved > current.on_hand:
        raise InventoryConflict("Invalid inventory balance")
    if current.version < 0 or expected_version != current.version:
        raise InventoryConflict("Stale inventory version")
    next_on_hand = current.on_hand + delta_on_hand
    next_reserved = current.reserved + delta_reserved
    if next_on_hand < 0 or next_reserved < 0 or next_reserved > next_on_hand:
        raise InventoryConflict("Insufficient stock or invalid reservation")
    return InventoryVersion(
        product_id=current.product_id,
        on_hand=next_on_hand,
        reserved=next_reserved,
        version=current.version + 1,
    )


def require_compare_and_swap_result(affected_rows):
    """Fail closed when the future transactional UPDATE did not affect one row."""
    if type(affected_rows) is not int or affected_rows != 1:
        raise InventoryConflict("Inventory update conflict or ambiguous write")
    return True
