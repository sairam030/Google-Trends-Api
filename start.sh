#!/bin/bash
# Production start script for Google Trends API

set -e

echo "🚀 Google Trends API - Starting..."
echo "=================================="

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
