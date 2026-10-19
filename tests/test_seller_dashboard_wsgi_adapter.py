"""Offline WSGI contract tests; no network or production services."""
import json
import unittest
from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_inventory_view import InventoryItem
from backend.seller_dashboard_wsgi_adapter import create_wsgi_dashboard


class SellerDashboardWSGITests(unittest.TestCase):
    def setUp(self):
        self.called = []
        def load_session(token):
            self.called.append(token)
            return SellerPrincipal("user-1", True)
        self.app = create_wsgi_dashboard(
            load_session,
            lambda user, seller: SellerMembership(user, seller, "viewer", "active"),
            lambda seller: [(
                seller, InventoryItem("sku-1", "Sample", 2, 0, True)
            )],
        )

    def request(self, path="/api/seller/dashboard", query="seller_id=seller-A",
                method="GET", cookie="seller_session=verified"):
        received = []
        environ = {"PATH_INFO": path, "QUERY_STRING": query,
                   "REQUEST_METHOD": method, "HTTP_COOKIE": cookie}
        data = b"".join(self.app(
            environ, lambda status, headers: received.append((status, headers))
        ))
        return received[0], json.loads(data)

    def test_authorized_get(self):
        (status, headers), body = self.request()
        self.assertTrue(status.startswith("200 "))
        self.assertTrue(body["read_only"])
        self.assertIn(("Cache-Control", "no-store"), headers)

    def test_missing_cookie_denied(self):
        (status, _), body = self.request(cookie="")
        self.assertTrue(status.startswith("403 "))
        self.assertEqual(body, {"error": "seller_dashboard_unavailable"})

    def test_mutation_denied(self):
        (status, headers), body = self.request(method="POST")
        self.assertTrue(status.startswith("405 "))
        self.assertIn(("Allow", "GET"), headers)

    def test_invalid_query_rejected_before_authentication(self):
        self.called.clear()
        for query in ("seller_id=a&seller_id=b", "unknown=value",
                      "seller_id=a&low_stock_threshold=abc"):
            (status, _), body = self.request(query=query)
            self.assertTrue(status.startswith("400 "))
            self.assertEqual(body, {"error": "invalid_query"})
        self.assertEqual(self.called, [])

    def test_other_route_is_not_exposed(self):
        (status, _), body = self.request(path="/api/other")
        self.assertTrue(status.startswith("404 "))
        self.assertEqual(body, {"error": "not_found"})


if __name__ == "__main__":
    unittest.main()
