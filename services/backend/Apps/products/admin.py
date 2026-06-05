from django.contrib import admin

from Apps.products.models import Product, ProductAlias, Tag


class ProductAliasInline(admin.TabularInline):
    model = ProductAlias
    extra = 0
    fields = ("alias_text", "normalized")
    readonly_fields = ("normalized",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "sku", "category", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name", "sku", "brand__name")
    autocomplete_fields = ("brand",)
    readonly_fields = ("normalized_name", "created_at", "updated_at")
    inlines = [ProductAliasInline]


@admin.register(ProductAlias)
class ProductAliasAdmin(admin.ModelAdmin):
    list_display = ("alias_text", "product", "brand", "normalized")
    search_fields = ("alias_text", "product__name", "brand__name")
    readonly_fields = ("normalized",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("code", "product", "brand", "label", "created_at")
    search_fields = ("code", "product__name", "brand__name")
    readonly_fields = ("code", "created_at", "updated_at")
