"""Read-only, deterministic suspicious-login alert projection.

Input is trusted aggregate counts from a server-side, bounded time window.
No raw credentials, IP addresses, tokens, or individual user identities.
"""
from dataclasses import dataclass
import re

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_ALLOWED = frozenset({"login_denied", "login_throttled"})


@dataclass(frozen=True)
class SellerLoginAlert:
    bucket_digest: str
    severity: str
    reason: str
    attempts: int


def project_login_alerts(aggregates, *, warning_threshold=5,
                         critical_threshold=15, max_alerts=100):
    """Project bounded alert summaries without any outbound notification."""
    if (type(warning_threshold) is not int or warning_threshold < 1
            or type(critical_threshold) is not int
            or critical_threshold <= warning_threshold
            or type(max_alerts) is not int or not 1 <= max_alerts <= 1000):
        raise ValueError("Invalid alert policy")
    if not isinstance(aggregates, (list, tuple)) or len(aggregates) > 10000:
        raise ValueError("Bounded aggregates required")
    counts = {}
    for row in aggregates:
        if not isinstance(row, (tuple, list)) or len(row) != 3:
            raise ValueError("Invalid aggregate")
        digest, code, count = row
        if (not isinstance(digest, str) or not _DIGEST.fullmatch(digest)
                or code not in _ALLOWED or type(count) is not int
                or not 0 <= count <= 1000000):
            raise ValueError("Invalid aggregate")
        counts[digest] = counts.get(digest, 0) + count
    alerts = []
    for digest, count in counts.items():
        if count >= warning_threshold:
            severity = "critical" if count >= critical_threshold else "warning"
            alerts.append(SellerLoginAlert(
                bucket_digest=digest, severity=severity,
                reason="repeated_authentication_denials", attempts=count))
    alerts.sort(key=lambda item: (-item.attempts, item.bucket_digest))
    return alerts[:max_alerts]
