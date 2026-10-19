"""Offline seller password hashing using standard-library scrypt."""
import hashlib
import hmac
import secrets

N = 16384
R = 8
P = 1


def valid_password(value):
    return isinstance(value, str) and 12 <= len(value) <= 1024 and len(value.encode("utf-8")) <= 4096


def hash_seller_password(password):
    if not valid_password(password):
        raise ValueError("Password must contain 12-1024 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt,
                            n=N, r=R, p=P, dklen=32)
    return "scrypt$16384$8$1$" + salt.hex() + "$" + digest.hex()


def verify_seller_password(password, encoded):
    if not valid_password(password) or not isinstance(encoded, str):
        return False
    try:
        parts = encoded.split("$")
        if (len(parts) != 6 or parts[:4] != ["scrypt", "16384", "8", "1"]
                or len(parts[4]) != 32 or len(parts[5]) != 64):
            return False
        salt = bytes.fromhex(parts[4])
        expected = bytes.fromhex(parts[5])
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt,
                                n=N, r=R, p=P, dklen=32)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, MemoryError):
        return False
