"""Administrator-only read model combining alert counts with review state.

No HTTP route or database connection is created. Callers provide trusted
server-side aggregate and review loaders; source events remain immutable.
"""
from .admin_security_alert_service import (
    SecurityAlertsUnavailable, get_admin_security_alerts,
)
from .admin_security_alert_review import SecurityAlertReview


def get_admin_security_alert_dashboard(*, principal, load_aggregates,
                                       load_review, max_alerts=100):
    """Join only authorized alerts to their independent review states."""
    base = get_admin_security_alerts(
        principal=principal, load_aggregates=load_aggregates,
        max_alerts=max_alerts,
    )
    if not callable(load_review):
        raise SecurityAlertsUnavailable("Security alerts unavailable")
    try:
        alerts = []
        for alert in base["alerts"]:
            review = load_review(alert["bucket_digest"])
            if review is not None and (
                not isinstance(review, SecurityAlertReview)
                or review.bucket_digest != alert["bucket_digest"]
                or review.state not in ("open", "reviewing", "resolved")
                or type(review.version) is not int or review.version < 1
            ):
                raise ValueError("Invalid security review")
            alerts.append({
                **alert,
                "review_state": "open" if review is None else review.state,
                "review_version": 0 if review is None else review.version,
            })
        return {
            "read_only": True,
            "alerts": alerts,
            "total_returned": len(alerts),
        }
    except Exception:
        raise SecurityAlertsUnavailable("Security alerts unavailable") from None
