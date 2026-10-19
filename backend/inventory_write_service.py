"""Default-deny authorization boundary for inventory mutations.

No production writes are enabled by this module. The principal, membership,
and product ownership MUST be loaded from trusted server-side sources.
"""
from .inventory_idempotency_contract import InventoryCommand
from .seller_access_policy import AccessDecision, can_access_product


class InventoryWriteDenied(PermissionError):
    """An inventory mutation is not authorized."""


def execute_authorized_inventory_change(command, *, principal, membership,
                                        product_seller_id, transaction):
    """Require a trusted write policy before touching a transaction adapter.

    The current seller policy intentionally does not grant inventory_write to
    any role. This boundary therefore fails closed until a separately reviewed
    policy and authenticated HTTP integration explicitly enable writes.
    """
    if not isinstance(command, InventoryCommand):
        raise InventoryWriteDenied("Invalid inventory command")
    if can_access_product(
        principal, membership, seller_id=command.seller_id,
        product_seller_id=product_seller_id, action="inventory_write",
    ) is not AccessDecision.ALLOW:
        raise InventoryWriteDenied("Inventory write access denied")
    from .inventory_transaction_adapter import execute_inventory_transaction
    return execute_inventory_transaction(command, transaction=transaction)
