from django.contrib import admin

from Apps.analytics.models import CampaignStat, PlatformStat, ProductStat


@admin.register(CampaignStat)
class CampaignStatAdmin(admin.ModelAdmin):
    list_display = ("campaign", "brand", "reservations", "redemptions", "total_spend", "computed_at")
    search_fields = ("brand__name",)


@admin.register(ProductStat)
class ProductStatAdmin(admin.ModelAdmin):
    list_display = ("product", "brand", "redemptions", "reviews_count", "average_rating", "computed_at")
    search_fields = ("brand__name", "product__name")


@admin.register(PlatformStat)
class PlatformStatAdmin(admin.ModelAdmin):
    list_display = ("date", "brands_total", "users_total", "redemptions_total", "total_reward_paid", "total_fees")
    ordering = ("-date",)
