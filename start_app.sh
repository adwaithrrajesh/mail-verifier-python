#!/bin/bash

# Email Finder Application Startup Script
# This script starts the Flask application on port 8008

echo "🚀 Starting Email Finder Application..."
echo "📍 Port: 8008"
echo "🌐 Access: http://localhost:8008"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python -m venv venv' first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "📦 Checking dependencies..."
pip list | grep -q "dnspython" || {
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
}

# Start the application
echo "🎯 Starting Flask application..."
echo "Press CTRL+C to stop the application"
echo ""

python -m mailscout
