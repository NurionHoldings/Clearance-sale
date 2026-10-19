"""Minimal, privacy-safe authentication outcome events.

Only fixed event codes and an HMAC-derived bucket may be recorded.
No passwords, tokens, user IDs, IP addresses or exception details.
"""
from dataclasses import dataclass
import re

_CODES = frozenset({"login_success", "login_denied", "login_throttled",
                    "login_invalid_request", "login_unavailable"})
_BUCKET = re.compile(r"[0-9a-f]{64}\Z")


@dataclass(frozen=True)
class SellerAuthEvent:
    code: str
    bucket_digest: str


def make_auth_event(code, bucket_digest):
    if code not in _CODES:
        raise ValueError("Unsupported auth event")
    if not isinstance(bucket_digest, str) or not _BUCKET.fullmatch(bucket_digest):
        raise ValueError("Invalid private bucket")
    return SellerAuthEvent(code=code, bucket_digest=bucket_digest)


def emit_auth_event(reporter, code, bucket_digest):
    """Best effort only; reporting must not break authentication."""
    if reporter is None:
        return
    try:
        reporter(make_auth_event(code, bucket_digest))
    except Exception:
        pass
