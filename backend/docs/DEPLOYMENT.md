# NewsHub Backend Deployment Guide

## Prerequisites
- Python 3.11+
- PostgreSQL 14+ (recommended for production)
- Redis (for caching and sessions)
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- SSL certificate (Let's Encrypt recommended)

## Server Setup (Ubuntu 22.04)

### 1. Install System Dependencies
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip postgresql postgresql-contrib nginx redis-server
```

### 2. Create Database
```bash
sudo -u postgres psql
CREATE DATABASE newshub_db;
CREATE USER newshub_user WITH PASSWORD 'strong_password';
ALTER ROLE newshub_user SET client_encoding TO 'utf8';
ALTER ROLE newshub_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE newshub_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE newshub_db TO newshub_user;
\q
```

### 3. Clone and Setup Application
```bash
cd /var/www
git clone <repository-url> newshub
cd newshub/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4. Configure Environment
```bash
cp .env.example .env
nano .env
```

**Production .env:**
```env
SECRET_KEY=<generate-with-django-command>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://newshub_user:strong_password@localhost:5432/newshub_db
```

### 5. Run Migrations and Collect Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6. Configure Gunicorn
Create `/etc/systemd/system/newshub.service`:
```ini
[Unit]
Description=NewsHub Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/newshub/backend
Environment="PATH=/var/www/newshub/backend/venv/bin"
ExecStart=/var/www/newshub/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/newshub/backend/newshub.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start newshub
sudo systemctl enable newshub
```

### 7. Configure Nginx
Create `/etc/nginx/sites-available/newshub`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/newshub/backend/staticfiles/;
    }
    
    location /media/ {
        alias /var/www/newshub/backend/media/;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/newshub/backend/newshub.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/newshub /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## Monitoring & Maintenance

### Log Files
- Application: `journalctl -u newshub -f`
- Nginx: `/var/log/nginx/error.log`

### Database Backups
```bash
# Daily backup cron job
0 2 * * * pg_dump newshub_db > /backups/newshub_$(date +\%Y\%m\%d).sql
```

### Updates
```bash
cd /var/www/newshub/backend
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart newshub
```
