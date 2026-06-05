from django.contrib import admin

from Apps.campaigns.models import (
    Campaign,
    CampaignURL,
    FallbackOffer,
    QRCode,
    Restriction,
    RewardTier,
)


class RewardTierInline(admin.TabularInline):
    model = RewardTier
    extra = 0


class RestrictionInline(admin.StackedInline):
    model = Restriction
    extra = 0
    readonly_fields = ("restriction_type", "min_units", "description")
    can_delete = False


class FallbackOfferInline(admin.StackedInline):
    model = FallbackOffer
    extra = 0


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "product", "status", "daily_budget", "auto_paused", "created_at")
    list_filter = ("status", "is_bogo")
    search_fields = ("name", "brand__name", "product__name")
    autocomplete_fields = ("brand", "product")
    inlines = [RewardTierInline, RestrictionInline, FallbackOfferInline]


@admin.register(CampaignURL)
class CampaignURLAdmin(admin.ModelAdmin):
    list_display = ("campaign", "token")
    readonly_fields = ("token",)


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("campaign", "token")
    readonly_fields = ("token",)
