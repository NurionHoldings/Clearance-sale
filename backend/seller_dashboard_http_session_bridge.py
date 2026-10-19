"""Trusted HTTP-session bridge for the read-only seller dashboard.

The hosting framework must supply a verified server-side session lookup.
Only an opaque cookie value is accepted; user/role/seller identity always
comes from trusted loaders. This module does not install a live route.
"""
from http.cookies import CookieError, SimpleCookie

from .seller_dashboard_route_adapter import handle_seller_dashboard_request

SESSION_COOKIE = "seller_session"


def extract_seller_session(cookie_header):
    """Read a single opaque cookie; reject ambiguous or malformed headers."""
    if not isinstance(cookie_header, str) or not cookie_header or len(cookie_header) > 8192:
        return None
    try:
        parsed = SimpleCookie()
        parsed.load(cookie_header)
        if SESSION_COOKIE not in parsed:
            return None
        token = parsed[SESSION_COOKIE].value
    except (CookieError, ValueError, TypeError):
        return None
    if not token or len(token) > 4096 or any(ord(c) < 33 or ord(c) > 126 for c in token):
        return None
    return token


def handle_cookie_authenticated_dashboard(
    *, method, cookie_header, seller_id, load_session, load_membership,
    query_inventory_by_seller, status="all", low_stock_threshold=5,
    report_error=None,
):
    """Bridge framework request data to trusted GET-only authorization."""
    token = extract_seller_session(cookie_header)
    return handle_seller_dashboard_request(
        method=method, session_token=token, seller_id=seller_id,
        load_session=load_session, load_membership=load_membership,
        query_inventory_by_seller=query_inventory_by_seller,
        status=status, low_stock_threshold=low_stock_threshold,
        report_error=report_error,
    )
