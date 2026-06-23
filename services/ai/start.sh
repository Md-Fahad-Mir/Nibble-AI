#!/bin/bash

echo "================================"
echo "  Receipt OCR API - Startup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python $(python3 --version) found"
echo ""

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✓ Dependencies installed"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "✓ All dependencies already installed"
fi

echo ""
echo "================================"
echo "  Starting API Server"
echo "================================"
echo ""
echo "🚀 Server starting at: http://0.0.0.0:8000"
echo "📚 Documentation at:   http://localhost:8000/docs"
echo "🏥 Health check:       http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python3 -m uvicorn receipt_api:app --host 0.0.0.0 --port 8000
