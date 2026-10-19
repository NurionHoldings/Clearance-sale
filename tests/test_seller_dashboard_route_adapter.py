"""Offline tests for the GET-only seller dashboard route adapter."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_route_adapter import handle_seller_dashboard_request
from backend.seller_inventory_view import InventoryItem


class SellerDashboardRouteAdapterTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.kwargs = dict(
            method="GET", session_token="trusted-session", seller_id="seller-A",
            load_session=lambda token: SellerPrincipal("user-1", True),
            load_membership=lambda user, seller: SellerMembership(
                "user-1", "seller-A", "viewer", "active"
            ),
            query_inventory_by_seller=lambda seller: [
                ("seller-A", InventoryItem("sku-1", "Example", 8, 1, True))
            ],
        )

    def test_get_is_read_only(self):
        code, payload = handle_seller_dashboard_request(**self.kwargs)
        self.assertEqual(code, 200)
        self.assertTrue(payload["read_only"])
        self.assertEqual(payload["visible_count"], 1)

    def test_mutating_methods_are_rejected_before_loader(self):
        def forbidden(*args):
            self.fail("Must reject before calling trusted loaders")
        for method in ("POST", "PUT", "PATCH", "DELETE", None):
            with self.subTest(method=method):
                args = dict(self.kwargs, method=method, load_session=forbidden)
                code, payload = handle_seller_dashboard_request(**args)
                self.assertEqual(code, 405)
                self.assertEqual(payload["allowed_methods"], ["GET"])

    def test_invalid_filters_are_rejected_before_loader(self):
        def forbidden(*args):
            self.fail("Invalid input must not reach session loader")
        for status in ("unknown", None, [], {}):
            with self.subTest(status=status):
                args = dict(self.kwargs, status=status, load_session=forbidden)
                self.assertEqual(
                    handle_seller_dashboard_request(**args),
                    (400, {"error": "invalid_filter"}),
                )

    def test_invalid_threshold_is_rejected_before_loader(self):
        def forbidden(*args):
            self.fail("Invalid input must not reach session loader")
        for threshold in (-1, 1000001, True, "5", None):
            with self.subTest(threshold=threshold):
                args = dict(self.kwargs, low_stock_threshold=threshold,
                            load_session=forbidden)
                self.assertEqual(
                    handle_seller_dashboard_request(**args),
                    (400, {"error": "invalid_threshold"}),
                )


if __name__ == "__main__":
    unittest.main()
