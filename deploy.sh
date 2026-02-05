#!/bin/bash

#########################################
# NewsHub EC2 Deployment Script
# Run this on your EC2 Ubuntu server
#########################################

set -e  # Exit on error

echo "=========================================="
echo "NewsHub Deployment Script"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
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
if [ "$EUID" -eq 0 ]; then 
    log_error "Please do not run this script as root"
    exit 1
fi

# Get deployment directory
DEPLOY_DIR="/var/www/newshub"
REPO_URL="https://github.com/SaketSinghRajput/abdnews.git"

# Database credentials
DB_NAME="newshub_db"
DB_USER="newshub_user"
DB_PASSWORD="123456789"

# Step 1: Update system packages
log_info "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install dependencies
log_info "Step 2: Installing system dependencies..."
# Update repositories first to make sure everything is current
sudo apt update

# Install the standard Python 3 packages (which are 3.10 on Ubuntu 22.04)
sudo apt install -y python3 python3-venv python3-pip python3-dev build-essential libssl-dev libffi-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y git
sudo apt install -y supervisor

# Step 3: Setup PostgreSQL
log_info "Step 3: Setting up PostgreSQL database..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check if database exists
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
if [ "$DB_EXISTS" != "1" ]; then
    log_info "Creating database and user..."
    sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
    log_info "Database created successfully"
else
    log_warn "Database already exists, using existing database: $DB_NAME"
fi

# Step 4: Clone repository
log_info "Step 4: Setting up application directory..."

# Check if we're already in a git repo or need to clone
if [ -d "$DEPLOY_DIR/.git" ]; then
    log_warn "Git repository exists. Pulling latest changes..."
    cd $DEPLOY_DIR
    git pull origin main
elif [ -d "$DEPLOY_DIR/abdnews/.git" ]; then
    log_warn "Repository found in subdirectory. Using abdnews as deploy directory..."
    DEPLOY_DIR="$DEPLOY_DIR/abdnews"
    cd $DEPLOY_DIR
    git pull origin main
elif [ -d "$DEPLOY_DIR" ] && [ "$(ls -A $DEPLOY_DIR)" ]; then
    log_warn "Directory exists but no git repo found. Backing up and cloning fresh..."
    sudo mv $DEPLOY_DIR $DEPLOY_DIR.backup.$(date +%Y%m%d_%H%M%S)
    sudo mkdir -p $DEPLOY_DIR
    sudo chown $USER:$USER $DEPLOY_DIR
    git clone $REPO_URL $DEPLOY_DIR
else
    log_info "Cloning repository..."
    sudo mkdir -p $DEPLOY_DIR
    sudo chown $USER:$USER $DEPLOY_DIR
    git clone $REPO_URL $DEPLOY_DIR
fi

cd $DEPLOY_DIR

# Step 5: Setup Python virtual environment
log_info "Step 5: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_info "Virtual environment created"
else
    log_warn "Virtual environment already exists"
fi

source venv/bin/activate

# Step 6: Install Python dependencies
log_info "Step 6: Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt
pip install gunicorn psycopg2-binary

# Step 7: Configure Django
log_info "Step 7: Configuring Django..."
cd backend

# Create .env file if not exists
if [ ! -f ".env" ]; then
    log_info "Creating .env file..."
    cat > .env << EOF
DEBUG=False
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=*
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
EOF
    log_info ".env file created"
else
    log_warn ".env file already exists"
fi

# Step 8: Run Django migrations
log_info "Step 8: Running database migrations..."
python manage.py migrate

# Step 9: Create superuser (if needed)
log_info "Step 9: Checking for superuser..."
SUPERUSER_EXISTS=$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())")
if [ "$SUPERUSER_EXISTS" != "True" ]; then
    log_warn "No superuser found. Please create one:"
    python manage.py createsuperuser
fi

# Step 10: Setup demo data
log_info "Step 10: Setting up demo data..."
if [ -f "scripts/setup_demo_data.py" ]; then
    python scripts/setup_demo_data.py
else
    log_warn "Demo data script not found, skipping..."
fi

# Step 11: Collect static files
log_info "Step 11: Collecting static files..."
python manage.py collectstatic --noinput

# Step 12: Setup Gunicorn
log_info "Step 12: Configuring Gunicorn..."
sudo tee /etc/systemd/system/gunicorn.socket > /dev/null << EOF
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
EOF

sudo tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=gunicorn daemon for NewsHub
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=$USER
Group=www-data
WorkingDirectory=$DEPLOY_DIR/backend
ExecStart=$DEPLOY_DIR/venv/bin/gunicorn \\
    --workers 3 \\
    --worker-class sync \\
    --bind unix:/run/gunicorn.sock \\
    --timeout 120 \\
    config.wsgi:application

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

log_info "Gunicorn configured and started"

# Step 13: Configure Nginx
log_info "Step 13: Configuring Nginx..."
sudo tee /etc/nginx/sites-available/newshub > /dev/null << EOF
upstream gunicorn {
    server unix:/run/gunicorn.sock;
}

server {
    listen 80;
    server_name _;
    client_max_body_size 50M;

    # Static files
    location /static/ {
        alias $DEPLOY_DIR/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $DEPLOY_DIR/backend/media/;
        expires 30d;
    }

    # Frontend
    location / {
        alias $DEPLOY_DIR/frontend/;
        try_files \$uri \$uri/ /index.html;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API routes
    location /api/ {
        proxy_pass http://gunicorn;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://gunicorn;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/newshub /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

log_info "Nginx configured and started"

# Step 14: Setup firewall
log_info "Step 14: Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

log_info "Firewall configured"

# Step 15: Set permissions
log_info "Step 15: Setting file permissions..."
sudo chown -R $USER:www-data $DEPLOY_DIR
sudo chmod -R 755 $DEPLOY_DIR
sudo chown -R www-data:www-data $DEPLOY_DIR/backend/media
sudo chown -R www-data:www-data $DEPLOY_DIR/backend/staticfiles

echo ""
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Your NewsHub application is now running!"
echo ""
echo "Access points:"
echo "  - Frontend: http://$(curl -s ifconfig.me)/"
echo "  - Admin: http://$(curl -s ifconfig.me)/admin/"
echo ""
echo "Default credentials:"
echo "  - Username: admin"
echo "  - Password: Demo@123456"
echo ""
echo "Important next steps:"
echo "  1. Change default passwords"
echo "  2. Configure domain name"
echo "  3. Setup SSL certificate (use certbot)"
echo "  4. Configure email settings in .env"
echo "  5. Review security settings"
echo ""
echo "Useful commands:"
echo "  - Check Gunicorn: sudo systemctl status gunicorn"
echo "  - Check Nginx: sudo systemctl status nginx"
echo "  - View logs: sudo journalctl -u gunicorn -f"
echo "  - Restart app: sudo systemctl restart gunicorn"
echo ""
echo "=========================================="
