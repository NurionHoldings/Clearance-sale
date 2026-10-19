"""Read-only administrator security alert service.

Requires a trusted server-side principal and an injected aggregate loader.
This module does not expose HTTP routes or connect to a live database.
"""
from .seller_login_alert_projection import project_login_alerts


class SecurityAlertsUnavailable(PermissionError):
    pass


def get_admin_security_alerts(*, principal, load_aggregates,
                              max_alerts=100):
    """Deny by default, including invalid or inactive administrator roles."""
    if (not isinstance(principal, dict)
            or principal.get("authenticated") is not True
            or principal.get("active") is not True
            or principal.get("role") != "security_admin"):
        raise SecurityAlertsUnavailable("Security alerts unavailable")
    if not callable(load_aggregates):
        raise SecurityAlertsUnavailable("Security alerts unavailable")
    try:
        alerts = project_login_alerts(
            load_aggregates(), max_alerts=max_alerts)
        return {
            "read_only": True,
            "alerts": [
                {"severity": alert.severity, "reason": alert.reason,
                 "attempts": alert.attempts,
                 "bucket_digest": alert.bucket_digest}
                for alert in alerts
            ],
            "total_returned": len(alerts),
        }
    except Exception:
        raise SecurityAlertsUnavailable("Security alerts unavailable") from None
