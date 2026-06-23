"""
FIXED RECEIPT OCR ANALYZER
Corrected OpenCV parameters and robust error handling
"""

import os
import json
import base64
import cv2
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI()


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def aggressive_preprocess(image_path, output_path="receipt_enhanced.jpg"):
    """
    Fixed preprocessing with corrected OpenCV parameters
    """
    print("\n" + "="*70)
    print("[PREPROCESS] AGGRESSIVE ENHANCEMENT")
    print("="*70 + "\n")
    
    try:
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        print(f"[1] Original size: {w}×{h}")
        
        # UPSCALE 3x
        img = cv2.resize(img, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        h, w = img.shape[:2]
        print(f"[2] ✓ Upscaled 3.0× → {w}×{h}")
        
        # DENOISE (FIXED: removed hForColorComponents parameter)
        try:
            img = cv2.fastNlMeansDenoisingColored(
                img, 
                None, 
                h=15,
                templateWindowSize=7, 
                searchWindowSize=21
            )
            print(f"[3] ✓ Denoising applied")
        except Exception as e:
            print(f"[3] ⚠️  Denoising skipped: {str(e)[:50]}")
        
        # CONTRAST ENHANCEMENT
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        l = clahe.apply(l)
        
        # Histogram equalization
        l = cv2.equalizeHist(l)
        
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        print(f"[4] ✓ Contrast enhancement (CLAHE + HE)")
        
        # SHARPENING
        kernel = np.array([
            [-2, -1, 0],
            [-1,  1, 1],
            [ 0,  1, 2]
        ]) * 2
        img = cv2.filter2D(img, -1, kernel)
        print(f"[5] ✓ Sharpening applied")
        
        # BILATERAL FILTERING
        img = cv2.bilateralFilter(img, 9, 75, 75)
        print(f"[6] ✓ Bilateral filtering")
        
        # BINARIZATION
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(
            gray, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 
            21, 10
        )
        img = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        print(f"[7] ✓ Adaptive binarization")
        
        # SAVE
        success = cv2.imwrite(output_path, img)
        if success:
            print(f"\n[✓] Enhanced image saved: {output_path}")
            print(f"[✓] Final size: {img.shape[1]}×{img.shape[0]}\n")
            return output_path
        else:
            print(f"[ERROR] Failed to save image\n")
            return image_path
        
    except Exception as e:
        print(f"\n[ERROR] Preprocessing failed: {e}\n")
        return image_path


def analyze_receipt(image_path):
    """Analyze receipt with OCR"""
    
    print("="*70)
    print("[ANALYZE] RECEIPT OCR")
    print("="*70 + "\n")
    
    # Preprocess
    processed_path = aggressive_preprocess(image_path)
    
    # Encode
    base64_image = encode_image(processed_path)
    ext = os.path.splitext(processed_path.lower())[1]
    mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    
    prompt = """
You are an expert OCR specialist. Extract ALL items from this receipt.

Return ONLY valid JSON:
{
  "store": "store name",
  "date": "date",
  "time": "time",
  "items": [
    {
      "line": 1,
      "name": "product name",
      "qty": "quantity",
      "price": "unit price",
      "total": "line total"
    }
  ],
  "subtotal": "amount",
  "tax": "amount",
  "total": "final total",
  "payment": "payment method",
  "confidence": "high/medium/low",
  "items_found": 0
}
"""
    
    try:
        print("[API] Sending to OpenAI...\n")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            temperature=0.02,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }],
            max_tokens=2500
        )
        
        # Parse response
        response_text = response.choices[0].message.content
        print(f"[API] Raw response:\n{response_text[:500]}\n")
        
        data = json.loads(response_text)
        
        # Display
        display_results(data)
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipt_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Saved: {filename}\n")
        
        return data
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        print(f"Response was: {response_text[:200]}\n")
        return None
    except Exception as e:
        print(f"[ERROR] API call failed: {e}\n")
        return None


def display_results(data):
    """Display extracted data"""
    
    print("="*70)
    print("[RESULTS] EXTRACTED RECEIPT")
    print("="*70 + "\n")
    
    print(f"🏪 Store: {data.get('store', 'N/A')}")
    print(f"📅 Date: {data.get('date', 'N/A')}")
    print(f"🕐 Time: {data.get('time', 'N/A')}\n")
    
    print("-"*70)
    print(f"{'Line':<5} {'Product':<40} {'Qty':<6} {'Price':<10} {'Total':<10}")
    print("-"*70)
    
    items = data.get("items", [])
    for item in items:
        name = str(item.get("name", ""))[:38]
        qty = str(item.get("qty", "1"))
        price = str(item.get("price", "N/A"))
        total = str(item.get("total", "N/A"))
        print(f"{item.get('line', ''):<5} {name:<40} {qty:<6} ${price:<9} ${total:<9}")
    
    print("\n" + "-"*70)
    print(f"Subtotal: ${data.get('subtotal', 'N/A')}")
    print(f"Tax:      ${data.get('tax', 'N/A')}")
    print(f"TOTAL:    ${data.get('total', 'N/A')}")
    print(f"Payment:  {data.get('payment', 'N/A')}")
    print(f"Confidence: {data.get('confidence', 'N/A').upper()}")
    print(f"Items Found: {data.get('items_found', len(items))}")
    print("\n" + "="*70 + "\n")


def main():
    print("\n" + "="*70)
    print("     RECEIPT OCR ANALYZER (FIXED)")
    print("="*70 + "\n")
    
    image_path = input("Enter image path: ").strip().strip("\"'")
    
    if not os.path.exists(image_path):
        print(f"❌ File not found: {image_path}\n")
        return
    
    analyze_receipt(image_path)


if __name__ == "__main__":
    main()