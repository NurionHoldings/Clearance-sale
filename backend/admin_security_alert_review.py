"""Separate acknowledgement contract for security alerts.

Original authentication events are immutable. Acknowledgements are a distinct
administrative record, not an edit to the alert or source events.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import re

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_STATES = frozenset({"open", "reviewing", "resolved"})


@dataclass(frozen=True)
class SecurityAlertReview:
    bucket_digest: str
    state: str
    updated_at: datetime
    version: int


def transition_security_alert_review(*, principal, current, bucket_digest,
                                     next_state, now=None):
    """Validate a single optimistic-lock state transition; no persistence."""
    if (not isinstance(principal, dict)
            or principal.get("authenticated") is not True
            or principal.get("active") is not True
            or principal.get("role") != "security_admin"):
        raise PermissionError("Security review unavailable")
    if (not isinstance(bucket_digest, str) or not _DIGEST.fullmatch(bucket_digest)
            or next_state not in _STATES):
        raise ValueError("Invalid security review")
    if current is not None:
        if (not isinstance(current, SecurityAlertReview)
                or current.bucket_digest != bucket_digest
                or current.state not in _STATES
                or type(current.version) is not int or current.version < 1):
            raise ValueError("Invalid current review")
        permitted = {"open": {"reviewing"}, "reviewing": {"resolved", "open"},
                     "resolved": {"open"}}
        if next_state not in permitted[current.state]:
            raise ValueError("Invalid review transition")
    elif next_state != "open":
        raise ValueError("New reviews must start open")
    timestamp = datetime.now(timezone.utc) if now is None else now
    if (not isinstance(timestamp, datetime) or timestamp.tzinfo is None
            or timestamp.utcoffset() is None):
        raise ValueError("Timezone-aware timestamp required")
    return SecurityAlertReview(bucket_digest, next_state, timestamp,
                               1 if current is None else current.version + 1)
