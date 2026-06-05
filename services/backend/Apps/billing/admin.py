from django.contrib import admin

from Apps.billing.models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "monthly_price",
        "rebate_fee_percent",
        "review_fee",
        "data_access_level",
        "customer_data_module",
        "is_active",
    )
    list_filter = ("is_active", "data_access_level", "customer_data_module")
    ordering = ("sort_order",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "brand",
        "plan",
        "status",
        "next_charge_at",
        "last_charged_at",
        "total_charged",
    )
    list_filter = ("status", "plan")
    search_fields = ("brand__name",)
    readonly_fields = ("last_charged_at", "total_charged", "created_at", "updated_at")
