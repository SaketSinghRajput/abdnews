#!/bin/bash

#########################################
# NewsHub Demo Data Setup Script
# Run this on your EC2 server to populate demo content
#########################################

set -e  # Exit on error

echo "=========================================="
echo "NewsHub Demo Data Setup"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Detect deployment directory
if [ -d "/var/www/newshub/abdnews/.git" ]; then
    DEPLOY_DIR="/var/www/newshub/abdnews"
elif [ -d "/var/www/newshub/.git" ]; then
    DEPLOY_DIR="/var/www/newshub"
else
    log_warn "Could not find deployment directory. Using current directory."
    DEPLOY_DIR=$(pwd)
fi

log_info "Using deployment directory: $DEPLOY_DIR"
cd $DEPLOY_DIR

# Activate virtual environment
log_info "Activating virtual environment..."
if [ -f "/venv/bin/activate" ]; then
    source /venv/bin/activate
else
    log_warn "Virtual environment not found at venv/bin/activate"
    exit 1
fi

# Run demo data setup
log_info "Setting up demo data..."
cd backend

if [ -f "scripts/setup_demo_data.py" ]; then
    python scripts/setup_demo_data.py
    log_info "Demo data setup completed successfully!"
else
    log_warn "Demo data script not found at backend/scripts/setup_demo_data.py"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Demo Data Setup Complete!"
echo "=========================================="
echo ""
echo "Demo content created:"
echo "  - 10 categories"
echo "  - 3 subscription plans"
echo "  - 5 demo users"
echo "  - 10 full articles"
echo ""
echo "Admin credentials:"
echo "  - Username: admin"
echo "  - Password: Demo@123456"
echo ""
echo "=========================================="
