#!/bin/bash
# Production start script for Google Trends API

set -e

echo "🚀 Google Trends API - Starting..."
echo "=================================="

# For Docker/Railway deployment
if [ -f "/.dockerenv" ] || [ -n "$RAILWAY_ENVIRONMENT" ]; then
    echo "🐳 Running in containerized environment"
    
    # Verify Chrome and ChromeDriver
    echo "🔍 Verifying Chrome installation..."
    if command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version 2>/dev/null || echo "Unknown")
        echo "   Chrome: $CHROME_VERSION"
    else
        echo "   ⚠️  Chrome not found"
    fi
    
    echo "🔍 Verifying ChromeDriver..."
    if [ -f "/usr/bin/chromedriver" ]; then
        DRIVER_VERSION=$(/usr/bin/chromedriver --version 2>/dev/null || echo "Unknown")
        echo "   ChromeDriver: $DRIVER_VERSION"
        echo "   Path: /usr/bin/chromedriver"
        ls -lh /usr/bin/chromedriver
    elif [ -f "/usr/bin/chromium-driver" ]; then
        DRIVER_VERSION=$(/usr/bin/chromium-driver --version 2>/dev/null || echo "Unknown")
        echo "   ChromeDriver: $DRIVER_VERSION"
        echo "   Path: /usr/bin/chromium-driver"
        ls -lh /usr/bin/chromium-driver
        export CHROMEDRIVER_PATH=/usr/bin/chromium-driver
    else
        echo "   ⚠️  ChromeDriver not found!"
        echo "   Searching for ChromeDriver..."
        find /usr -name "*chromedriver*" 2>/dev/null || true
    fi
    
    # Create temp directory
    mkdir -p temp_downloads
    
    echo ""
    echo "✅ Starting Google Trends API (Production Mode)..."
    echo "   Port: 8000"
    echo ""
    
    # Start with uvicorn directly
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000
fi

# For local development
echo "💻 Running in local development mode"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create temp directory
mkdir -p temp_downloads

# Start API
echo ""
echo "✅ Starting Google Trends API..."
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python src/main.py
