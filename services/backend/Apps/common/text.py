"""Text helpers used for receipt matching and code generation."""

import re
import secrets

# Unambiguous alphabet for human-facing codes (no 0/O/1/I).
_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def normalize_text(value: str) -> str:
    """Lowercase, strip punctuation, and collapse whitespace.

    Used to compare product names / aliases against noisy OCR receipt text.
    Apostrophes are removed (not split) so "Driscoll's" matches a receipt's
    "DRISCOLLS"; other punctuation becomes a separator.
    """
    value = (value or "").lower().strip()
    value = value.replace("'", "").replace("’", "")  # straight + curly apostrophe
    value = re.sub(r"[^a-z0-9 ]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def random_code(length: int = 10) -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(length))
