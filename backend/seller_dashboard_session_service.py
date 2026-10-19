"""Trusted-session seller dashboard composition; no HTTP or DB connection.

All loaders are injected trusted server-side functions. The session resolves to
a verified principal; membership is looked up by verified user and seller.
Inventory queries MUST filter by seller at the database and each returned row
is checked again for tenant scope. This endpoint-like composition is read-only.
"""
from .seller_access_policy import (
    AccessDecision, SellerMembership, SellerPrincipal, can_access_seller_inventory,
)
from .seller_dashboard_service import SellerAccessDenied, get_authorized_seller_dashboard
from .seller_inventory_scope import InventoryScopeError, scoped_inventory_loader


def get_session_seller_dashboard(
    *, session_token, seller_id, load_session, load_membership,
    query_inventory_by_seller, status="all", low_stock_threshold=5,
    report_error=None,
):
    if not isinstance(session_token, str) or not session_token.strip():
        raise SellerAccessDenied("Missing authenticated session")
    if not isinstance(seller_id, str) or not seller_id.strip():
        raise SellerAccessDenied("Missing seller identity")
    if not all(callable(loader) for loader in (
        load_session, load_membership, query_inventory_by_seller,
    )):
        raise SellerAccessDenied("Trusted server loaders required")
    if report_error is not None and not callable(report_error):
        raise SellerAccessDenied("Invalid diagnostic reporter")

    def record_failure(stage):
        if report_error is not None:
            try:
                report_error("seller_dashboard_dependency_failed", stage)
            except Exception:
                pass  # Diagnostics must not replace the safe public failure.

    try:
        principal = load_session(session_token)
    except Exception:
        record_failure("session")
        raise SellerAccessDenied("Seller dashboard unavailable") from None
    if not isinstance(principal, SellerPrincipal) or not principal.authenticated:
        raise SellerAccessDenied("Unauthenticated principal")
    if not isinstance(principal.user_id, str) or not principal.user_id.strip():
        raise SellerAccessDenied("Invalid principal")
    try:
        membership = load_membership(principal.user_id, seller_id)
    except Exception:
        record_failure("membership")
        raise SellerAccessDenied("Seller dashboard unavailable") from None
    if not isinstance(membership, SellerMembership) or (
        can_access_seller_inventory(
            principal, membership, seller_id=seller_id, action="read"
        ) is not AccessDecision.ALLOW
    ):
        raise SellerAccessDenied("Seller membership denied")
    try:
        return get_authorized_seller_dashboard(
            principal=principal, membership=membership, seller_id=seller_id,
            load_inventory=scoped_inventory_loader(query_inventory_by_seller),
            status=status, low_stock_threshold=low_stock_threshold,
        )
    except InventoryScopeError:
        record_failure("inventory_scope")
        raise SellerAccessDenied("Seller dashboard unavailable") from None
    except Exception:
        record_failure("dashboard")
        raise SellerAccessDenied("Seller dashboard unavailable") from None
