"""Framework-neutral read-only HTTP response boundary for seller dashboards.

A future authenticated server can adapt this result to its framework. This
module neither trusts client identity nor starts a server or database.
"""
from .seller_dashboard_service import SellerAccessDenied
from .seller_dashboard_session_service import get_session_seller_dashboard


def seller_dashboard_read_response(
    *, session_token, seller_id, load_session, load_membership,
    query_inventory_by_seller, status="all", low_stock_threshold=5,
    report_error=None,
):
    """Return (HTTP status, JSON-safe body) without disclosing internal errors."""
    try:
        payload = get_session_seller_dashboard(
            session_token=session_token,
            seller_id=seller_id,
            load_session=load_session,
            load_membership=load_membership,
            query_inventory_by_seller=query_inventory_by_seller,
            status=status,
            low_stock_threshold=low_stock_threshold,
            report_error=report_error,
        )
    except SellerAccessDenied:
        return 403, {"error": "seller_dashboard_unavailable"}
    except Exception:
        return 503, {"error": "seller_dashboard_unavailable"}
    return 200, payload
