"""Pure seller session lifecycle primitives (no database or HTTP endpoint).

The caller must authenticate credentials before issuing a session and persist
only token_digest in a trusted server-side store. Never log raw tokens.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
import uuid

from .seller_access_policy import SellerPrincipal

MAX_SESSION_AGE = timedelta(hours=12)


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    user_id: str
    token_digest: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


def _utc(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timezone-aware timestamp required")
    return value.astimezone(timezone.utc)


def digest_session_token(token):
    if not isinstance(token, str) or not token or len(token) > 4096:
        raise ValueError("Invalid session token")
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_session(*, user_id, now=None):
    """Issue only after trusted authentication; return raw token once."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise ValueError("Verified user ID required")
    issued = _utc(now if now is not None else datetime.now(timezone.utc))
    token = secrets.token_urlsafe(32)
    record = SessionRecord(
        session_id=str(uuid.uuid4()), user_id=user_id,
        token_digest=digest_session_token(token), created_at=issued,
        expires_at=issued + MAX_SESSION_AGE,
    )
    return token, record


def verify_session(*, token, record, now=None):
    """Return authenticated principal only for a matching live record."""
    if not isinstance(record, SessionRecord):
        return None
    try:
        checked = _utc(now if now is not None else datetime.now(timezone.utc))
        created, expires = _utc(record.created_at), _utc(record.expires_at)
        if (not isinstance(record.user_id, str) or not record.user_id.strip()
                or record.revoked_at is not None or checked < created
                or checked >= expires or expires - created > MAX_SESSION_AGE):
            return None
        if not hmac.compare_digest(digest_session_token(token), record.token_digest):
            return None
    except (TypeError, ValueError):
        return None
    return SellerPrincipal(record.user_id, True)


def revoke_session(record, *, now=None):
    """Return a revoked copy; caller must persist it atomically."""
    if not isinstance(record, SessionRecord):
        raise ValueError("Session record required")
    revoked = _utc(now if now is not None else datetime.now(timezone.utc))
    if revoked < _utc(record.created_at):
        raise ValueError("Revocation predates issuance")
    from dataclasses import replace
    return replace(record, revoked_at=record.revoked_at or revoked)
