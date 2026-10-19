"""Offline privacy and auth-event wiring tests."""
import unittest
from unittest.mock import patch
from backend.seller_auth_events import make_auth_event, emit_auth_event
from backend.seller_throttled_login_flow import handle_throttled_login


class Throttle:
    def __init__(self, allowed):
        self.allowed = allowed
    def consume(self, digest):
        return self.allowed


class AuthEventTests(unittest.TestCase):
    def test_event_schema_only_contains_fixed_code_and_digest(self):
        event = make_auth_event("login_denied", "a" * 64)
        self.assertEqual(set(vars(event)), {"code", "bucket_digest"})
        for code in ("password=secret", "login_unknown"):
            with self.assertRaises(ValueError):
                make_auth_event(code, "a" * 64)

    def test_reporter_error_does_not_escape(self):
        def broken(event):
            raise RuntimeError("logging unavailable")
        emit_auth_event(broken, "login_denied", "a" * 64)

    def test_blocked_login_reports_throttle_without_authenticating(self):
        events = []
        args = dict(
            client_ip="192.0.2.10", throttle_secret=b"s" * 32,
            throttle=Throttle(False), store=object(), method="POST",
            scheme="https", origin="https://seller.example.com",
            allowed_origins=("https://seller.example.com",),
            content_type="application/json", content_length=100,
            credentials={"user_id": "user-1", "password": "secret-value"},
            report_event=events.append,
        )
        with patch("backend.seller_auth_request_adapter.authenticate_seller") as auth:
            status, _, cookie = handle_throttled_login(**args)
        self.assertEqual(status, 403)
        self.assertIsNone(cookie)
        auth.assert_not_called()
        self.assertEqual([e.code for e in events], ["login_throttled"])
        self.assertNotIn("secret-value", repr(events))


if __name__ == "__main__":
    unittest.main()
