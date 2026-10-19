"""Offline authorization contract tests: no external service required."""
import unittest

from backend.seller_access_policy import (
    AccessDecision, SellerMembership, SellerPrincipal,
    can_access_product, can_access_seller_inventory,
)


class SellerAccessPolicyTests(unittest.TestCase):
    def setUp(self):
        self.principal = SellerPrincipal(user_id="user-1", authenticated=True)
        self.owner = SellerMembership(
            user_id="user-1", seller_id="seller-A", role="owner", status="active"
        )

    def test_owner_can_read_and_preview_but_not_mutate(self):
        for action in ("read", "draft_preview"):
            self.assertEqual(
                can_access_seller_inventory(self.principal, self.owner,
                                            seller_id="seller-A", action=action),
                AccessDecision.ALLOW,
            )
        for action in ("write", "delete", "reserve", "export"):
            self.assertEqual(
                can_access_seller_inventory(self.principal, self.owner,
                                            seller_id="seller-A", action=action),
                AccessDecision.DENY,
            )

    def test_cross_tenant_and_product_owner_mismatch_denied(self):
        self.assertEqual(
            can_access_seller_inventory(self.principal, self.owner, seller_id="seller-B"),
            AccessDecision.DENY,
        )
        self.assertEqual(
            can_access_product(self.principal, self.owner, seller_id="seller-A",
                               product_seller_id="seller-B"),
            AccessDecision.DENY,
        )

    def test_inactive_wrong_user_and_unauthenticated_denied(self):
        cases = [
            (SellerPrincipal("user-1", False), self.owner),
            (SellerPrincipal("user-2", True), self.owner),
            (self.principal, SellerMembership("user-1", "seller-A", "owner", "suspended")),
            (self.principal, SellerMembership("user-1", "seller-A", "unknown", "active")),
        ]
        for principal, membership in cases:
            with self.subTest(principal=principal, membership=membership):
                self.assertEqual(
                    can_access_seller_inventory(principal, membership, seller_id="seller-A"),
                    AccessDecision.DENY,
                )

    def test_malformed_principal_identity_is_denied_without_exception(self):
        for identity in (None, 123, [], {}, ""):
            with self.subTest(identity=identity):
                principal = SellerPrincipal(identity, True)
                self.assertEqual(
                    can_access_seller_inventory(principal, self.owner, seller_id="seller-A"),
                    AccessDecision.DENY,
                )

    def test_malformed_role_and_action_are_denied(self):
        for role in ([], {}, None):
            membership = SellerMembership("user-1", "seller-A", role, "active")
            self.assertEqual(
                can_access_seller_inventory(self.principal, membership, seller_id="seller-A"),
                AccessDecision.DENY,
            )
        for action in ([], {}, None):
            self.assertEqual(
                can_access_seller_inventory(self.principal, self.owner, seller_id="seller-A", action=action),
                AccessDecision.DENY,
            )

    def test_viewer_read_only_and_bad_inputs(self):
        viewer = SellerMembership("user-1", "seller-A", "viewer", "active")
        self.assertEqual(
            can_access_seller_inventory(self.principal, viewer, seller_id="seller-A"),
            AccessDecision.ALLOW,
        )
        self.assertEqual(
            can_access_seller_inventory(self.principal, viewer,
                                        seller_id="seller-A", action="draft_preview"),
            AccessDecision.DENY,
        )
        for principal, membership, seller_id in [
            (None, self.owner, "seller-A"),
            (self.principal, None, "seller-A"),
            (self.principal, self.owner, ""),
        ]:
            self.assertEqual(
                can_access_seller_inventory(principal, membership, seller_id=seller_id),
                AccessDecision.DENY,
            )


if __name__ == "__main__":
    unittest.main()
