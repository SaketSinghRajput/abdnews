# AWS EC2 Ubuntu Deployment Guide - NewsHub

Complete step-by-step guide to deploy NewsHub on AWS EC2 Ubuntu server.

## Prerequisites
- AWS Account with EC2 access
- GitHub repository: https://github.com/SaketSinghRajput/abdnews.git
- SSH key pair for EC2 instance

---

## Step 1: Launch EC2 Instance

### 1.1 Create EC2 Instance
1. Go to AWS Console → EC2 Dashboard
2. Click "Launch Instances"
3. **AMI Selection**: Choose "Ubuntu Server 22.04 LTS" (free tier eligible)
4. **Instance Type**: t2.micro (free tier) or t2.small (recommended for production)
5. **Storage**: 30 GB (default should be fine)
6. **Security Group**: 
   - Allow SSH (port 22) - from your IP
   - Allow HTTP (port 80) - from 0.0.0.0/0
   - Allow HTTPS (port 443) - from 0.0.0.0/0
7. **Key Pair**: Create or select your key pair
8. Launch the instance and note the Public IP address

### 1.2 Connect to Instance
```bash
# On your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## Step 2: System Update & Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and development tools
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# Install PostgreSQL (Database)
sudo apt install -y postgresql postgresql-contrib

# Install Nginx (Web Server)
sudo apt install -y nginx

# Install Node.js (for frontend build tools if needed)
sudo apt install -y nodejs npm

# Install Git
sudo apt install -y git

# Install Supervisor (Process Manager)
sudo apt install -y supervisor

# Install Certbot (SSL Certificates)
sudo apt install -y certbot python3-certbot-nginx
```

---

## Step 3: Database Setup

```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user (in psql shell):
CREATE DATABASE newshub_db;
CREATE USER newshub_user WITH PASSWORD 'your_secure_password';
ALTER ROLE newshub_user SET client_encoding TO 'utf8';
ALTER ROLE newshub_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE newshub_user SET default_transaction_deferrable TO on;
ALTER ROLE newshub_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE newshub_db TO newshub_user;
\q
```

---

## Step 4: Clone Repository & Setup Backend

```bash
# Create app directory
sudo mkdir -p /var/www/newshub
sudo chown ubuntu:ubuntu /var/www/newshub
cd /var/www/newshub

# Clone repository
git clone https://github.com/SaketSinghRajput/abdnews.git .

# Create Python virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# Add psycopg2 for PostgreSQL
pip install psycopg2-binary
```

---

## Step 5: Configure Django Backend

```bash
cd /var/www/newshub/backend

# Create .env file with production settings
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your_secret_key_generate_with_python_secrets
ALLOWED_HOSTS=your_domain.com,www.your_domain.com,YOUR_EC2_IP
DATABASE_NAME=newshub_db
DATABASE_USER=newshub_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
CORS_ALLOWED_ORIGINS=https://your_domain.com,https://www.your_domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
EOF

# Generate secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" >> .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

---

## Step 6: Configure Gunicorn

```bash
cd /var/www/newshub

# Install Gunicorn
pip install gunicorn

# Create Gunicorn socket file
sudo nano /etc/systemd/system/gunicorn.socket
```

Paste this content:
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create service file:
```bash
sudo nano /etc/systemd/system/gunicorn.service
```

Paste this content:
```ini
[Unit]
Description=gunicorn daemon for NewsHub
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/newshub/backend
ExecStart=/var/www/newshub/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind unix:/run/gunicorn.sock \
    --timeout 120 \
    config.wsgi:application

Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start Gunicorn:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl start gunicorn.service
sudo systemctl enable gunicorn.service

# Check status
sudo systemctl status gunicorn.service
```

---

## Step 7: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/newshub
```

Paste this content:
```nginx
upstream gunicorn {
    server unix:/run/gunicorn.sock;
}

server {
    listen 80;
    server_name your_domain.com www.your_domain.com;
    client_max_body_size 50M;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your_domain.com www.your_domain.com;
    client_max_body_size 50M;

    # SSL certificates (will be created by Certbot)
    ssl_certificate /etc/letsencrypt/live/your_domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your_domain.com/privkey.pem;

    # SSL security headers
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Static files
    location /static/ {
        alias /var/www/newshub/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/newshub/backend/media/;
        expires 30d;
    }

    # Frontend (React/Vue or static HTML)
    location / {
        alias /var/www/newshub/frontend/;
        try_files $uri $uri/ /index.html;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # API routes - proxy to Gunicorn
    location /api/ {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/newshub /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## Step 8: Setup SSL Certificate

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot certonly --nginx -d your_domain.com -d www.your_domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

---

## Step 9: Configure Firewall (UFW)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## Step 10: Setup Cron Jobs for Background Tasks

```bash
# Open crontab
crontab -e

# Add these lines:
# Run Django management commands
0 * * * * cd /var/www/newshub/backend && /var/www/newshub/venv/bin/python manage.py clearsessions

# Backup database daily at 2 AM
0 2 * * * sudo -u postgres pg_dump newshub_db > /var/backups/newshub_db_$(date +\%Y\%m\%d).sql
```

---

## Step 11: Setup Monitoring & Logs

```bash
# Check Django logs
sudo journalctl -u gunicorn.service -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check Supervisor logs
sudo tail -f /var/log/supervisor/gunicorn.log
```

---

## Step 12: Domain Configuration (DNS)

1. Go to your domain registrar
2. Update DNS records to point to EC2 Elastic IP:
   - **A Record**: your_domain.com → YOUR_EC2_IP
   - **A Record**: www.your_domain.com → YOUR_EC2_IP

Wait 5-10 minutes for DNS propagation.

---

## Post-Deployment Checklist

- [ ] Database is created and running
- [ ] Django migrations applied
- [ ] Static files collected
- [ ] Gunicorn is running
- [ ] Nginx is configured and running
- [ ] SSL certificate installed
- [ ] DNS records updated
- [ ] Email configuration working
- [ ] Backup system configured
- [ ] Monitoring setup complete

---

## Troubleshooting

### Gunicorn not starting
```bash
sudo systemctl status gunicorn.service
sudo journalctl -u gunicorn.service -n 50
```

### Nginx 502 Bad Gateway
```bash
# Check Gunicorn socket
ls -la /run/gunicorn.sock
sudo systemctl restart gunicorn.service
```

### Static files not loading
```bash
cd /var/www/newshub/backend
python manage.py collectstatic --noinput --clear
sudo chown -R www-data:www-data staticfiles/
```

### SSL certificate issues
```bash
sudo certbot renew --force-renewal
sudo systemctl restart nginx
```

---

## Performance Optimization

### Enable Gzip compression in Nginx
```nginx
gzip on;
gzip_types text/plain text/css text/javascript application/json application/javascript;
gzip_min_length 1000;
```

### Redis caching (optional)
```bash
sudo apt install redis-server
pip install django-redis
```

### Database optimization
```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_articles_published ON articles(published_at);
CREATE INDEX idx_articles_category ON articles(category_id);
```

---

## Security Best Practices

1. **Fail2Ban** - Prevent brute force attacks
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

2. **Regular backups**
```bash
sudo -u postgres pg_dump newshub_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

3. **Keep system updated**
```bash
sudo apt update && sudo apt upgrade -y
```

4. **Monitor server resources**
```bash
htop
df -h
free -h
```

---

## Contact & Support

- GitHub: https://github.com/SaketSinghRajput/abdnews.git
- Issues: Check GitHub Issues page
- Email: your_email@example.com

---

**Happy Deployment!** 🚀
