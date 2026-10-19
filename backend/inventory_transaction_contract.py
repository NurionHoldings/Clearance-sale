"""Transaction protocol for future inventory persistence adapters (no DB calls).

Required transaction order:
1. Authenticate/authorize seller outside this adapter.
2. Begin transaction and lock idempotency scope (seller_id, key).
3. If committed key exists, compare fingerprint and replay committed result.
4. Otherwise load the product balance scoped to seller_id, plan CAS update.
5. Require exactly one updated row, insert idempotency result in SAME transaction.
6. Commit both together; on any error roll back. Handle concurrent unique-key
   conflicts by re-reading committed record and comparing fingerprint.

Never commit inventory first and idempotency receipt later.
"""

from dataclasses import dataclass

from .inventory_concurrency_contract import (
    InventoryVersion, InventoryConflict, require_compare_and_swap_result,
)
from .inventory_idempotency_contract import (
    InventoryCommand, IdempotencyConflict, plan_idempotent_inventory_command,
)


@dataclass(frozen=True)
class StoredCommandReceipt:
    fingerprint: str
    result: InventoryVersion


def plan_transaction(command, *, current, receipt=None):
    """Pure plan; persistence adapter must execute under transactional locking."""
    if not isinstance(command, InventoryCommand):
        raise ValueError("Invalid command")
    if receipt is not None:
        if not isinstance(receipt, StoredCommandReceipt):
            raise IdempotencyConflict("Malformed stored receipt")
        return plan_idempotent_inventory_command(
            command, current=None, prior_fingerprint=receipt.fingerprint,
            prior_result=receipt.result,
        )
    return plan_idempotent_inventory_command(command, current=current)


def validate_transaction_write(plan, *, affected_rows):
    """Only a newly planned write may claim a successful CAS update."""
    if not isinstance(plan, dict) or plan.get("replayed") is not False:
        raise InventoryConflict("Only a new command may write inventory")
    if not isinstance(plan.get("next_state"), InventoryVersion):
        raise InventoryConflict("Missing planned inventory result")
    require_compare_and_swap_result(affected_rows)
    return StoredCommandReceipt(
        fingerprint=plan["fingerprint"], result=plan["next_state"]
    )
