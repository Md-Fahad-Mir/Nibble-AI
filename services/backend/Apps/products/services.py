"""Business logic for the product library."""

from __future__ import annotations

from django.db import IntegrityError

from Apps.common.text import normalize_text
from Apps.products.models import Product, ProductAlias, Tag


class ProductError(Exception):
    """Expected, user-facing product errors (mapped to HTTP 400)."""


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
def create_product(*, brand, name, **fields) -> Product:
    if Product.objects.filter(brand=brand, name=name).exists():
        raise ProductError("A product with this name already exists.")
    return Product.objects.create(brand=brand, name=name, **fields)


def update_product(product: Product, **fields) -> Product:
    new_name = fields.get("name")
    if new_name and new_name != product.name:
        if (
            Product.objects.filter(brand=product.brand, name=new_name)
            .exclude(pk=product.pk)
            .exists()
        ):
            raise ProductError("A product with this name already exists.")
    for key, value in fields.items():
        setattr(product, key, value)
    product.save()
    return product


def archive_product(product: Product) -> Product:
    """Soft-disable a product (kept for historical campaign/receipt references)."""
    product.is_active = False
    product.save(update_fields=["is_active", "updated_at"])
    return product


# ---------------------------------------------------------------------------
# Aliases
# ---------------------------------------------------------------------------
def add_alias(*, product: Product, alias_text: str) -> ProductAlias:
    normalized = normalize_text(alias_text)
    if not normalized:
        raise ProductError("Alias text cannot be empty.")
    if ProductAlias.objects.filter(brand=product.brand, normalized=normalized).exists():
        raise ProductError("That alias is already in use for this brand.")
    try:
        return ProductAlias.objects.create(
            product=product, brand=product.brand, alias_text=alias_text
        )
    except IntegrityError:
        raise ProductError("That alias is already in use for this brand.")


def remove_alias(alias: ProductAlias) -> None:
    alias.delete()


# ---------------------------------------------------------------------------
# Tag generator (pulls from the library — no manual upload)
# ---------------------------------------------------------------------------
def generate_tags(*, brand, product_ids=None) -> list[Tag]:
    """Create a tag for each requested product (or all active products).

    Idempotent per product: a product that already has a tag is reused rather
    than duplicated.
    """
    products = Product.objects.filter(brand=brand, is_active=True)
    if product_ids:
        products = products.filter(id__in=product_ids)

    tags: list[Tag] = []
    for product in products:
        tag = product.tags.first()
        if tag is None:
            tag = Tag.objects.create(brand=brand, product=product, label=product.name)
        tags.append(tag)
    return tags
