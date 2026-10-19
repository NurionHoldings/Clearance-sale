"""Pure inventory quantity rules. No persistence, orders, payments, or network I/O."""

def available_quantity(on_hand: int, reserved: int) -> int:
    if type(on_hand) is not int or type(reserved) is not int:
        raise TypeError("Inventory quantities must be integers")
    if on_hand < 0 or reserved < 0 or reserved > on_hand:
        raise ValueError("Invalid inventory state")
    return on_hand - reserved


def reserve(on_hand: int, reserved: int, requested: int) -> int:
    available = available_quantity(on_hand, reserved)
    if type(requested) is not int or requested <= 0:
        raise ValueError("Requested quantity must be a positive integer")
    if requested > available:
        raise ValueError("Insufficient available inventory")
    return reserved + requested


def release(on_hand: int, reserved: int, quantity: int) -> int:
    available_quantity(on_hand, reserved)
    if type(quantity) is not int or quantity <= 0 or quantity > reserved:
        raise ValueError("Invalid release quantity")
    return reserved - quantity
