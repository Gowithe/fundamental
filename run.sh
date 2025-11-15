#!/bin/bash

# Stock Analyzer - Run Script for macOS/Linux

echo "🚀 Stock Analyzer - Starting..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run app
echo ""
echo "🎯 Starting Flask server..."
echo "📍 Open browser: http://localhost:5000"
echo ""
python app.py
