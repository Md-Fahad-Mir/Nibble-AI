from django.contrib import admin

from Apps.reviews.models import (
    Review,
    ReviewCampaign,
    ReviewModeration,
    ReviewPrompt,
    ReviewSession,
)


class ReviewPromptInline(admin.TabularInline):
    model = ReviewPrompt
    extra = 0


@admin.register(ReviewCampaign)
class ReviewCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "status", "daily_budget", "reward_amount", "auto_paused")
    list_filter = ("status",)
    search_fields = ("name", "brand__name")
    autocomplete_fields = ("brand",)
    filter_horizontal = ("products",)
    inlines = [ReviewPromptInline]


@admin.register(ReviewSession)
class ReviewSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "review_campaign", "status", "expires_at")
    list_filter = ("status",)
    search_fields = ("user__email", "product__name")


class ReviewModerationInline(admin.StackedInline):
    model = ReviewModeration
    extra = 0
    readonly_fields = ("auto_published", "held_until", "released_at")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "status", "published_at", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("product__name", "user__email")
    inlines = [ReviewModerationInline]
