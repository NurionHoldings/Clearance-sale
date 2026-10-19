"""Framework-neutral read-only administrator security alerts API boundary.

No route is mounted. The hosting server must resolve the administrator
principal from a trusted session, never from request JSON or query strings.
"""
from .admin_security_alert_dashboard import get_admin_security_alert_dashboard
from .admin_security_alert_service import SecurityAlertsUnavailable


def handle_admin_security_alerts_request(*, method, principal,
                                         load_aggregates, load_review,
                                         max_alerts=100):
    """Return (HTTP status, JSON body) with generic failures and no caching."""
    if method != "GET":
        return 405, {"error": "method_not_allowed"}
    if type(max_alerts) is not int or not 1 <= max_alerts <= 100:
        return 400, {"error": "invalid_request"}
    try:
        payload = get_admin_security_alert_dashboard(
            principal=principal, load_aggregates=load_aggregates,
            load_review=load_review, max_alerts=max_alerts,
        )
        return 200, payload
    except SecurityAlertsUnavailable:
        return 403, {"error": "security_alerts_unavailable"}
    except Exception:
        return 503, {"error": "security_alerts_unavailable"}
