"""Framework-neutral seller authentication request handler.

Not mounted or deployed. The hosting app must supply trusted HTTPS metadata,
an exact origin allowlist, and a real rate limiter before using this handler.
"""
from .seller_auth_http_security import (
    auth_request_allowed, session_cookie_header, clear_session_cookie_header,
)
from .seller_login_service import authenticate_seller, logout_seller, SellerLoginDenied


def handle_auth_request(*, action, method, scheme, origin, allowed_origins,
                        content_type, content_length, attempt_allowed,
                        store, credentials=None, session_token=None):
    """Return (HTTP status, JSON body, optional Set-Cookie header)."""
    if action not in ("login", "logout"):
        return 404, {"error": "not_found"}, None
    if not auth_request_allowed(
        method=method, scheme=scheme, origin=origin,
        allowed_origins=allowed_origins, content_type=content_type,
        content_length=content_length, attempt_allowed=attempt_allowed,
    ):
        return 403, {"error": "request_denied"}, None
    try:
        if action == "login":
            if not isinstance(credentials, dict) or set(credentials) != {"user_id", "password"}:
                return 400, {"error": "invalid_request"}, None
            token, expires_at = authenticate_seller(
                user_id=credentials["user_id"],
                password=credentials["password"], store=store,
            )
            return 200, {"authenticated": True, "expires_at": expires_at.isoformat()}, session_cookie_header(token)
        if not isinstance(session_token, str) or not session_token:
            return 403, {"error": "request_denied"}, None
        logout_seller(token=session_token, store=store)
        return 200, {"authenticated": False}, clear_session_cookie_header()
    except (SellerLoginDenied, ValueError, TypeError):
        return 403, {"error": "request_denied"}, None
