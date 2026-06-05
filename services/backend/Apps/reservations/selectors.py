"""Read-side queries for reservations."""

from Apps.reservations.models import Reservation


def reservations_for_user(user, *, status: str = ""):
    qs = Reservation.objects.filter(user=user).select_related(
        "campaign", "campaign__brand", "campaign__product"
    )
    if status:
        qs = qs.filter(status=status)
    return qs


def get_user_reservation(user, reservation_id) -> Reservation | None:
    return (
        Reservation.objects.filter(user=user, id=reservation_id)
        .select_related("campaign", "campaign__brand", "campaign__product")
        .first()
    )
