"""Offline idempotent inventory command contract tests."""
import unittest

from backend.inventory_concurrency_contract import InventoryConflict, InventoryVersion
from backend.inventory_idempotency_contract import (
    IdempotencyConflict, InventoryCommand, fingerprint_inventory_command,
    plan_idempotent_inventory_command,
)


class InventoryIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.command = InventoryCommand(
            "seller-A", "product-1", "request-1", 3, delta_reserved=2
        )
        self.current = InventoryVersion("product-1", 10, 1, 3)

    def test_new_command_and_identical_retry(self):
        planned = plan_idempotent_inventory_command(self.command, current=self.current)
        self.assertFalse(planned["replayed"])
        self.assertEqual(planned["next_state"], InventoryVersion("product-1", 10, 3, 4))
        retry = plan_idempotent_inventory_command(
            self.command, current=None, prior_fingerprint=planned["fingerprint"],
            prior_result=planned["next_state"],
        )
        self.assertTrue(retry["replayed"])
        self.assertEqual(retry["next_state"], planned["next_state"])

    def test_reused_key_with_different_request_is_rejected(self):
        original = plan_idempotent_inventory_command(self.command, current=self.current)
        changed = InventoryCommand("seller-A", "product-1", "request-1", 3, delta_reserved=3)
        with self.assertRaises(IdempotencyConflict):
            plan_idempotent_inventory_command(
                changed, current=self.current,
                prior_fingerprint=original["fingerprint"],
                prior_result=original["next_state"],
            )

    def test_product_mismatch_and_incomplete_replay_denied(self):
        with self.assertRaises(InventoryConflict):
            plan_idempotent_inventory_command(
                self.command, current=InventoryVersion("other", 10, 1, 3)
            )
        with self.assertRaises(IdempotencyConflict):
            plan_idempotent_inventory_command(
                self.command, current=None,
                prior_fingerprint=fingerprint_inventory_command(self.command),
                prior_result=None,
            )

    def test_bad_identities_and_quantities_fail_closed(self):
        for command in [
            InventoryCommand("", "product-1", "key", 3),
            InventoryCommand("seller-A", "product-1", "", 3),
            InventoryCommand("seller-A", "product-1", "key", True),
            InventoryCommand("seller-A", "product-1", "key", -1),
        ]:
            with self.subTest(command=command), self.assertRaises(ValueError):
                fingerprint_inventory_command(command)


if __name__ == "__main__":
    unittest.main()
