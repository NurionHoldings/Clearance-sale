"""Fail-closed read-only seller dashboard application boundary.

This module is NOT an HTTP endpoint or authentication implementation.
A future server must load principal, membership and scoped inventory from
trusted server-side stores. Browser-provided seller identity is never trusted.
"""
from .seller_access_policy import AccessDecision, can_access_seller_inventory
from .seller_dashboard_contract import build_seller_dashboard


class SellerAccessDenied(PermissionError):
    """No seller inventory data may be returned to an unauthorized caller."""


def get_authorized_seller_dashboard(
    *, principal, membership, seller_id, load_inventory, status="all",
    low_stock_threshold=5,
):
    """Authorize BEFORE invoking the trusted seller-scoped inventory loader."""
    if can_access_seller_inventory(
        principal, membership, seller_id=seller_id, action="read"
    ) is not AccessDecision.ALLOW:
        raise SellerAccessDenied("Seller inventory access denied")

    if not callable(load_inventory):
        raise TypeError("Trusted inventory loader is required")

    # The loader must enforce seller_id in its DB query; never return a
    # cross-tenant collection and filter it only after fetching.
    items = load_inventory(seller_id)
    return build_seller_dashboard(
        items, status=status, low_stock_threshold=low_stock_threshold
    )
