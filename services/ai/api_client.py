#!/usr/bin/env python3
"""
Receipt OCR API Client Example
Easy way to test the API and integrate it into your app
"""

import requests
import json
import sys
from pathlib import Path


def upload_receipt(image_path: str, api_url: str = "http://localhost:8000") -> dict:
    """
    Upload a receipt image to the API and get extracted data
    
    Args:
        image_path: Path to receipt image file
        api_url: Base URL of the API (default: localhost:8000)
    
    Returns:
        Dictionary with extracted receipt data
    """
    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return None
    
    print(f"📤 Uploading {image_path}...")
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(
                f"{api_url}/receipt",
                files=files,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to API at {api_url}")
            print("   Make sure the server is running: python -m uvicorn receipt_api:app")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API error: {e}")
            return None


def check_health(api_url: str = "http://localhost:8000") -> bool:
    """Check if API server is running"""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def format_output(data: dict) -> None:
    """Pretty print receipt data"""
    if not data:
        return
    
    print("\n" + "="*70)
    print("  EXTRACTED RECEIPT DATA")
    print("="*70)
    
    # Items
    items = data.get("items", [])
    print(f"\n📦 Items ({len(items)} found):")
    print("-"*70)
    print(f"{'#':<3} {'Product':<40} {'Price':>12} {'Confidence':>10}")
    print("-"*70)
    for i, item in enumerate(items, 1):
        name = item.get("name", "")[:38]
        price = item.get("price", 0)
        conf = item.get("confidence", 0)
        print(f"{i:<3} {name:<40} ${price:>11.2f} {conf}x")
    
    # Discounts
    discounts = data.get("discounts", [])
    if discounts:
        print("\n🎟️  Discounts:")
        print("-"*70)
        for discount in discounts:
            name = discount.get("name", "")
            price = discount.get("price", 0)
            conf = discount.get("confidence", 0)
            print(f"  {name:<40} -${price:>10.2f} ({conf}x)")
    
    # Summary
    summary = data.get("summary", {})
    print("\n" + "="*70)
    print("  SUMMARY")
    print("="*70)
    print(f"Items found:  {summary.get('items_found', 0)}")
    print(f"Subtotal:     ${summary.get('subtotal', 0):.2f}")
    print(f"Savings:      ${summary.get('savings', 0):.2f}")
    print(f"Total:        ${summary.get('total', 0):.2f}")
    print("="*70 + "\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python api_client.py <receipt_image.jpg> [api_url]")
        print("\nExamples:")
        print("  python api_client.py receipt.jpg")
        print("  python api_client.py receipt.jpg http://localhost:8000")
        print("  python api_client.py receipt.jpg http://192.168.1.100:8000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print("\n" + "="*70)
    print("  Receipt OCR API Client")
    print("="*70 + "\n")
    
    # Check API health
    print(f"🔍 Checking API at {api_url}...")
    if not check_health(api_url):
        print(f"❌ API not responding at {api_url}")
        print("   Start the server with: python -m uvicorn receipt_api:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    print("✓ API is healthy\n")
    
    # Upload receipt
    result = upload_receipt(image_path, api_url)
    if result:
        print("✓ Receipt processed successfully\n")
        format_output(result)
        
        # Optionally save to file
        output_file = Path(image_path).stem + "_result.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"💾 Results saved to: {output_file}\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
