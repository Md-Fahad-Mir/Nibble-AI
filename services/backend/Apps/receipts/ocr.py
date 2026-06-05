"""OCR provider seam.

A real provider (Veryfi / Taggun / AWS Textract) would read ``receipt.image``
and return structured fields. Until that integration, this mock accepts the
already-structured line items supplied with the upload (a "digital receipt"),
which is exactly the shape a real OCR call would return.
"""

import hashlib


def run_ocr(*, image=None, merchant="", purchased_at=None, total=None, items=None) -> dict:
    items = items or []
    return {
        "provider": "mock",
        "merchant": merchant,
        "purchased_at": purchased_at.isoformat() if purchased_at else None,
        "total": str(total) if total is not None else None,
        "items": [
            {
                "description": i["description"],
                "quantity": int(i.get("quantity", 1)),
                "unit_price": str(i["unit_price"]) if i.get("unit_price") is not None else None,
            }
            for i in items
        ],
    }


def fingerprint(*, merchant, purchased_at, total, items, image=None) -> str:
    """Deterministic fingerprint for duplicate detection.

    Includes the image bytes when present; otherwise derives from the parsed
    merchant/date/total/line-items.
    """
    parts = [
        (merchant or "").strip().lower(),
        purchased_at.isoformat() if purchased_at else "",
        str(total) if total is not None else "",
    ]
    for item in sorted((items or []), key=lambda i: i["description"].lower()):
        parts.append(f"{item['description'].strip().lower()}x{int(item.get('quantity', 1))}")

    hasher = hashlib.sha256("|".join(parts).encode("utf-8"))

    if image is not None:
        try:
            for chunk in image.chunks():
                hasher.update(chunk)
            image.seek(0)
        except Exception:
            pass

    return hasher.hexdigest()
