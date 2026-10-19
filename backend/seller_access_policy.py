"""Pure seller access checks; no session, database, or HTTP integration.

The caller MUST authenticate the principal and load membership/product ownership
from trusted server-side sources. Never pass browser-supplied ownership here.
"""
from dataclasses import dataclass
from enum import Enum


class AccessDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class SellerPrincipal:
    user_id: str
    authenticated: bool


@dataclass(frozen=True)
class SellerMembership:
    user_id: str
    seller_id: str
    role: str
    status: str


def can_access_seller_inventory(principal, membership, *, seller_id, action="read"):
    """Default-deny: evaluate server-verified seller membership for an action."""
    if not isinstance(principal, SellerPrincipal) or not isinstance(membership, SellerMembership):
        return AccessDecision.DENY
    if not isinstance(seller_id, str) or not seller_id.strip():
        return AccessDecision.DENY
    if not principal.authenticated or not principal.user_id.strip():
        return AccessDecision.DENY
    if membership.user_id != principal.user_id or membership.seller_id != seller_id:
        return AccessDecision.DENY
    if membership.status != "active":
        return AccessDecision.DENY
    allowed = {
        "viewer": frozenset({"read"}),
        "manager": frozenset({"read", "draft_preview"}),
        "owner": frozenset({"read", "draft_preview"}),
    }
    return (
        AccessDecision.ALLOW
        if action in allowed.get(membership.role, frozenset())
        else AccessDecision.DENY
    )


def can_access_product(principal, membership, *, seller_id, product_seller_id, action="read"):
    """Require both valid seller membership and matching trusted product owner."""
    if not isinstance(product_seller_id, str) or product_seller_id != seller_id:
        return AccessDecision.DENY
    return can_access_seller_inventory(
        principal, membership, seller_id=seller_id, action=action
    )
