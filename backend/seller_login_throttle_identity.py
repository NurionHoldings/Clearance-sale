"""Privacy-preserving bucket identifiers for shared authentication throttling."""
import hashlib
import hmac
import ipaddress


def login_throttle_bucket(*, client_ip, secret):
    """Derive a nonreversible per-address bucket using a server-only secret.

    The caller must supply the verified remote address from a trusted proxy,
    never an untrusted forwarded header. The secret must be shared by all nodes.
    """
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("Server secret must contain at least 32 bytes")
    if not isinstance(client_ip, str):
        raise ValueError("Verified IP required")
    address = ipaddress.ip_address(client_ip)
    return hmac.new(secret, address.packed, hashlib.sha256).hexdigest()
