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
        if not isinstance(item.sku, str) or not 1 <= len(item.sku.strip()) <= 64:
            raise ValueError("SKU must be 1 to 64 characters")
        normalized_sku = item.sku.strip()
        if normalized_sku in seen:
            raise ValueError("Duplicate SKU")
        if not isinstance(item.name, str) or not 1 <= len(item.name.strip()) <= 200:
            raise ValueError("Product name must be 1 to 200 characters")
        if type(item.active) is not bool:
            raise TypeError("Active status must be boolean")
        seen.add(normalized_sku)
        available = available_quantity(item.on_hand, item.reserved)
        rows.append({
            "sku": normalized_sku,
            "name": item.name.strip(),
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



def filter_inventory_rows(summary, status="all", low_stock_threshold=5):
    """Filter an existing snapshot without modifying it or accessing storage.

    Status: all, active, inactive, low_stock, out_of_stock.
    Low stock means 1..threshold available units for an active item.
    """
    allowed = {"all", "active", "inactive", "low_stock", "out_of_stock"}
    if status not in allowed:
        raise ValueError("Unsupported inventory status")
    if type(low_stock_threshold) is not int or low_stock_threshold < 0:
        raise ValueError("Low stock threshold must be a nonnegative integer")
    rows = summary["items"]
    if status == "all":
        selected = rows
    elif status == "active":
        selected = [row for row in rows if row["active"]]
    elif status == "inactive":
        selected = [row for row in rows if not row["active"]]
    elif status == "low_stock":
        selected = [row for row in rows if row["active"] and 0 < row["available"] <= low_stock_threshold]
    else:
        selected = [row for row in rows if row["active"] and row["available"] == 0]
    return [row.copy() for row in selected]


def seller_dashboard_metrics(summary, low_stock_threshold=5):
    """Read-only dashboard counters and sorted actionable inventory alerts."""
    if type(low_stock_threshold) is not int or low_stock_threshold < 0:
        raise ValueError("Low stock threshold must be a nonnegative integer")
    low = filter_inventory_rows(summary, "low_stock", low_stock_threshold)
    sold_out = filter_inventory_rows(summary, "out_of_stock", low_stock_threshold)
    inactive = filter_inventory_rows(summary, "inactive", low_stock_threshold)
    alerts = [
        {"sku": row["sku"], "name": row["name"], "type": "out_of_stock", "available": 0}
        for row in sold_out
    ] + [
        {"sku": row["sku"], "name": row["name"], "type": "low_stock", "available": row["available"]}
        for row in low
    ]
    alerts.sort(key=lambda row: (0 if row["type"] == "out_of_stock" else 1, row["available"], row["sku"]))
    return {
        "product_count": summary["product_count"],
        "active_count": summary["active_count"],
        "inactive_count": len(inactive),
        "available_units": summary["available_units"],
        "low_stock_count": len(low),
        "out_of_stock_count": len(sold_out),
        "alerts": alerts,
    }
