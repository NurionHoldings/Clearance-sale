"""Seller login/session composition with a trusted transactional store.

The caller must supply a trusted account identifier and enforce rate limits,
CSRF defenses and secure cookie handling at the HTTP boundary.
No network listener, database connection or automatic migration is created.
"""
from .seller_password_security import verify_seller_password
from .seller_session_lifecycle import issue_session, verify_session


class SellerLoginDenied(PermissionError):
    pass


def authenticate_seller(*, user_id, password, store, now=None):
    """Verify an active account, then commit a newly issued session."""
    if not isinstance(user_id, str) or not user_id.strip():
        raise SellerLoginDenied("Invalid credentials")
    if not all(callable(getattr(store, name, None)) for name in
               ("get_active_account_hash", "save_session")):
        raise SellerLoginDenied("Authentication unavailable")
    connection = getattr(store, "connection", None)
    if connection is None or not callable(getattr(connection, "commit", None)):
        raise SellerLoginDenied("Authentication unavailable")
    try:
        password_hash = store.get_active_account_hash(user_id)
        if not verify_seller_password(password, password_hash):
            raise SellerLoginDenied("Invalid credentials")
        token, record = issue_session(user_id=user_id, now=now)
        store.save_session(record)
        connection.commit()
        return token, record.expires_at
    except Exception:
        if callable(getattr(connection, "rollback", None)):
            try:
                connection.rollback()
            except Exception:
                pass
        raise SellerLoginDenied("Authentication unavailable") from None


def resolve_seller_session(*, token, store, now=None):
    """Resolve a verified principal from a persisted active session."""
    if not callable(getattr(store, "load_session_record", None)):
        return None
    try:
        record = store.load_session_record(token)
        return verify_session(token=token, record=record, now=now)
    except Exception:
        return None


def logout_seller(*, token, store):
    """Revoke and commit before reporting logout success."""
    connection = getattr(store, "connection", None)
    if (connection is None or not callable(getattr(connection, "commit", None))
            or not callable(getattr(store, "revoke_token", None))):
        raise SellerLoginDenied("Logout unavailable")
    try:
        revoked_count = store.revoke_token(token)
        if type(revoked_count) is not int or revoked_count != 1:
            raise SellerLoginDenied("Logout unavailable")
        connection.commit()
    except Exception:
        if callable(getattr(connection, "rollback", None)):
            try:
                connection.rollback()
            except Exception:
                pass
        raise SellerLoginDenied("Logout unavailable") from None
