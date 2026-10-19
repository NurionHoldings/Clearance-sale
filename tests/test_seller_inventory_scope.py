"""Offline tenant-isolation tests; no database credentials or service."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_dashboard_service import get_authorized_seller_dashboard, SellerAccessDenied
from backend.seller_inventory_scope import (
    InventoryScopeError, scoped_inventory_loader, verify_scoped_inventory,
)
from backend.seller_inventory_view import InventoryItem


class SellerInventoryScopeTests(unittest.TestCase):
    def setUp(self):
        self.a = InventoryItem("A-1", "Seller A product", 7, 2)
        self.b = InventoryItem("B-1", "Seller B product", 5, 0)
        self.principal = SellerPrincipal("u1", True)
        self.membership = SellerMembership("u1", "seller-A", "viewer", "active")

    def test_matching_scope_and_empty_scope(self):
        self.assertEqual(verify_scoped_inventory("seller-A", [("seller-A", self.a)]), [self.a])
        self.assertEqual(verify_scoped_inventory("seller-A", []), [])

    def test_cross_tenant_row_fails_entire_result(self):
        for rows in [
            [("seller-A", self.a), ("seller-B", self.b)],
            [("seller-B", self.b)],
            [("seller-A", self.a), ("seller-A", "invalid")],
            [("seller-A", self.a), ("", self.b)],
        ]:
            with self.subTest(rows=rows), self.assertRaises(InventoryScopeError):
                verify_scoped_inventory("seller-A", rows)

    def test_malformed_scope_or_collection_denied(self):
        for seller_id, records in [
            ("", []), (None, []), ("seller-A", None),
            ("seller-A", [self.a]), ("seller-A", [("seller-A",)]),
        ]:
            with self.subTest(seller_id=seller_id, records=records):
                with self.assertRaises(InventoryScopeError):
                    verify_scoped_inventory(seller_id, records)

    def test_authorized_service_rejects_leaked_query_result(self):
        called = []
        def query(seller_id):
            called.append(seller_id)
            return [("seller-A", self.a), ("seller-B", self.b)]
        with self.assertRaises(InventoryScopeError):
            get_authorized_seller_dashboard(
                principal=self.principal, membership=self.membership,
                seller_id="seller-A", load_inventory=scoped_inventory_loader(query),
            )
        self.assertEqual(called, ["seller-A"])

    def test_unauthorized_request_never_queries_database_adapter(self):
        called = []
        loader = scoped_inventory_loader(lambda seller_id: called.append(seller_id) or [])
        with self.assertRaises(SellerAccessDenied):
            get_authorized_seller_dashboard(
                principal=self.principal, membership=self.membership,
                seller_id="seller-B", load_inventory=loader,
            )
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main()
