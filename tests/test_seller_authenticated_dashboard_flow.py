"""Offline integration checks for seller dashboard session wiring."""
from datetime import datetime, timezone
import unittest
from backend.seller_access_policy import SellerMembership
from backend.seller_authenticated_dashboard_flow import authenticated_dashboard_flow
from backend.seller_inventory_view import InventoryItem
from backend.seller_session_lifecycle import issue_session


class SellerDashboardFlowTests(unittest.TestCase):
    def test_verified_session_scopes_inventory(self):
        token, record = issue_session(user_id="user-1", now=datetime.now(timezone.utc))
        class Store:
            def load_session_record(self, value):
                return record if value == token else None
            def load_membership(self, user, seller):
                return SellerMembership(user, seller, "viewer", "active")
        calls = []
        def inventory(seller):
            calls.append(seller)
            return [(seller, InventoryItem("sku-1", "Sample", 3, 0, True))]
        args = dict(auth_store=Store(), seller_id="seller-A",
                    query_inventory_by_seller=inventory)
        code, body = authenticated_dashboard_flow(
            **args, cookie_header="__Host-seller_session=" + token)
        self.assertEqual(code, 200)
        self.assertTrue(body["read_only"])
        self.assertEqual(calls, ["seller-A"])
        code, _ = authenticated_dashboard_flow(**args, cookie_header="")
        self.assertEqual(code, 403)
        self.assertEqual(calls, ["seller-A"])


    def test_wrong_seller_is_denied(self):
        token, record = issue_session(user_id="user-1", now=datetime.now(timezone.utc))
        class Store:
            def load_session_record(self, value):
                return record if value == token else None
            def load_membership(self, user, seller):
                return SellerMembership(user, "seller-B", "viewer", "active")
        calls = []
        code, _ = authenticated_dashboard_flow(
            auth_store=Store(), seller_id="seller-A",
            cookie_header="__Host-seller_session=" + token,
            query_inventory_by_seller=lambda seller: calls.append(seller) or [])
        self.assertEqual(code, 403)
        self.assertEqual(calls, [])

    def test_revoked_session_is_denied(self):
        from dataclasses import replace
        token, record = issue_session(user_id="user-1", now=datetime.now(timezone.utc))
        record = replace(record, revoked_at=datetime.now(timezone.utc))
        class Store:
            def load_session_record(self, value):
                return record if value == token else None
            def load_membership(self, user, seller):
                raise AssertionError("Membership must not be read")
        code, _ = authenticated_dashboard_flow(
            auth_store=Store(), seller_id="seller-A",
            cookie_header="__Host-seller_session=" + token,
            query_inventory_by_seller=lambda seller: self.fail("Inventory must not be read"))
        self.assertEqual(code, 403)

if __name__ == "__main__":
    unittest.main()
