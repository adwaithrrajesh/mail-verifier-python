#!/bin/bash

# MailScout Email Finder - Hetzner Optimized
# Optimized for Hetzner 4GB RAM, 20GB SSD, 20TB traffic

echo "🚀 Starting MailScout on Hetzner Server..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run 'python3 -m venv venv' first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "Checking dependencies..."
python -c "import dns.resolver, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Apply Hetzner-optimized configuration
echo "Applying Hetzner-optimized settings..."
python hetzner_config.py

# Set environment variables for Hetzner optimization (5GB RAM)
export NUM_THREADS=50
export NUM_BULK_THREADS=25
export SMTP_TIMEOUT=8
export BATCH_SIZE=100
export CONNECTION_POOL_SIZE=50
export MAX_RETRIES=3
export RETRY_DELAY=1.0
export RATE_LIMIT_PER_MINUTE=500

# Run the mailscout module with Hetzner optimizations
echo "Starting MailScout server with Hetzner optimizations..."
echo "Server will be available at: http://0.0.0.0:8008"
echo "Expected performance: 5-10 emails/second (1000 emails in 2-5 minutes)"
echo "Target success rate: 90-95%"
echo "Memory usage: ~4GB (optimized for 5GB RAM)"
echo "Press Ctrl+C to stop the server"
echo ""

python -m mailscout

