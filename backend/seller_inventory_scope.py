"""Tenant-scoped inventory loader contract for future database adapters.

No database is connected here. Adapters must enforce seller scope in the query,
not fetch all tenants and filter in Python.
"""
from .seller_inventory_view import InventoryItem


class InventoryScopeError(ValueError):
    """A trusted loader returned a record outside the authorized seller scope."""


def verify_scoped_inventory(seller_id, records):
    """Validate trusted query results before projecting them to a dashboard.

    Each record must be (record_seller_id, InventoryItem). Fail the entire
    response on any malformed or cross-tenant row; never silently discard it.
    """
    if not isinstance(seller_id, str) or not seller_id.strip():
        raise InventoryScopeError("Invalid seller scope")
    if not isinstance(records, (tuple, list)):
        raise InventoryScopeError("Expected a materialized scoped record collection")
    items = []
    for record in records:
        if not isinstance(record, (tuple, list)) or len(record) != 2:
            raise InventoryScopeError("Malformed inventory record")
        owner_id, item = record
        if not isinstance(owner_id, str) or owner_id != seller_id:
            raise InventoryScopeError("Cross-tenant inventory row detected")
        if not isinstance(item, InventoryItem):
            raise InventoryScopeError("Invalid inventory item")
        items.append(item)
    return items


def scoped_inventory_loader(query_by_seller):
    """Wrap a trusted query function and enforce record ownership postcondition.

    The query MUST be server-side tenant-filtered; this wrapper is defense in
    depth, not a replacement for database row-level security.
    """
    if not callable(query_by_seller):
        raise TypeError("Trusted seller-scoped query required")

    def load(seller_id):
        return verify_scoped_inventory(seller_id, query_by_seller(seller_id))

    return load
