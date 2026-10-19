"""Trusted server-side identity resolution for seller inventory access.

The injected loaders MUST read authenticated session identity, membership and
product ownership from server-side trusted sources. Browser-provided seller
roles, owner IDs or membership objects are never accepted as authority.
No HTTP endpoints, production credentials, or write permissions are enabled.
"""
from .seller_access_policy import (
    AccessDecision, SellerMembership, SellerPrincipal, can_access_product,
)


class SellerIdentityDenied(PermissionError):
    """Identity or seller ownership could not be verified."""


def resolve_verified_product_access(*, session_token, seller_id, product_id,
                                    load_session, load_membership,
                                    load_product_owner, action="read"):
    """Resolve identity first, then check server-owned membership and product."""
    if not isinstance(session_token, str) or not session_token.strip():
        raise SellerIdentityDenied("Missing authenticated session")
    if not isinstance(seller_id, str) or not seller_id.strip():
        raise SellerIdentityDenied("Missing seller identity")
    if not isinstance(product_id, str) or not product_id.strip():
        raise SellerIdentityDenied("Missing product identity")

    principal = load_session(session_token)
    if not isinstance(principal, SellerPrincipal) or not principal.authenticated:
        raise SellerIdentityDenied("Unauthenticated principal")
    if not isinstance(principal.user_id, str) or not principal.user_id.strip():
        raise SellerIdentityDenied("Invalid principal")

    membership = load_membership(principal.user_id, seller_id)
    if not isinstance(membership, SellerMembership):
        raise SellerIdentityDenied("Unverified seller membership")

    product_seller_id = load_product_owner(product_id)
    if can_access_product(
        principal, membership, seller_id=seller_id,
        product_seller_id=product_seller_id, action=action,
    ) is not AccessDecision.ALLOW:
        raise SellerIdentityDenied("Seller product access denied")
    return principal, membership, product_seller_id
