"""Read-side queries for receipts and the review queue."""

from Apps.receipts.models import ManualReviewItem, Receipt


def receipts_for_user(user):
    return Receipt.objects.filter(user=user).select_related("campaign", "brand")


def get_user_receipt(user, receipt_id) -> Receipt | None:
    return (
        Receipt.objects.filter(user=user, id=receipt_id)
        .prefetch_related("line_items")
        .first()
    )


def review_queue_for_brand(brand, *, status=ManualReviewItem.Status.OPEN):
    qs = ManualReviewItem.objects.filter(brand=brand).select_related(
        "receipt", "receipt__user"
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_brand_review_item(brand, item_id) -> ManualReviewItem | None:
    return (
        ManualReviewItem.objects.filter(brand=brand, id=item_id)
        .select_related("receipt")
        .first()
    )
