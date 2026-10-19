"""Offline tests for authorization-before-data-access invariant."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_service import (
    SellerAccessDenied, get_authorized_seller_dashboard,
)
from backend.seller_inventory_view import InventoryItem


class SellerDashboardServiceTests(unittest.TestCase):
    def setUp(self):
        self.principal = SellerPrincipal("user-1", True)
        self.membership = SellerMembership("user-1", "seller-A", "viewer", "active")
        self.calls = []

    def loader(self, seller_id):
        self.calls.append(seller_id)
        return [InventoryItem("A-101", "Demo", 10, 2)]

    def test_authorized_read_uses_verified_seller_scope(self):
        response = get_authorized_seller_dashboard(
            principal=self.principal, membership=self.membership,
            seller_id="seller-A", load_inventory=self.loader,
        )
        self.assertEqual(self.calls, ["seller-A"])
        self.assertTrue(response["read_only"])
        self.assertEqual(response["visible_count"], 1)
        self.assertEqual(response["products"][0]["available"], 8)

    def test_unauthorized_never_calls_loader(self):
        cases = [
            (SellerPrincipal("user-1", False), self.membership, "seller-A"),
            (self.principal, self.membership, "seller-B"),
            (SellerPrincipal("other", True), self.membership, "seller-A"),
            (self.principal, SellerMembership("user-1", "seller-A", "viewer", "inactive"), "seller-A"),
        ]
        for principal, membership, seller_id in cases:
            with self.subTest(principal=principal, seller_id=seller_id):
                with self.assertRaises(SellerAccessDenied):
                    get_authorized_seller_dashboard(
                        principal=principal, membership=membership,
                        seller_id=seller_id, load_inventory=self.loader,
                    )
        self.assertEqual(self.calls, [])

    def test_loader_missing_or_failure_does_not_fallback_to_demo(self):
        with self.assertRaises(TypeError):
            get_authorized_seller_dashboard(
                principal=self.principal, membership=self.membership,
                seller_id="seller-A", load_inventory=None,
            )
        def broken_loader(_seller_id):
            raise RuntimeError("DB unavailable")
        with self.assertRaises(RuntimeError):
            get_authorized_seller_dashboard(
                principal=self.principal, membership=self.membership,
                seller_id="seller-A", load_inventory=broken_loader,
            )


if __name__ == "__main__":
    unittest.main()
