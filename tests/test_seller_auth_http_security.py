"""Offline regression tests for seller HTTP authentication guards."""
import unittest
from backend.seller_auth_http_security import (
    auth_request_allowed, clear_session_cookie_header,
    session_cookie_header, trusted_origin,
)


class SellerAuthHttpSecurityTests(unittest.TestCase):
    def setUp(self):
        self.origin = "https://seller.example.com"
        self.params = dict(method="POST", scheme="https", origin=self.origin,
                           allowed_origins=(self.origin,),
                           content_type="application/json",
                           content_length=150, attempt_allowed=True)

    def test_valid_request(self):
        self.assertTrue(auth_request_allowed(**self.params))

    def test_bad_transport_origin_or_rate_limit(self):
        for change in ({"scheme": "http"}, {"method": "GET"},
                       {"origin": "https://evil.example.com"},
                       {"attempt_allowed": False}, {"attempt_allowed": 1},
                       {"content_length": 4097}, {"content_length": True},
                       {"content_type": "text/plain"}):
            with self.subTest(change=change):
                self.assertFalse(auth_request_allowed(**(self.params | change)))

    def test_only_exact_allowlisted_https_origin(self):
        self.assertFalse(trusted_origin("http://seller.example.com",
                                        ("http://seller.example.com",)))
        self.assertFalse(trusted_origin("https://seller.example.com.evil.test",
                                        (self.origin,)))
        self.assertTrue(trusted_origin(self.origin, (self.origin,)))

    def test_host_cookie_flags(self):
        header = session_cookie_header("a" * 43)
        self.assertIn("__Host-seller_session=", header)
        self.assertIn("Secure; HttpOnly; SameSite=Strict", header)
        self.assertIn("Path=/", header)
        self.assertNotIn("Domain=", header)
        self.assertIn("Max-Age=0", clear_session_cookie_header())

    def test_cookie_injection_denied(self):
        for token in ("abc", "a" * 43 + "\r\nInjected: yes", "a" * 300):
            with self.assertRaises(ValueError):
                session_cookie_header(token)


if __name__ == "__main__":
    unittest.main()
