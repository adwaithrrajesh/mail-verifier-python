#!/bin/bash

# MailScout Hetzner Deployment Script
# Complete installation and configuration for 5GB RAM optimization
# Target: 90-95% success rate, 2-5 minutes for 1000 emails

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="mailscout"
APP_PORT=8008
PYTHON_VERSION="3.11"
VENV_NAME="venv"
LOG_FILE="/var/log/mailscout.log"
SERVICE_NAME="mailscout"
USER_NAME="mailscout"

echo -e "${BLUE}🚀 MailScout Hetzner Deployment Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${CYAN}Target: 90-95% success rate, 2-5 minutes for 1000 emails${NC}"
echo -e "${CYAN}Optimized for: 5GB RAM, Hetzner Cloud${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   print_info "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed"
    exit 1
fi

print_status "Starting MailScout deployment on Hetzner..."

# Update system packages
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_info "Installing system dependencies..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    git \
    curl \
    wget \
    htop \
    netstat-nat \
    ufw \
    fail2ban \
    logrotate

# Create application user
print_info "Creating application user..."
if ! id "$USER_NAME" &>/dev/null; then
    sudo useradd -m -s /bin/bash "$USER_NAME"
    print_status "User $USER_NAME created"
else
    print_info "User $USER_NAME already exists"
fi

# Create application directory
APP_DIR="/opt/$APP_NAME"
print_info "Setting up application directory..."
sudo mkdir -p "$APP_DIR"
sudo chown "$USER_NAME:$USER_NAME" "$APP_DIR"

# Copy application files
print_info "Copying application files..."
cp -r . "$APP_DIR/"
cd "$APP_DIR"

# Set proper permissions
sudo chown -R "$USER_NAME:$USER_NAME" "$APP_DIR"
chmod +x *.sh

# Create virtual environment
print_info "Creating Python virtual environment..."
sudo -u "$USER_NAME" python3.11 -m venv "$APP_DIR/$VENV_NAME"

# Activate virtual environment and install dependencies
print_info "Installing Python dependencies..."
sudo -u "$USER_NAME" bash -c "source $APP_DIR/$VENV_NAME/bin/activate && pip install --upgrade pip"
sudo -u "$USER_NAME" bash -c "source $APP_DIR/$VENV_NAME/bin/activate && pip install -r requirements.txt"

# Configure firewall
print_info "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow $APP_PORT/tcp
sudo ufw allow 587/tcp  # SMTP port
sudo ufw allow 465/tcp  # SMTP SSL port
sudo ufw allow 25/tcp   # SMTP port (if unblocked by Hetzner)
print_status "Firewall configured"

# Configure fail2ban for security
print_info "Configuring fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[mailscout]
enabled = true
port = $APP_PORT
logpath = $LOG_FILE
maxretry = 10
bantime = 1800
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban
print_status "Fail2ban configured"

# Create systemd service
print_info "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=MailScout Email Finder Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/$VENV_NAME/bin
ExecStart=$APP_DIR/$VENV_NAME/bin/python -m mailscout
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Create log directory and file
sudo mkdir -p /var/log
sudo touch "$LOG_FILE"
sudo chown "$USER_NAME:$USER_NAME" "$LOG_FILE"

# Configure log rotation
print_info "Configuring log rotation..."
sudo tee /etc/logrotate.d/$SERVICE_NAME > /dev/null <<EOF
$LOG_FILE {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER_NAME $USER_NAME
    postrotate
        systemctl reload $SERVICE_NAME > /dev/null 2>&1 || true
    endscript
}
EOF

# Create startup script
print_info "Creating optimized startup script..."
sudo -u "$USER_NAME" tee "$APP_DIR/start_optimized.sh" > /dev/null <<'EOF'
#!/bin/bash

# MailScout Optimized Startup Script for Hetzner
# Optimized for 5GB RAM with 90-95% success rate

echo "🚀 Starting MailScout with Hetzner optimizations..."
echo "================================================"

# Set optimal environment variables for 5GB RAM
export NUM_THREADS=50
export NUM_BULK_THREADS=25
export SMTP_TIMEOUT=8
export BATCH_SIZE=100
export CONNECTION_POOL_SIZE=50
export MAX_RETRIES=3
export RETRY_DELAY=1.0
export RATE_LIMIT_PER_MINUTE=500

# Memory optimization
export PYTHONHASHSEED=0
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Network optimization
export DNS_CACHE_SIZE=2000
export CONNECTION_REUSE=true
export CIRCUIT_BREAKER=true

# Apply Hetzner configuration
echo "Applying Hetzner-optimized settings..."
python hetzner_config.py

echo "🎯 Target Success Rate: 90-95%"
echo "⚡ Expected Performance: 5-10 emails/second"
echo "💾 Memory Usage: ~4GB (optimized for 5GB RAM)"
echo "🌐 Server: http://0.0.0.0:8008"
echo ""

# Start the application
exec python -m mailscout
EOF

chmod +x "$APP_DIR/start_optimized.sh"

# Create health check script
print_info "Creating health check script..."
sudo -u "$USER_NAME" tee "$APP_DIR/health_check.sh" > /dev/null <<'EOF'
#!/bin/bash

# MailScout Health Check Script
APP_PORT=8008
HEALTH_URL="http://localhost:$APP_PORT/stats"

# Check if service is running
if ! pgrep -f "python -m mailscout" > /dev/null; then
    echo "❌ MailScout service is not running"
    exit 1
fi

# Check if port is listening
if ! netstat -tlnp | grep ":$APP_PORT " > /dev/null; then
    echo "❌ MailScout is not listening on port $APP_PORT"
    exit 1
fi

# Check HTTP response
if curl -s -f "$HEALTH_URL" > /dev/null; then
    echo "✅ MailScout is healthy"
    exit 0
else
    echo "❌ MailScout health check failed"
    exit 1
fi
EOF

chmod +x "$APP_DIR/health_check.sh"

# Create monitoring script
print_info "Creating monitoring script..."
sudo -u "$USER_NAME" tee "$APP_DIR/monitor.sh" > /dev/null <<'EOF'
#!/bin/bash

# MailScout Monitoring Script
echo "📊 MailScout Performance Monitor"
echo "================================"

# Get service status
echo "🔍 Service Status:"
systemctl is-active mailscout
echo ""

# Get performance stats
echo "📈 Performance Statistics:"
curl -s http://localhost:8008/stats | python3 -m json.tool
echo ""

# Get system resources
echo "💻 System Resources:"
echo "Memory Usage:"
free -h
echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)"
echo ""

# Get network connections
echo "🌐 Network Connections:"
netstat -tlnp | grep :8008
echo ""

# Get recent logs
echo "📝 Recent Logs:"
journalctl -u mailscout -n 20 --no-pager
EOF

chmod +x "$APP_DIR/monitor.sh"

# Reload systemd and start service
print_info "Starting MailScout service..."
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl start "$SERVICE_NAME"

# Wait for service to start
sleep 5

# Check if service is running
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_status "MailScout service started successfully"
else
    print_error "Failed to start MailScout service"
    print_info "Checking logs..."
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    exit 1
fi

# Test the service
print_info "Testing MailScout service..."
sleep 3

if curl -s -f "http://localhost:$APP_PORT" > /dev/null; then
    print_status "MailScout is responding correctly"
else
    print_warning "MailScout may not be fully ready yet"
fi

# Display service information
echo ""
echo -e "${GREEN}🎉 MailScout Deployment Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${CYAN}📊 Service Information:${NC}"
echo -e "   Service Name: $SERVICE_NAME"
echo -e "   Application Port: $APP_PORT"
echo -e "   Application Directory: $APP_DIR"
echo -e "   Log File: $LOG_FILE"
echo -e "   User: $USER_NAME"
echo ""
echo -e "${CYAN}🌐 Access URLs:${NC}"
echo -e "   Main API: http://$(curl -s ifconfig.me):$APP_PORT"
echo -e "   Health Check: http://$(curl -s ifconfig.me):$APP_PORT/stats"
echo -e "   Diagnostics: http://$(curl -s ifconfig.me):$APP_PORT/diagnostics/smtp"
echo ""
echo -e "${CYAN}🔧 Management Commands:${NC}"
echo -e "   Start:   sudo systemctl start $SERVICE_NAME"
echo -e "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo -e "   Restart: sudo systemctl restart $SERVICE_NAME"
echo -e "   Status:  sudo systemctl status $SERVICE_NAME"
echo -e "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo -e "   Monitor: $APP_DIR/monitor.sh"
echo ""
echo -e "${CYAN}📈 Performance Expectations:${NC}"
echo -e "   Success Rate: 90-95%"
echo -e "   1000 emails: 2-5 minutes"
echo -e "   Memory Usage: ~4GB"
echo -e "   Concurrent Threads: 50"
echo -e "   Batch Size: 100 emails"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "   - Port 587 is used primarily (works on Hetzner)"
echo -e "   - Ports 25/465 may be blocked by Hetzner"
echo -e "   - Request port unblocking from Hetzner for max success rate"
echo -e "   - Monitor logs for any issues"
echo ""
print_status "Deployment completed successfully!"
