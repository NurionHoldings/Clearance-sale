"""Reusable preflight checks for a future seller authentication HTTP adapter.

The caller must pass a trusted HTTPS scheme and an allowlisted Origin.
This module does not launch a route or read credentials.
"""
from urllib.parse import urlsplit


def trusted_origin(origin, allowed_origins):
    if not isinstance(origin, str) or not isinstance(allowed_origins, (tuple, frozenset)):
        return False
    if origin not in allowed_origins:
        return False
    try:
        parsed = urlsplit(origin)
        return (parsed.scheme == "https" and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and parsed.path == "" and parsed.query == "" and parsed.fragment == "")
    except ValueError:
        return False


def auth_request_allowed(*, method, scheme, origin, allowed_origins,
                         content_type, content_length, attempt_allowed):
    """Deny by default; attempt_allowed comes from trusted server rate limiter."""
    if method != "POST" or scheme != "https":
        return False
    if not trusted_origin(origin, allowed_origins):
        return False
    if attempt_allowed is not True:
        return False
    if not isinstance(content_type, str) or content_type.split(";", 1)[0].strip().lower() != "application/json":
        return False
    return type(content_length) is int and 0 < content_length <= 4096


def session_cookie_header(token):
    """Build an HTTPS-only host cookie; token must be URL-safe."""
    if (not isinstance(token, str) or not 32 <= len(token) <= 256
            or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in token)):
        raise ValueError("Invalid session token")
    return "__Host-seller_session=" + token + "; Path=/; Secure; HttpOnly; SameSite=Strict"


def clear_session_cookie_header():
    return "__Host-seller_session=; Path=/; Max-Age=0; Secure; HttpOnly; SameSite=Strict"
