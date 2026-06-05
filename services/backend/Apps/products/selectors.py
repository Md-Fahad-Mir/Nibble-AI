"""Read-side queries for the product library (all brand-scoped)."""

from Apps.common.text import normalize_text
from Apps.products.models import Product, ProductAlias


def products_for_brand(brand):
    return Product.objects.filter(brand=brand)


def get_brand_product(brand, product_id) -> Product | None:
    return Product.objects.filter(brand=brand, id=product_id).first()


def match_product(*, brand, text: str) -> Product | None:
    """Resolve receipt text to one of the brand's active products.

    Looks at aliases first (indexed), then the product's normalized name.
    Returns None on no match — callers (M8) treat this as "needs review".
    """
    norm = normalize_text(text)
    if not norm:
        return None

    alias = (
        ProductAlias.objects.filter(
            brand=brand, normalized=norm, product__is_active=True
        )
        .select_related("product")
        .first()
    )
    if alias is not None:
        return alias.product

    return Product.objects.filter(
        brand=brand, is_active=True, normalized_name=norm
    ).first()
