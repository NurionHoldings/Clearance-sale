"""Offline tests for trusted seller identity resolution."""
import unittest

from backend.seller_access_policy import SellerMembership, SellerPrincipal
from backend.seller_identity_resolver import (
    SellerIdentityDenied, resolve_verified_product_access,
)


class SellerIdentityResolverTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.principal = SellerPrincipal("user-1", True)
        self.membership = SellerMembership("user-1", "seller-A", "owner", "active")

    def resolve(self, *, token="server-session", seller="seller-A", product="product-1",
                principal=None, membership=None, owner="seller-A", action="read"):
        def session_loader(value):
            self.calls.append(("session", value))
            return self.principal if principal is None else principal

        def membership_loader(user_id, seller_id):
            self.calls.append(("membership", user_id, seller_id))
            return self.membership if membership is None else membership

        def owner_loader(product_id):
            self.calls.append(("owner", product_id))
            return owner

        return resolve_verified_product_access(
            session_token=token, seller_id=seller, product_id=product,
            load_session=session_loader, load_membership=membership_loader,
            load_product_owner=owner_loader, action=action,
        )

    def test_verified_read_resolves_server_owned_identity(self):
        self.assertEqual(self.resolve(), (self.principal, self.membership, "seller-A"))
        self.assertEqual(self.calls, [
            ("session", "server-session"),
            ("membership", "user-1", "seller-A"),
            ("owner", "product-1"),
        ])

    def test_missing_session_denied_without_loading_any_data(self):
        with self.assertRaises(SellerIdentityDenied):
            self.resolve(token="")
        self.assertEqual(self.calls, [])

    def test_unauthenticated_session_stops_before_membership_lookup(self):
        with self.assertRaises(SellerIdentityDenied):
            self.resolve(principal=SellerPrincipal("user-1", False))
        self.assertEqual(self.calls, [("session", "server-session")])

    def test_cross_tenant_and_inactive_membership_denied(self):
        for owner, membership in (
            ("seller-B", self.membership),
            ("seller-A", SellerMembership("user-1", "seller-A", "owner", "suspended")),
            ("seller-A", SellerMembership("user-2", "seller-A", "owner", "active")),
        ):
            with self.subTest(owner=owner, membership=membership):
                with self.assertRaises(SellerIdentityDenied):
                    self.resolve(owner=owner, membership=membership)
                self.calls.clear()

    def test_inventory_write_remains_default_denied(self):
        with self.assertRaises(SellerIdentityDenied):
            self.resolve(action="inventory_write")


if __name__ == "__main__":
    unittest.main()
