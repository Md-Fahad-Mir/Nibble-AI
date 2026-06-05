from django.contrib import admin

from Apps.offers.models import Bookmark, CooldownRecord, OfferView


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "product", "brand", "created_at")
    list_filter = ("kind",)
    search_fields = ("user__email",)


@admin.register(OfferView)
class OfferViewAdmin(admin.ModelAdmin):
    list_display = ("campaign", "user", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("campaign__name", "user__email")


@admin.register(CooldownRecord)
class CooldownRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "campaign", "started_at", "expires_at")
    search_fields = ("user__email", "campaign__name")
    readonly_fields = ("created_at", "updated_at")
