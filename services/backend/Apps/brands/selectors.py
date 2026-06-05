"""Read-side queries enforcing brand tenancy."""

from Apps.brands.models import Brand, BrandMembership


def brands_for_user(user):
    """Brands the user is an active member of."""
    return Brand.objects.filter(
        memberships__user=user, memberships__is_active=True
    ).distinct()


def get_active_membership(user, brand) -> BrandMembership | None:
    return BrandMembership.objects.filter(
        user=user, brand=brand, is_active=True
    ).first()


def is_member(user, brand) -> bool:
    return get_active_membership(user, brand) is not None
