"""Offline integration tests for throttled seller login composition."""
import unittest
from unittest.mock import patch

from backend.seller_throttled_login_flow import handle_throttled_login


class Throttle:
    def __init__(self, allowed):
        self.allowed = allowed
        self.calls = []
    def consume(self, digest):
        self.calls.append(digest)
        return self.allowed


class ThrottledLoginTests(unittest.TestCase):
    def setUp(self):
        self.args = dict(
            client_ip="192.0.2.10", throttle_secret=b"s" * 32,
            throttle=Throttle(True), store=object(), method="POST",
            scheme="https", origin="https://seller.example.com",
            allowed_origins=("https://seller.example.com",),
            content_type="application/json", content_length=100,
            credentials={"user_id": "user-1", "password": "example-password"},
        )

    def test_allowed_attempt_reaches_authentication(self):
        with patch("backend.seller_auth_request_adapter.authenticate_seller") as auth:
            from datetime import datetime, timezone
            auth.return_value = ("A" * 40, datetime.now(timezone.utc))
            status, body, cookie = handle_throttled_login(**self.args)
        self.assertEqual(status, 200)
        self.assertTrue(body["authenticated"])
        self.assertIn("__Host-seller_session=", cookie)
        self.assertEqual(auth.call_count, 1)
        self.assertEqual(len(self.args["throttle"].calls), 1)

    def test_exceeded_limit_never_checks_password(self):
        self.args["throttle"] = Throttle(False)
        with patch("backend.seller_auth_request_adapter.authenticate_seller") as auth:
            status, body, cookie = handle_throttled_login(**self.args)
        self.assertEqual(status, 403)
        self.assertIsNone(cookie)
        auth.assert_not_called()

    def test_invalid_client_address_fails_closed(self):
        self.args["client_ip"] = "untrusted-forwarded-header"
        with patch("backend.seller_auth_request_adapter.authenticate_seller") as auth:
            status, _, _ = handle_throttled_login(**self.args)
        self.assertEqual(status, 403)
        auth.assert_not_called()
        self.assertEqual(self.args["throttle"].calls, [])


if __name__ == "__main__":
    unittest.main()
