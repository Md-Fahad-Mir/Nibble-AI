from django.contrib import admin

from Apps.payouts.models import PayoutBatch, PayoutMethod, WithdrawalRequest


@admin.register(PayoutMethod)
class PayoutMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "handle", "is_default", "created_at")
    list_filter = ("provider", "is_default")
    search_fields = ("user__email", "handle")


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "provider", "amount", "status", "batch", "created_at")
    list_filter = ("status", "provider")
    search_fields = ("user__email", "handle")
    readonly_fields = ("hold", "reviewed_by", "reviewed_at", "paid_at", "created_at", "updated_at")


@admin.register(PayoutBatch)
class PayoutBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "total_amount", "created_by", "exported_at", "created_at")
    list_filter = ("status",)
    readonly_fields = ("total_amount", "exported_at", "created_at", "updated_at")
