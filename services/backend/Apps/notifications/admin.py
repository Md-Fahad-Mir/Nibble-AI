from django.contrib import admin

from Apps.notifications.models import (
    DeviceToken,
    Notification,
    NotificationPreference,
    NotificationTemplate,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("type", "title", "is_active")
    list_filter = ("is_active",)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "platform", "is_active", "last_seen")
    list_filter = ("platform", "is_active")
    search_fields = ("user__email", "token")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "push_enabled", "promotional", "new_offers")
    search_fields = ("user__email",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("type", "user", "status", "read_at", "created_at")
    list_filter = ("type", "status")
    search_fields = ("user__email", "title")
    readonly_fields = ("sent_at", "created_at", "updated_at")
