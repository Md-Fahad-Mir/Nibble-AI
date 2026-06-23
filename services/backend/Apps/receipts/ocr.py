"""OCR provider seam.

When an image is uploaded *and* ``settings.AI_SERVICE_URL`` is configured, this
calls the internal receipt-OCR microservice (``services/ai``: FastAPI + Tesseract)
and maps its response into the structured shape the rest of the app expects.

If no image is supplied, the service is unreachable, or it returns an error, we
fall back to the deterministic mock that simply echoes the already-structured
line items supplied with the upload (a "digital receipt") — which is exactly the
shape a real OCR call would return. This keeps receipt processing working (and
all tests green) regardless of the AI service's availability.
"""

import hashlib
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def run_ocr(*, image=None, merchant="", purchased_at=None, total=None, items=None) -> dict:
    items = items or []
    ai_url = (getattr(settings, "AI_SERVICE_URL", "") or "").strip()

    if image is not None and ai_url:
        ai_result = _run_ai_ocr(
            image=image, base_url=ai_url,
            merchant=merchant, purchased_at=purchased_at, total=total,
        )
        if ai_result is not None:
            return ai_result

    return _mock_ocr(merchant=merchant, purchased_at=purchased_at, total=total, items=items)


def _mock_ocr(*, merchant, purchased_at, total, items) -> dict:
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


def _run_ai_ocr(*, image, base_url, merchant, purchased_at, total):
    """POST the receipt image to the AI service; return mapped data or None.

    Returns None on any failure so the caller transparently falls back to the
    mock — the AI service must never be able to block a receipt upload.
    """
    try:
        import httpx  # provided transitively by the openai/anthropic SDKs
    except Exception:  # noqa: BLE001 - missing client => fall back
        logger.warning("httpx unavailable; using mock OCR.")
        return None

    data = _read_image_bytes(image)
    if not data:
        return None

    name = getattr(image, "name", "") or "receipt.jpg"
    timeout = getattr(settings, "AI_OCR_TIMEOUT", 30.0)
    try:
        resp = httpx.post(
            f"{base_url.rstrip('/')}/receipt",
            files={"file": (name, data, "application/octet-stream")},
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001 - any error => fall back to mock
        logger.warning("AI OCR call failed (%s); using mock OCR.", exc)
        return None

    return _map_ai_payload(payload, merchant=merchant, purchased_at=purchased_at, total=total)


def _map_ai_payload(payload, *, merchant, purchased_at, total) -> dict:
    """Map the AI service's {items, discounts, summary} into our OCR shape."""
    ai_items = payload.get("items") or []
    summary = payload.get("summary") or {}
    ai_total = summary.get("total")
    return {
        "provider": "ai-tesseract",
        "merchant": merchant,  # the Tesseract engine does not extract merchant
        "purchased_at": purchased_at.isoformat() if purchased_at else None,
        "total": (
            str(ai_total) if ai_total is not None
            else (str(total) if total is not None else None)
        ),
        "items": [
            {
                "description": it.get("name", ""),
                "quantity": 1,
                "unit_price": str(it["price"]) if it.get("price") is not None else None,
            }
            for it in ai_items
        ],
        "ai_raw": payload,
    }


def _read_image_bytes(image) -> bytes | None:
    try:
        if hasattr(image, "seek"):
            image.seek(0)
        if hasattr(image, "read"):
            data = image.read()
        elif hasattr(image, "chunks"):
            data = b"".join(image.chunks())
        else:
            return None
        if hasattr(image, "seek"):
            image.seek(0)
        return data or None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not read receipt image bytes (%s).", exc)
        return None


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
