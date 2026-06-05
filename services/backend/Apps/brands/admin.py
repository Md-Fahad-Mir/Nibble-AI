from django.contrib import admin

from Apps.brands.models import Brand, BrandApplication, BrandMembership


class BrandMembershipInline(admin.TabularInline):
    model = BrandMembership
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "plan", "created_at")
    list_filter = ("status", "plan")
    search_fields = ("name", "slug", "contact_email")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BrandMembershipInline]


@admin.register(BrandMembership)
class BrandMembershipAdmin(admin.ModelAdmin):
    list_display = ("brand", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("brand__name", "user__email")
    autocomplete_fields = ("brand", "user")


@admin.register(BrandApplication)
class BrandApplicationAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "applicant", "status", "reviewed_by", "created_at")
    list_filter = ("status",)
    search_fields = ("brand_name", "applicant__email", "contact_email")
    readonly_fields = ("reviewed_by", "reviewed_at", "brand", "created_at", "updated_at")
