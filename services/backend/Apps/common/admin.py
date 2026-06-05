from django.contrib import admin

from Apps.common.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor_type", "actor_id", "target_type", "target_id", "created_at")
    list_filter = ("action", "actor_type", "target_type")
    search_fields = ("actor_id", "target_id")
    readonly_fields = (
        "id",
        "actor_type",
        "actor_id",
        "action",
        "target_type",
        "target_id",
        "metadata",
        "ip_address",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        # Audit entries are written by the system, never created by hand.
        return False

    def has_change_permission(self, request, obj=None):
        return False
