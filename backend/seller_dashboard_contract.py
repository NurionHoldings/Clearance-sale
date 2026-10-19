"""Pure, read-only seller dashboard response builder.

Accepts already-authorized inventory records; it does not authenticate callers,
query a database, or expose an HTTP endpoint.
"""
try:
    from .seller_inventory_view import (
        seller_inventory_summary, seller_dashboard_metrics, filter_inventory_rows
    )
except ImportError:
    from seller_inventory_view import (
        seller_inventory_summary, seller_dashboard_metrics, filter_inventory_rows
    )


def build_seller_dashboard(items, *, status="all", low_stock_threshold=5):
    """Build a JSON-compatible snapshot for a future authenticated UI adapter."""
    snapshot = seller_inventory_summary(items)
    metrics = seller_dashboard_metrics(snapshot, low_stock_threshold)
    filtered = filter_inventory_rows(snapshot, status, low_stock_threshold)
    return {
        "schema_version": 1,
        "read_only": True,
        "filter": status,
        "low_stock_threshold": low_stock_threshold,
        "metrics": metrics,
        "visible_count": len(filtered),
        "products": filtered,
    }


def validate_product_registration_draft(*, sku, name, price_won, on_hand, reserved=0, active=True):
    """Validate a proposed product registration without saving or publishing it."""
    if not isinstance(sku, str) or not 1 <= len(sku.strip()) <= 64:
        raise ValueError("SKU must be 1 to 64 characters")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 200:
        raise ValueError("Product name must be 1 to 200 characters")
    if type(price_won) is not int or not 0 <= price_won <= 1_000_000_000:
        raise ValueError("Price must be an integer between 0 and 1,000,000,000 won")
    if type(on_hand) is not int or not 0 <= on_hand <= 1_000_000:
        raise ValueError("On-hand quantity out of range")
    if type(reserved) is not int or not 0 <= reserved <= on_hand:
        raise ValueError("Reserved quantity out of range")
    if type(active) is not bool:
        raise ValueError("Active status must be boolean")
    return {
        "schema_version": 1,
        "read_only": True,
        "sku": sku.strip(),
        "name": name.strip(),
        "price_won": price_won,
        "on_hand": on_hand,
        "reserved": reserved,
        "active": active,
        "available": on_hand - reserved if active else 0,
    }
