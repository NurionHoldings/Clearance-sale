"""Fail-closed inventory write service tests (no DB/network)."""
import unittest

from backend.inventory_idempotency_contract import InventoryCommand
from backend.inventory_write_service import (
    InventoryWriteDenied, execute_authorized_inventory_change,
)
from backend.seller_access_policy import SellerMembership, SellerPrincipal


class NoTouchTransaction:
    def __getattr__(self, name):
        raise AssertionError("Denied inventory write touched transaction: " + name)


class InventoryWriteServiceTests(unittest.TestCase):
    def setUp(self):
        self.command = InventoryCommand(
            "seller-A", "product-1", "request-1", 3, delta_reserved=1
        )
        self.principal = SellerPrincipal("user-1", True)
        self.membership = SellerMembership("user-1", "seller-A", "owner", "active")
        self.transaction = NoTouchTransaction()

    def test_even_owner_cannot_mutate_without_approved_write_policy(self):
        with self.assertRaises(InventoryWriteDenied):
            execute_authorized_inventory_change(
                self.command, principal=self.principal, membership=self.membership,
                product_seller_id="seller-A", transaction=self.transaction,
            )

    def test_cross_seller_product_and_unverified_user_are_denied(self):
        for principal, membership, product_owner in (
            (self.principal, self.membership, "seller-B"),
            (SellerPrincipal("user-1", False), self.membership, "seller-A"),
            (self.principal, SellerMembership("user-1", "seller-B", "owner", "active"), "seller-A"),
            (self.principal, SellerMembership("user-1", "seller-A", "owner", "suspended"), "seller-A"),
        ):
            with self.subTest(product_owner=product_owner, membership=membership):
                with self.assertRaises(InventoryWriteDenied):
                    execute_authorized_inventory_change(
                        self.command, principal=principal, membership=membership,
                        product_seller_id=product_owner, transaction=self.transaction,
                    )

    def test_invalid_command_denied_before_transaction_access(self):
        with self.assertRaises(InventoryWriteDenied):
            execute_authorized_inventory_change(
                None, principal=self.principal, membership=self.membership,
                product_seller_id="seller-A", transaction=self.transaction,
            )


if __name__ == "__main__":
    unittest.main()
