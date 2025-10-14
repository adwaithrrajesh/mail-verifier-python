#!/bin/bash

# MailScout Email Finder - Run Script
# This script activates the virtual environment and runs the mailscout module

echo "Starting MailScout Email Finder..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run 'python3 -m venv venv' first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
python -c "import dns.resolver, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the mailscout module
echo "Starting MailScout server..."
echo "Server will be available at: http://127.0.0.1:8008"
echo "Press Ctrl+C to stop the server"
echo ""

python -m mailscout
