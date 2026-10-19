"""Offline tests for the read-only dashboard response boundary."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_read_response import seller_dashboard_read_response
from backend.seller_inventory_view import InventoryItem


class SellerDashboardReadResponseTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.kwargs = {
            "session_token": "server-verified-session",
            "seller_id": "seller-A",
            "load_session": lambda token: SellerPrincipal("user-1", True),
            "load_membership": lambda user, seller: SellerMembership(
                "user-1", "seller-A", "viewer", "active"
            ),
            "query_inventory_by_seller": lambda seller: [
                ("seller-A", InventoryItem("sku-1", "Example", 8, 1, True))
            ],
        }

    def test_authorized_response_is_read_only(self):
        code, body = seller_dashboard_read_response(**self.kwargs)
        self.assertEqual(code, 200)
        self.assertTrue(body["read_only"])
        self.assertEqual(body["visible_count"], 1)

    def test_missing_session_does_not_call_dependencies(self):
        def forbidden(*args):
            self.fail("No dependency should be called")
        args = dict(self.kwargs, session_token="", load_session=forbidden)
        code, body = seller_dashboard_read_response(**args)
        self.assertEqual((code, body), (403, {
            "error": "seller_dashboard_unavailable"
        }))

    def test_cross_tenant_row_never_leaks(self):
        args = dict(self.kwargs, query_inventory_by_seller=lambda seller: [
            ("seller-B", InventoryItem("private-sku", "Private", 5, 0, True))
        ])
        code, body = seller_dashboard_read_response(**args)
        self.assertEqual(code, 403)
        self.assertEqual(body, {"error": "seller_dashboard_unavailable"})
        self.assertNotIn("private", repr(body))

    def test_dependency_failure_does_not_leak_details(self):
        def broken(*args):
            raise RuntimeError("database-secret-and-private-host")
        args = dict(self.kwargs, load_session=broken)
        code, body = seller_dashboard_read_response(**args)
        self.assertEqual(code, 403)
        self.assertEqual(body, {"error": "seller_dashboard_unavailable"})
        self.assertNotIn("secret", repr(body))


if __name__ == "__main__":
    unittest.main()
