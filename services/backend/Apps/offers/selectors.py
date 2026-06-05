"""Read-side queries for the consumer offer feed."""

from django.db.models import Q

from Apps.brands.models import Brand
from Apps.campaigns.models import Campaign
from Apps.offers.models import Bookmark


def active_offers(*, search: str = "", category: str = ""):
    """Active campaigns from operational brands, optionally filtered.

    'explore' (or empty) means all categories.
    """
    qs = (
        Campaign.objects.filter(
            status=Campaign.Status.ACTIVE, brand__status=Brand.Status.ACTIVE
        )
        .select_related("brand", "product", "restriction", "fallback_offer")
        .prefetch_related("tiers")
    )
    if category and category.lower() not in ("explore", "all"):
        qs = qs.filter(product__category__iexact=category)
    if search:
        qs = qs.filter(
            Q(name__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(product__name__icontains=search)
        )
    return qs.order_by("-created_at")


def bookmarks_for_user(user):
    return Bookmark.objects.filter(user=user).select_related("product", "brand")
