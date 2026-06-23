# Receipt OCR API - Complete Setup & Usage Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /mnt/f/Office/Rela
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
cd /mnt/f/Office/Rela
python -m uvicorn receipt_api:app --host 0.0.0.0 --port 8000
```

Server will run at: `http://0.0.0.0:8000`

---

## 📡 API Endpoints

### Root Info
- **GET** `/` — API information and endpoints

### Health Check
- **GET** `/health` — Check if server is running

### Parse Receipt (Main Endpoint)
- **POST** `/receipt` — Upload receipt image and extract data
  - **Parameter**: `file` (multipart/form-data) — Receipt image file (.jpg, .png)
  - **Optional**: `do_autocrop` (boolean, default: true) — Auto-crop receipt area
  - **Returns**: JSON with extracted items, discounts, and totals

### API Documentation
- **GET** `/docs` — Interactive Swagger UI documentation
- **GET** `/openapi.json` — OpenAPI schema

---

## 💻 Usage Examples

### Using cURL
```bash
curl -F "file=@/path/to/receipt.jpg" http://localhost:8000/receipt
```

### Using Python
```python
import requests

with open("receipt.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/receipt", files=files)
    print(response.json())
```

### Using JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('receipt.jpg'));

axios.post('http://localhost:8000/receipt', form, {
    headers: form.getHeaders()
}).then(res => console.log(res.data));
```

### Using Browser
1. Go to `http://localhost:8000/docs`
2. Click "Try it out" on `/receipt` endpoint
3. Select receipt image file
4. Click "Execute"

---

## 📊 Response Format

```json
{
  "items": [
    {
      "name": "PRODUCT NAME",
      "price": 12.99,
      "confidence": 7
    }
  ],
  "discounts": [
    {
      "name": "SAVINGS",
      "price": 2.00,
      "confidence": 3
    }
  ],
  "summary": {
    "items_found": 9,
    "subtotal": 129.64,
    "savings": 2.00,
    "total": 127.64
  }
}
```

---

## 🔧 Configuration

### Change Port
```bash
python -m uvicorn receipt_api:app --host 0.0.0.0 --port 5000
```

### Enable Auto-Reload (Development)
```bash
python -m uvicorn receipt_api:app --host 0.0.0.0 --port 8000 --reload
```

### Bind to Localhost Only
```bash
python -m uvicorn receipt_api:app --host 127.0.0.1 --port 8000
```

---

## 🌐 Remote Access

### Local Network (Same WiFi)
Replace `localhost` with your machine IP:
```bash
curl -F "file=@receipt.jpg" http://192.168.x.x:8000/receipt
```

### Public Internet (Using ngrok)
```bash
pip install ngrok
ngrok http 8000
# Then use the provided public URL
curl -F "file=@receipt.jpg" https://xxxxx-xx-xxx-xxx-xx.ngrok.io/receipt
```

### Docker Deployment
```bash
docker build -t receipt-ocr-api .
docker run -p 8000:8000 receipt-ocr-api
```

---

## 📋 Requirements

- Python 3.8+
- FastAPI, Uvicorn
- OpenCV, Tesseract OCR (local)
- NumPy, Pytesseract

See `requirements.txt` for full list.

---

## ✅ Verification

Check if API is running:
```bash
curl http://localhost:8000/health
# Returns: {"status":"ok"}
```

Get API info:
```bash
curl http://localhost:8000/
# Returns: API endpoints and info
```

---

## 📝 Notes

- OCR uses local Tesseract engine (no internet required)
- Auto-cropping detects receipt area automatically
- Confidence scores indicate how many OCR passes agreed on the result
- Processing time: 10-20 seconds per receipt (CPU-dependent)

---

## 🐛 Troubleshooting

**Port 8000 already in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**Tesseract not found:**
```bash
# Linux
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows
Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**Module import errors:**
```bash
pip install --upgrade -r requirements.txt
```

---

## 📞 Support

- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`
- Check terminal logs for detailed error messages
# alexchesler-rila01
# alexchesler-rila01
