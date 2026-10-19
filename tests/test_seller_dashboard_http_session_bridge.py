"""Offline regression tests for cookie-authenticated seller dashboard bridge."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_http_session_bridge import (
    extract_seller_session, handle_cookie_authenticated_dashboard,
)
from backend.seller_inventory_view import InventoryItem


class SellerDashboardHttpSessionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tokens = []
        def load_session(token):
            self.tokens.append(token)
            return SellerPrincipal("user-1", True) if token == "verified" else None
        self.args = dict(
            method="GET", cookie_header="seller_session=verified",
            seller_id="seller-A", load_session=load_session,
            load_membership=lambda user, seller: SellerMembership(
                "user-1", "seller-A", "viewer", "active"
            ),
            query_inventory_by_seller=lambda seller: [
                ("seller-A", InventoryItem("sku-1", "Sample", 3, 0, True))
            ],
        )

    def test_cookie_verified_by_trusted_session_loader(self):
        code, body = handle_cookie_authenticated_dashboard(**self.args)
        self.assertEqual(code, 200)
        self.assertTrue(body["read_only"])
        self.assertEqual(self.tokens, ["verified"])

    def test_missing_cookie_fails_closed_without_loader(self):
        code, body = handle_cookie_authenticated_dashboard(
            **dict(self.args, cookie_header="other=abc")
        )
        self.assertEqual(code, 403)
        self.assertEqual(body, {"error": "seller_dashboard_unavailable"})
        self.assertEqual(self.tokens, [])

    def test_invalid_session_is_denied(self):
        code, body = handle_cookie_authenticated_dashboard(
            **dict(self.args, cookie_header="seller_session=unverified")
        )
        self.assertEqual(code, 403)
        self.assertEqual(body, {"error": "seller_dashboard_unavailable"})

    def test_mutating_method_does_not_call_loader(self):
        code, body = handle_cookie_authenticated_dashboard(
            **dict(self.args, method="POST")
        )
        self.assertEqual(code, 405)
        self.assertEqual(self.tokens, [])

    def test_duplicate_session_cookies_are_rejected(self):
        for header in (
            "seller_session=verified; seller_session=unverified",
            "seller_session=unverified; seller_session=verified",
        ):
            with self.subTest(header=header):
                self.assertIsNone(extract_seller_session(header))
                code, body = handle_cookie_authenticated_dashboard(
                    **dict(self.args, cookie_header=header)
                )
                self.assertEqual(code, 403)
                self.assertEqual(body, {"error": "seller_dashboard_unavailable"})
        self.assertEqual(self.tokens, [])

    def test_malformed_cookie_is_rejected(self):
        for value in (None, "", "seller_session=", "x" * 8193):
            with self.subTest(value=str(value)[:12]):
                self.assertIsNone(extract_seller_session(value))


if __name__ == "__main__":
    unittest.main()
