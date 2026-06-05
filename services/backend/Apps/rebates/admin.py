from django.contrib import admin

from Apps.rebates.models import Redemption, RewardIssuance


class RewardIssuanceInline(admin.StackedInline):
    model = RewardIssuance
    extra = 0
    readonly_fields = (
        "brand_reward_entry",
        "customer_credit_entry",
        "brand_fee_entry",
        "hold",
        "reward_amount",
        "fee_amount",
    )
    can_delete = False


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "brand",
        "campaign",
        "reward_amount",
        "fee_amount",
        "status",
        "issued_at",
    )
    list_filter = ("status",)
    search_fields = ("user__email", "brand__name", "campaign__name")
    readonly_fields = ("issued_at", "created_at", "updated_at")
    inlines = [RewardIssuanceInline]
