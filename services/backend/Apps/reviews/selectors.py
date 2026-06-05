"""Read-side queries for the reviews module."""

from Apps.reviews.models import (
    Review,
    ReviewCampaign,
    ReviewSession,
)


def review_campaigns_for_brand(brand):
    return ReviewCampaign.objects.filter(brand=brand).prefetch_related("products")


def get_brand_review_campaign(brand, campaign_id) -> ReviewCampaign | None:
    return ReviewCampaign.objects.filter(brand=brand, id=campaign_id).first()


def active_sessions_for_user(user):
    return (
        ReviewSession.objects.filter(user=user, status=ReviewSession.Status.ACTIVE)
        .select_related("review_campaign", "product")
        .prefetch_related("review_campaign__prompts")
    )


def get_user_session(user, session_id) -> ReviewSession | None:
    return (
        ReviewSession.objects.filter(user=user, id=session_id)
        .select_related("review_campaign", "product")
        .prefetch_related("review_campaign__prompts")
        .first()
    )


def reviews_for_user(user):
    return Review.objects.filter(user=user).select_related("product", "review_campaign")


def reviews_for_brand(brand, *, status: str = ""):
    qs = Review.objects.filter(review_campaign__brand=brand).select_related(
        "product", "user", "review_campaign"
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_brand_review(brand, review_id) -> Review | None:
    return Review.objects.filter(
        review_campaign__brand=brand, id=review_id
    ).select_related("review_campaign").first()
