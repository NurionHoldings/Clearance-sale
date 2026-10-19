"""Framework-neutral, read-only seller dashboard route adapter.

The host server MUST obtain the session token from a trusted, authenticated
server-side session mechanism. Do not pass a browser-provided user ID, role,
seller membership or product owner into the trusted loaders. This adapter
does not start an HTTP server or create any database connection.
"""
from .seller_dashboard_read_response import seller_dashboard_read_response

ALLOWED_METHOD = "GET"


def handle_seller_dashboard_request(
    *, method, session_token, seller_id, load_session, load_membership,
    query_inventory_by_seller, status="all", low_stock_threshold=5,
    report_error=None,
):
    """Map a GET request to the existing authorization and response boundary."""
    if method != ALLOWED_METHOD:
        return 405, {
            "error": "method_not_allowed",
            "allowed_methods": [ALLOWED_METHOD],
        }
    if not isinstance(status, str) or status not in (
        "all", "active", "inactive", "low_stock", "out_of_stock"
    ):
        return 400, {"error": "invalid_filter"}
    if type(low_stock_threshold) is not int or not 0 <= low_stock_threshold <= 1000000:
        return 400, {"error": "invalid_threshold"}
    return seller_dashboard_read_response(
        session_token=session_token,
        seller_id=seller_id,
        load_session=load_session,
        load_membership=load_membership,
        query_inventory_by_seller=query_inventory_by_seller,
        status=status,
        low_stock_threshold=low_stock_threshold,
        report_error=report_error,
    )
