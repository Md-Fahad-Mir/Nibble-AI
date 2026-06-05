from django.contrib import admin

from Apps.reservations.models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "campaign",
        "kind",
        "offer_type",
        "reward_amount",
        "status",
        "expires_at",
        "created_at",
    )
    list_filter = ("kind", "offer_type", "status")
    search_fields = ("user__email", "campaign__name")
    readonly_fields = (
        "hold",
        "redeemed_at",
        "expired_at",
        "cancelled_at",
        "created_at",
        "updated_at",
    )
