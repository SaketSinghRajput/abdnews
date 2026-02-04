#!/bin/bash

#########################################
# NewsHub Update/Redeploy Script
# Run this to update your deployment
#########################################

set -e

echo "=========================================="
echo "NewsHub Update Script"
echo "=========================================="

DEPLOY_DIR="/var/www/newshub"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

cd $DEPLOY_DIR

# Pull latest changes
log_info "Pulling latest changes from repository..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
log_info "Updating Python dependencies..."
pip install -r backend/requirements.txt

# Run migrations
log_info "Running database migrations..."
cd backend
python manage.py migrate

# Collect static files
log_info "Collecting static files..."
python manage.py collectstatic --noinput

# Restart Gunicorn
log_info "Restarting Gunicorn..."
sudo systemctl restart gunicorn

# Reload Nginx
log_info "Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "✓ Update completed successfully!"
echo "=========================================="
echo ""
echo "Application has been updated and restarted."
echo ""
