# NewsHub EC2 Deployment Scripts

This directory contains automated deployment scripts for AWS EC2 Ubuntu servers.

## 📦 Files Overview

### 1. `deploy.sh`
Main deployment script that sets up everything from scratch on a fresh EC2 Ubuntu instance.

**What it does:**
- Updates system packages
- Installs Python, PostgreSQL, Nginx, and dependencies
- Creates database and user
- Clones repository
- Sets up Python virtual environment
- Configures Django application
- Runs migrations and collects static files
- Sets up Gunicorn service
- Configures Nginx reverse proxy
- Sets up firewall rules
- Creates demo data

### 2. `update_deploy.sh`
Quick update script for redeploying after code changes.

**What it does:**
- Pulls latest code from Git
- Updates Python dependencies
- Runs new migrations
- Collects static files
- Restarts Gunicorn and Nginx

### 3. `backend/scripts/setup_demo_data.py`
Python script to populate database with demo content.

**What it creates:**
- 10 news categories (Politics, Technology, Business, etc.)
- 3 subscription plans (Free, Monthly, Yearly)
- 5 demo users (admin, editor, journalists, subscriber)
- 10 demo articles with full content
- All properly linked with realistic data

---

## 🚀 Quick Start Guide

### Step 1: Launch EC2 Instance

```bash
# On AWS Console:
# 1. Launch Ubuntu 22.04 LTS instance
# 2. t2.micro or t2.small
# 3. Add security group rules:
#    - SSH (22) - Your IP
#    - HTTP (80) - 0.0.0.0/0
#    - HTTPS (443) - 0.0.0.0/0
# 4. Create/use your key pair
```

### Step 2: Connect to Instance

```bash
# On your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Download and Run Deployment Script

```bash
# On EC2 instance
# Option 1: Clone repository first
git clone https://github.com/SaketSinghRajput/abdnews.git /var/www/newshub
cd /var/www/newshub
chmod +x deploy.sh
./deploy.sh

# Option 2: Download script directly
wget https://raw.githubusercontent.com/SaketSinghRajput/abdnews/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### Step 4: Access Your Application

```bash
# Get your public IP
curl ifconfig.me

# Access in browser:
# Frontend: http://YOUR_EC2_IP/
# Admin: http://YOUR_EC2_IP/admin/
```

---

## 👤 Default Credentials

After deployment, use these credentials:

**Admin User:**
- Username: `admin`
- Password: `Demo@123456`

**Other Demo Users:**
- `editor` / `Demo@123456`
- `journalist1` / `Demo@123456`
- `journalist2` / `Demo@123456`
- `subscriber1` / `Demo@123456`

⚠️ **IMPORTANT:** Change these passwords immediately in production!

---

## 🔄 Updating Your Deployment

When you push new code to GitHub:

```bash
# On EC2 instance
cd /var/www/newshub
./update_deploy.sh
```

This will:
1. Pull latest code
2. Update dependencies
3. Run migrations
4. Restart services

---

## 🗂️ Demo Data Details

### Categories Created (10)
- Politics
- Technology
- Business
- Entertainment
- Sports
- Health
- Science
- Lifestyle
- Opinion
- World

### Subscription Plans (3)
1. **Free**
   - Price: $0
   - Duration: Unlimited
   - Features: Basic access, 10 articles/month

2. **Premium Monthly**
   - Price: $9.99
   - Duration: 30 days
   - Features: Full access, email notifications, newsletter

3. **Premium Yearly**
   - Price: $99.99
   - Duration: 365 days
   - Features: Full access + best value

### Demo Articles (10)
1. Global Markets Rally - Economic Recovery
2. Revolutionary AI Medical Diagnosis
3. Climate Summit Historic Agreement
4. Championship Finals Overtime Victory
5. Mediterranean Diet Heart Health Study
6. Space Agency Moon Base Plans
7. Fashion Week Sustainable Clothing
8. Tech Giants Data Privacy Scrutiny
9. Political Debate Economic Policy
10. Blockbuster Film Opening Records

Each article includes:
- Full content (3-5 paragraphs)
- Category assignment
- Author attribution
- Realistic timestamps
- View counts
- Featured/breaking flags

---

## 🛠️ Useful Commands

### Check Service Status
```bash
# Gunicorn (Django app)
sudo systemctl status gunicorn

# Nginx (web server)
sudo systemctl status nginx

# PostgreSQL (database)
sudo systemctl status postgresql
```

### View Logs
```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Reload Nginx (no downtime)
sudo systemctl reload nginx

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### Database Management
```bash
# Access PostgreSQL
sudo -u postgres psql

# Connect to newsHub database
sudo -u postgres psql newshub_db

# Backup database
sudo -u postgres pg_dump newshub_db > backup_$(date +%Y%m%d).sql

# Restore database
sudo -u postgres psql newshub_db < backup_20260204.sql
```

### Django Management
```bash
# Activate virtual environment
cd /var/www/newshub
source venv/bin/activate

# Create superuser
cd backend
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

---

## 🔒 Setting Up SSL (HTTPS)

After domain is pointed to your EC2 IP:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Domain Configuration

### Update DNS Records
Point your domain to EC2 Elastic IP:

1. **Get Elastic IP** (AWS Console)
   - Allocate new Elastic IP
   - Associate with your EC2 instance

2. **Update DNS** (Your domain registrar)
   ```
   A Record: yourdomain.com → YOUR_ELASTIC_IP
   A Record: www.yourdomain.com → YOUR_ELASTIC_IP
   ```

3. **Update Django Settings**
   ```bash
   cd /var/www/newshub/backend
   nano .env
   
   # Update these lines:
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

4. **Restart Services**
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl reload nginx
   ```

---

## 📧 Email Configuration

Update email settings in `.env`:

```bash
cd /var/www/newshub/backend
nano .env
```

Add/update:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

For Gmail:
1. Enable 2-factor authentication
2. Generate App Password
3. Use app password in EMAIL_HOST_PASSWORD

---

## 🐛 Troubleshooting

### 502 Bad Gateway
```bash
# Check Gunicorn is running
sudo systemctl status gunicorn

# Check socket file exists
ls -la /run/gunicorn.sock

# Restart Gunicorn
sudo systemctl restart gunicorn
```

### Static Files Not Loading
```bash
cd /var/www/newshub/backend
source ../venv/bin/activate
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data staticfiles/
```

### Database Connection Errors
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify database exists
sudo -u postgres psql -l | grep newshub_db

# Check .env database settings
cat /var/www/newshub/backend/.env
```

### Permission Denied Errors
```bash
cd /var/www/newshub
sudo chown -R ubuntu:www-data .
sudo chmod -R 755 .
sudo chown -R www-data:www-data backend/media
sudo chown -R www-data:www-data backend/staticfiles
```

---

## 🔐 Security Checklist

After deployment:

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY in .env
- [ ] Configure firewall (UFW)
- [ ] Install Fail2Ban
- [ ] Set up SSL certificate
- [ ] Configure secure headers
- [ ] Enable DEBUG=False
- [ ] Set up regular backups
- [ ] Monitor server logs
- [ ] Update security groups
- [ ] Configure email alerts
- [ ] Set up monitoring (optional)

---

## 📊 Monitoring & Maintenance

### Automated Backups
Add to crontab (`crontab -e`):

```bash
# Daily database backup at 2 AM
0 2 * * * sudo -u postgres pg_dump newshub_db > /var/backups/newshub_$(date +\%Y\%m\%d).sql

# Weekly cleanup of old backups (keep last 30 days)
0 3 * * 0 find /var/backups -name "newshub_*.sql" -mtime +30 -delete

# Clear Django sessions weekly
0 4 * * 0 cd /var/www/newshub/backend && /var/www/newshub/venv/bin/python manage.py clearsessions
```

### Server Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Check disk space
df -h

# Check memory usage
free -h

# Check system load
htop
```

---

## 📞 Support

- **GitHub Repository**: https://github.com/SaketSinghRajput/abdnews.git
- **Issues**: https://github.com/SaketSinghRajput/abdnews/issues
- **Documentation**: See AWS_DEPLOYMENT_GUIDE.md

---

## 📝 License

[Your License Here]

---

**Happy Deploying! 🚀**
