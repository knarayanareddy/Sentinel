#!/bin/bash
set -e

echo "=== SENTINEL Deployment Script ==="
echo "Target: Vultr VM at 78.141.222.154"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root"
    exit 1
fi

# Step 1: System Updates
log_info "Step 1/8: Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# Step 2: Install Python 3.11+
log_info "Step 2/8: Installing Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update -qq
    apt-get install -y -qq python3.11 python3.11-venv python3.11-dev python3-pip
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
fi
log_info "Python version: $(python3 --version)"

# Step 3: Install Node.js 18+
log_info "Step 3/8: Installing Node.js 18..."
if ! command -v node &> /dev/null || [[ $(node --version | cut -d'v' -f2 | cut -d'.' -f1) -lt 18 ]]; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y -qq nodejs
fi
log_info "Node version: $(node --version)"
log_info "npm version: $(npm --version)"

# Step 4: Install nginx
log_info "Step 4/8: Installing nginx..."
apt-get install -y -qq nginx
systemctl enable nginx

# Step 5: Setup project directory
log_info "Step 5/8: Setting up project directory..."
mkdir -p /opt/sentinel
cd /opt/sentinel

# Check if project files exist
if [ ! -f "requirements.txt" ]; then
    log_error "Project files not found in /opt/sentinel"
    log_error "Please copy project files to /opt/sentinel first"
    exit 1
fi

# Step 6: Install Python dependencies
log_info "Step 6/8: Installing Python dependencies..."
python3.11 -m venv /opt/sentinel/venv
source /opt/sentinel/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 7: Build frontend
log_info "Step 7/8: Building frontend..."
cd frontend
npm install --production=false
npm run build
cd ..

# Step 8: Configure services
log_info "Step 8/8: Configuring services..."

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_warn ".env file created from .env.example"
        log_warn "Please edit /opt/sentinel/.env with actual values before starting services"
    else
        log_error ".env.example not found"
        exit 1
    fi
fi

# Install systemd service
cp deploy/sentinel-backend.service /etc/systemd/system/
systemctl daemon-reload

# Install nginx config
cp deploy/nginx.conf /etc/nginx/sites-available/sentinel
ln -sf /etc/nginx/sites-available/sentinel /etc/nginx/sites-enabled/sentinel
rm -f /etc/nginx/sites-enabled/default
nginx -t

# Create incidents directory
mkdir -p incidents
chmod 755 incidents

log_info "Deployment complete!"
echo ""
log_warn "IMPORTANT: Before starting services:"
echo "  1. Edit /opt/sentinel/.env with your Vultr API credentials"
echo "  2. Run: systemctl start sentinel-backend"
echo "  3. Run: systemctl start nginx"
echo "  4. Access the application at: http://78.141.222.154"
echo ""
log_info "Useful commands:"
echo "  View backend logs: journalctl -u sentinel-backend -f"
echo "  Restart backend: systemctl restart sentinel-backend"
echo "  Restart nginx: systemctl restart nginx"
echo "  Check status: systemctl status sentinel-backend nginx"
