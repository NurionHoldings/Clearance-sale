"""Offline session-to-dashboard authorization and tenant-scope tests."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_service import SellerAccessDenied
from backend.seller_dashboard_session_service import get_session_seller_dashboard
from backend.seller_inventory_scope import InventoryScopeError
from backend.seller_inventory_view import InventoryItem


class SellerDashboardSessionTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.principal = SellerPrincipal("user-1", True)
        self.membership = SellerMembership("user-1", "seller-A", "owner", "active")
        self.records = [("seller-A", InventoryItem("sku-1", "Sample", 10, 1, True))]

    def fetch(self, token="trusted-session", membership=None, records=None):
        def load_session(value):
            self.calls.append(("session", value))
            return self.principal
        def load_membership(user_id, seller_id):
            self.calls.append(("membership", user_id, seller_id))
            return self.membership if membership is None else membership
        def query_inventory(seller_id):
            self.calls.append(("inventory", seller_id))
            return self.records if records is None else records
        return get_session_seller_dashboard(
            session_token=token, seller_id="seller-A",
            load_session=load_session, load_membership=load_membership,
            query_inventory_by_seller=query_inventory,
        )

    def test_authorized_session_returns_read_only_dashboard(self):
        result = self.fetch()
        self.assertTrue(result["read_only"])
        self.assertEqual(result["visible_count"], 1)
        self.assertEqual(self.calls, [
            ("session", "trusted-session"),
            ("membership", "user-1", "seller-A"),
            ("inventory", "seller-A"),
        ])

    def test_missing_session_never_calls_loader(self):
        with self.assertRaises(SellerAccessDenied):
            self.fetch(token="")
        self.assertEqual(self.calls, [])

    def test_wrong_membership_does_not_query_inventory(self):
        wrong = SellerMembership("user-1", "seller-B", "owner", "active")
        with self.assertRaises(SellerAccessDenied):
            self.fetch(membership=wrong)
        self.assertEqual([call[0] for call in self.calls], ["session", "membership"])

    def test_cross_tenant_row_fails_entire_response(self):
        foreign = [("seller-B", InventoryItem("sku-2", "Foreign", 3, 0, True))]
        with self.assertRaises(InventoryScopeError):
            self.fetch(records=foreign)


if __name__ == "__main__":
    unittest.main()
