"""Read-only seller inventory projections; no persistence or external services."""
from dataclasses import dataclass

try:
    from .inventory_rules import available_quantity
except ImportError:
    from inventory_rules import available_quantity


@dataclass(frozen=True)
class InventoryItem:
    sku: str
    name: str
    on_hand: int
    reserved: int
    active: bool = True


def seller_inventory_summary(items):
    """Produce a deterministic snapshot; never mutates the source records."""
    rows = []
    seen = set()
    for item in items:
        if not isinstance(item, InventoryItem):
            raise TypeError("Expected InventoryItem")
        if not item.sku or not item.sku.strip() or item.sku in seen:
            raise ValueError("SKU must be unique and nonempty")
        if not item.name or not item.name.strip():
            raise ValueError("Product name required")
        if type(item.active) is not bool:
            raise TypeError("Active status must be boolean")
        seen.add(item.sku)
        available = available_quantity(item.on_hand, item.reserved)
        rows.append({
            "sku": item.sku,
            "name": item.name,
            "on_hand": item.on_hand,
            "reserved": item.reserved,
            "available": available if item.active else 0,
            "active": item.active,
        })
    rows.sort(key=lambda row: row["sku"])
    return {
        "product_count": len(rows),
        "active_count": sum(row["active"] for row in rows),
        "available_units": sum(row["available"] for row in rows),
        "items": rows,
    }
