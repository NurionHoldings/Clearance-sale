"""Offline login-to-dashboard composition contract.

This is not a public route and does not connect to a production database.
All stores and inventory queries are injected by a trusted server.
"""
from .seller_dashboard_http_session_bridge import handle_cookie_authenticated_dashboard
from .seller_login_service import resolve_seller_session


def authenticated_dashboard_flow(*, auth_store, seller_id, cookie_header,
                                 query_inventory_by_seller, status="all"):
    """Resolve the server-side session, membership, and scoped inventory."""
    return handle_cookie_authenticated_dashboard(
        method="GET", cookie_header=cookie_header, seller_id=seller_id,
        load_session=lambda token: resolve_seller_session(token=token, store=auth_store),
        load_membership=auth_store.load_membership,
        query_inventory_by_seller=query_inventory_by_seller, status=status,
    )
