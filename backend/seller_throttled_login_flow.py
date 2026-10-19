"""Trusted server composition for seller login throttling.

Not an HTTP endpoint. The caller must supply verified client IP and a
server-only shared secret, plus a dedicated transactional throttle store.
"""
from .seller_auth_request_adapter import handle_auth_request
from .seller_login_throttle_identity import login_throttle_bucket


def handle_throttled_login(*, client_ip, throttle_secret, throttle, store,
                           method, scheme, origin, allowed_origins,
                           content_type, content_length, credentials):
    """Consume a login attempt before any credential lookup; fail closed."""
    allowed = False
    try:
        bucket = login_throttle_bucket(client_ip=client_ip, secret=throttle_secret)
        allowed = throttle.consume(bucket) is True
    except (TypeError, ValueError, AttributeError):
        allowed = False
    return handle_auth_request(
        action="login", method=method, scheme=scheme, origin=origin,
        allowed_origins=allowed_origins, content_type=content_type,
        content_length=content_length, attempt_allowed=allowed,
        store=store, credentials=credentials,
    )
