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
