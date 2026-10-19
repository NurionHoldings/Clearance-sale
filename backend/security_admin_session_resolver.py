"""Trusted administrator session resolution for security dashboard access.

A valid seller session alone is never administrator authorization.
The role loader must query trusted server-side administration records.
No routes, admin grants, or production resources are created.
"""
from .seller_login_service import resolve_seller_session


def resolve_security_admin(*, token, auth_store, load_admin_role, now=None):
    """Fail closed unless session is live AND a separate active admin grant exists."""
    if not callable(load_admin_role):
        return None
    principal = resolve_seller_session(token=token, store=auth_store, now=now)
    if principal is None or principal.authenticated is not True:
        return None
    try:
        grant = load_admin_role(principal.user_id)
        if (not isinstance(grant, dict)
                or grant.get("role") != "security_admin"
                or grant.get("active") is not True):
            return None
    except Exception:
        return None
    return {"authenticated": True, "active": True, "role": "security_admin"}


def security_admin_session_resolver(*, auth_store, load_admin_role, now=None):
    """Bind trusted stores for use by the read-only HTTP session bridge."""
    return lambda token: resolve_security_admin(
        token=token, auth_store=auth_store,
        load_admin_role=load_admin_role, now=now,
    )
