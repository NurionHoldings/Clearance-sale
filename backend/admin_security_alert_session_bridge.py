"""Trusted-session boundary for administrator security alert reads.

No public route, cookie authentication provider or production DB is created.
The hosting app must resolve the session token from an HttpOnly cookie and
resolve its principal through a trusted server-side session store.
"""
from .admin_security_alert_api_adapter import handle_admin_security_alerts_request


def handle_session_admin_security_alerts(*, method, session_token,
                                         resolve_admin_session,
                                         load_aggregates, load_review,
                                         max_alerts=100):
    """Deny missing/invalid sessions before touching any alert loaders."""
    if method != "GET":
        return 405, {"error": "method_not_allowed"}, {"Cache-Control": "no-store"}
    if (not isinstance(session_token, str) or not 32 <= len(session_token) <= 256
            or not callable(resolve_admin_session)):
        return 403, {"error": "security_alerts_unavailable"}, {"Cache-Control": "no-store"}
    try:
        principal = resolve_admin_session(session_token)
    except Exception:
        principal = None
    status, payload = handle_admin_security_alerts_request(
        method=method, principal=principal, load_aggregates=load_aggregates,
        load_review=load_review, max_alerts=max_alerts,
    )
    return status, payload, {
        "Cache-Control": "no-store",
        "Content-Type": "application/json; charset=utf-8",
        "X-Content-Type-Options": "nosniff",
    }
