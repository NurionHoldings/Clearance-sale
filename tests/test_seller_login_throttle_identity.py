"""Offline tests for private login throttling identifiers."""
import unittest
from backend.seller_login_throttle_identity import login_throttle_bucket


class LoginThrottleIdentityTests(unittest.TestCase):
    def test_stable_and_secret_bound(self):
        secret = b"x" * 32
        key = login_throttle_bucket(client_ip="192.0.2.1", secret=secret)
        self.assertEqual(len(key), 64)
        self.assertEqual(key, login_throttle_bucket(client_ip="192.0.2.1", secret=secret))
        self.assertNotEqual(key, login_throttle_bucket(client_ip="192.0.2.2", secret=secret))
        self.assertNotEqual(key, login_throttle_bucket(client_ip="192.0.2.1", secret=b"y" * 32))

    def test_invalid_ip_and_weak_secret_denied(self):
        for ip in ("unknown", "192.0.2.1, 198.51.100.2", ""):
            with self.assertRaises(ValueError):
                login_throttle_bucket(client_ip=ip, secret=b"x" * 32)
        with self.assertRaises(ValueError):
            login_throttle_bucket(client_ip="192.0.2.1", secret=b"short")


if __name__ == "__main__":
    unittest.main()
