#!/usr/bin/env python3
"""
OFFLINE RECEIPT OCR  -  no API, no internet needed at runtime.

Engine : Tesseract (local)  +  OpenCV (local)
Method : auto-crop the receipt -> multi-pass OCR at several zoom levels
         (LANCZOS upscaling, gentle denoise) -> vote-based fuzzy de-dupe.

WHY THIS DESIGN
---------------
A phone photo of a small, wrinkled receipt is low-resolution, so any single
OCR pass misreads a few characters. Instead of one aggressive pass (which
destroys text), we ZOOM the cropped receipt several times with mild settings
and let the *agreement between passes* decide the result. A name/price that
shows up in many passes is trusted; one-off garbage is dropped. This reads the
LITERAL text on the paper and never invents items.

INSTALL (one time)
------------------
  Linux  : sudo apt install tesseract-ocr
  macOS  : brew install tesseract
  Windows: install from https://github.com/UB-Mannheim/tesseract/wiki
  Python : pip install pytesseract opencv-python numpy

RUN
---
  python offline_receipt_ocr.py  path/to/receipt.jpg
  (or run with no argument and it will ask for the path)
"""

import sys
import os
import re
import json
import csv
import difflib
from collections import Counter

try:
    import cv2
    import numpy as np
    import pytesseract
except ImportError as e:
    print(f"[ERROR] Missing library: {e.name}")
    print("Install with: pip install pytesseract opencv-python numpy")
    sys.exit(1)


# ----------------------------------------------------------------------
# 1. Find the receipt inside the photo (auto-crop)
#    Uses Tesseract's word boxes: the receipt is wherever the text clusters.
#    Works regardless of background colour, unlike colour thresholding.
# ----------------------------------------------------------------------
def auto_crop(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    big = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    data = pytesseract.image_to_data(big, config="--oem 3 --psm 11",
                                     output_type=pytesseract.Output.DICT)
    x1s, y1s, x2s, y2s = [], [], [], []
    for i, conf in enumerate(data["conf"]):
        try:
            conf = float(conf)
        except ValueError:
            continue
        if conf > 40 and len(data["text"][i].strip()) >= 2:
            x, y, w, h = (data["left"][i], data["top"][i],
                          data["width"][i], data["height"][i])
            x1s.append(x / 2); y1s.append(y / 2)
            x2s.append((x + w) / 2); y2s.append((y + h) / 2)

    if not x1s:
        return img  # nothing found, fall back to full frame

    x1 = int(np.percentile(x1s, 5));  y1 = int(np.percentile(y1s, 2))
    x2 = int(np.percentile(x2s, 95)); y2 = int(np.percentile(y2s, 98))
    m = 12
    H, W = img.shape[:2]
    return img[max(0, y1 - m):min(H, y2 + m), max(0, x1 - m):min(W, x2 + m)]


def enhance(crop, zoom, use_clahe):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    up = cv2.resize(gray, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LANCZOS4)
    up = cv2.bilateralFilter(up, 5, 50, 50)          # denoise, keep edges
    if use_clahe:
        up = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(up)
    return up


PRICE = re.compile(r"(\d{1,3})[.,](\d{2})\b")
CODE  = re.compile(r"^[^0-9]{0,4}(\d{3,12})")

def _clean_name(s):
    toks = [t for t in re.sub(r"[^A-Za-z '&]", " ", s).split() if len(t) > 1]
    return " ".join(toks).upper().strip()

def collect_votes(text, votes):
    for raw in text.splitlines():
        line = raw.strip()
        if len(line) < 6:
            continue
        prices = list(PRICE.finditer(line))
        code_m = CODE.match(line)
        if not prices or not code_m:
            continue
        last = prices[-1]
        price = float(f"{int(last.group(1))}.{last.group(2)}")
        if not (0 < price < 999):
            continue
        name = _clean_name(line[code_m.end():last.start()])
        if len(name) < 3:
            continue
        tail = line[last.end():]
        is_discount = ("/" in line[:last.start()]) or ("-" in tail[:3])
        votes[(is_discount, name, price)] += 1



def dedupe(votes, min_votes=2, similarity=0.7):
    items, discounts = [], []
    for (is_discount, name, price), n in sorted(votes.items(), key=lambda kv: -kv[1]):
        bucket = discounts if is_discount else items
        if any(difflib.SequenceMatcher(None, r["name"], name).ratio() > similarity
               for r in bucket):
            continue
        if n >= min_votes:
            bucket.append({"name": name, "price": price, "confidence": n})
    return items, discounts


def format_receipt_result(items, discounts):
    gross = sum(item["price"] for item in items)
    savings = sum(discount["price"] for discount in discounts)
    return {
        "items": [
            {"name": item["name"], "price": round(item["price"], 2), "confidence": item["confidence"]}
            for item in items
        ],
        "discounts": [
            {"name": discount["name"], "price": round(discount["price"], 2), "confidence": discount["confidence"]}
            for discount in discounts
        ],
        "summary": {
            "items_found": len(items),
            "subtotal": round(gross, 2),
            "savings": round(savings, 2),
            "total": round(gross - savings, 2),
        },
    }


ZOOMS = (4, 5, 6)
CLAHE_OPTS = (False, True)
PSMS = (6, 4)

def analyze(image_path, do_autocrop=True, manual_crop=None):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    if manual_crop:                      # (x, y, w, h)
        x, y, w, h = manual_crop
        crop = img[y:y + h, x:x + w]
    elif do_autocrop:
        crop = auto_crop(img)
    else:
        crop = img

    votes = Counter()
    for zoom in ZOOMS:
        for use_clahe in CLAHE_OPTS:
            for psm in PSMS:
                proc = enhance(crop, zoom, use_clahe)
                text = pytesseract.image_to_string(proc, config=f"--oem 3 --psm {psm}")
                collect_votes(text, votes)

    items, discounts = dedupe(votes)
    return items, discounts


# ----------------------------------------------------------------------
# 6. Output helpers
# ----------------------------------------------------------------------
def show(items, discounts):
    print("\n" + "=" * 56)
    print("  EXTRACTED ITEMS  (offline OCR)")
    print("=" * 56)
    print(f"{'#':<3}{'PRODUCT':<22}{'PRICE':>10}{'SEEN':>8}")
    print("-" * 56)
    for i, it in enumerate(items, 1):
        print(f"{i:<3}{it['name']:<22}{('$%.2f' % it['price']):>10}{(str(it['confidence'])+'x'):>8}")
    if discounts:
        print("-" * 56)
        print("  INSTANT SAVINGS")
        for d in discounts:
            print(f"   {d['name']:<22}{('-$%.2f' % d['price']):>10}")
    print("-" * 56)
    gross = sum(i["price"] for i in items)
    save = sum(d["price"] for d in discounts)
    print(f"   {'Items found':<22}{len(items):>10}")
    print(f"   {'Sum of items':<22}{('$%.2f' % gross):>10}")
    if save:
        print(f"   {'Less savings':<22}{('-$%.2f' % save):>10}")
        print(f"   {'Net':<22}{('$%.2f' % (gross - save)):>10}")
    print("=" * 56)
    print("Note: 'SEEN' = how many OCR passes agreed. Low numbers (2-3) are")
    print("worth a quick eyeball against the paper. Faint/garbled lines may")
    print("be missed entirely - that is a limit of the photo, not a guess.\n")


def save_outputs(items, discounts, base="receipt"):
    with open(base + ".json", "w") as f:
        json.dump({"items": items, "discounts": discounts}, f, indent=2)
    with open(base + ".csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["type", "name", "price", "confidence"])
        for it in items:
            w.writerow(["item", it["name"], it["price"], it["confidence"]])
        for d in discounts:
            w.writerow(["discount", d["name"], -d["price"], d["confidence"]])
    print(f"Saved: {base}.json  and  {base}.csv")


# ----------------------------------------------------------------------
def main():
    print("=" * 56)
    print("  OFFLINE RECEIPT OCR  (Tesseract - no API)")
    print("=" * 56)

    # confirm tesseract is actually installed
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        print("[ERROR] Tesseract engine not found.")
        print("  Linux : sudo apt install tesseract-ocr")
        print("  macOS : brew install tesseract")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        sys.exit(1)

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Receipt image path: ").strip().strip('"\'')

    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        sys.exit(1)

    print("\nReading (this runs several passes, ~10-20s on CPU)...")
    items, discounts = analyze(path)
    show(items, discounts)
    save_outputs(items, discounts)


if __name__ == "__main__":
    main()