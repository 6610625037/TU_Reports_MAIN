# TU REPORT - Deployment Guide

**Project:** TU Maintenance Ticket System
**Version:** 1.0
**Last Updated:** 2025-11-02

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Production Deployment](#production-deployment)
4. [WebSocket Configuration](#websocket-configuration)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Running the Application](#running-the-application)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Python 3.9+**
- **PostgreSQL 14+** with **PostGIS 3+** extension
- **Redis 6+** (for production WebSocket)
- **GDAL/GEOS** (for GeoDjango)
  - Windows: Install via [OSGeo4W](https://trac.osgeo.org/osgeo4w/) or [QGIS](https://qgis.org/)
  - Linux: `sudo apt-get install gdal-bin libgdal-dev`
  - macOS: `brew install gdal`

### Optional (Production)
- **Nginx** - Reverse proxy
- **Systemd** - Process manager
- **Let's Encrypt** - SSL certificates

---

## 💻 Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd PROJECT
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` File
Create `.env` in project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development - SQLite)
USE_SQLITE=True

# Database (Production - PostgreSQL)
# USE_SQLITE=False
# DB_NAME=tu_report_db
# DB_USER=tu_report_user
# DB_PASSWORD=secure_password_here
# DB_HOST=localhost
# DB_PORT=5432

# Redis (Production)
# REDIS_HOST=localhost
# REDIS_PORT=6379
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Load Initial Data
```bash
# Load categories
python manage.py loaddata categories.json

# Or create manually via admin
```

### 8. Run Development Server
```bash
# Standard Django server (HTTP only)
python manage.py runserver

# OR Daphne (with WebSocket support)
daphne -b 127.0.0.1 -p 8000 tu_report.asgi:application
```

Visit: http://localhost:8000

---

## 🚀 Production Deployment

### 1. Server Setup (Ubuntu 22.04)

#### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

#### Install Dependencies
```bash
# Python and PostgreSQL
sudo apt install python3.9 python3-pip python3-venv postgresql postgresql-contrib postgis -y

# GDAL for GeoDjango
sudo apt install gdal-bin libgdal-dev -y

# Redis
sudo apt install redis-server -y

# Nginx
sudo apt install nginx -y
```

### 2. Database Setup

#### Create PostgreSQL Database
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE tu_report_db;
CREATE USER tu_report_user WITH PASSWORD 'secure_password_here';
ALTER ROLE tu_report_user SET client_encoding TO 'utf8';
ALTER ROLE tu_report_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tu_report_user SET timezone TO 'Asia/Bangkok';
GRANT ALL PRIVILEGES ON DATABASE tu_report_db TO tu_report_user;

# Enable PostGIS
\c tu_report_db
CREATE EXTENSION postgis;
\q
```

### 3. Application Setup

#### Create Application Directory
```bash
sudo mkdir -p /var/www/tu_report
sudo chown $USER:$USER /var/www/tu_report
cd /var/www/tu_report
```

#### Clone and Setup
```bash
git clone <repository-url> .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Configure Production Settings
Edit `.env`:
```env
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

USE_SQLITE=False
DB_NAME=tu_report_db
DB_USER=tu_report_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
```

#### Update settings.py for Redis Channel Layer
Edit `tu_report/settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

#### Run Migrations and Collect Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 4. Systemd Service Configuration

#### Create Daphne Service
Create `/etc/systemd/system/tu_report_daphne.service`:

```ini
[Unit]
Description=TU Report Daphne (ASGI/WebSocket)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/tu_report
Environment="PATH=/var/www/tu_report/venv/bin"
ExecStart=/var/www/tu_report/venv/bin/daphne -b 127.0.0.1 -p 8000 tu_report.asgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable tu_report_daphne
sudo systemctl start tu_report_daphne
sudo systemctl status tu_report_daphne
```

### 5. Nginx Configuration

#### Create Nginx Config
Create `/etc/nginx/sites-available/tu_report`:

```nginx
upstream tu_report {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 20M;

    location / {
        proxy_pass http://tu_report;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws/ {
        proxy_pass http://tu_report;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    location /static/ {
        alias /var/www/tu_report/staticfiles/;
    }

    location /media/ {
        alias /var/www/tu_report/media/;
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/tu_report /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Certbot will auto-configure Nginx for HTTPS.

---

## ⚡ WebSocket Configuration

### Development
Uses `InMemoryChannelLayer` - no additional setup needed.

### Production
Uses `Redis` for channel layer:

1. **Install Redis:**
```bash
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

2. **Update settings.py:**
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

3. **Test Connection:**
```bash
redis-cli ping
# Should return: PONG
```

---

## 🗄️ Database Setup

### SQLite (Development Only)
Set in `.env`:
```env
USE_SQLITE=True
```

**Note:** SQLite does NOT support GeoDjango. GPS features will be disabled.

### PostgreSQL + PostGIS (Recommended for Production)

#### Install PostGIS Extension
```bash
sudo -u postgres psql tu_report_db -c "CREATE EXTENSION postgis;"
```

#### Verify Installation
```bash
sudo -u postgres psql tu_report_db -c "SELECT PostGIS_Version();"
```

#### Backup Database
```bash
pg_dump -U tu_report_user tu_report_db > backup.sql
```

#### Restore Database
```bash
psql -U tu_report_user tu_report_db < backup.sql
```

---

## 🔑 Environment Variables

### Complete `.env` Example (Production)

```env
# Django
SECRET_KEY=<generate-with-django-get-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
USE_SQLITE=False
DB_NAME=tu_report_db
DB_USER=tu_report_user
DB_PASSWORD=<strong-password>
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Generate Secret Key
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🏃 Running the Application

### Development
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run with WebSocket support
daphne -b 0.0.0.0 -p 8000 tu_report.asgi:application

# OR standard Django server (no WebSocket)
python manage.py runserver
```

### Production (Systemd)
```bash
# Start
sudo systemctl start tu_report_daphne

# Stop
sudo systemctl stop tu_report_daphne

# Restart
sudo systemctl restart tu_report_daphne

# View logs
sudo journalctl -u tu_report_daphne -f
```

---

## 🧪 Testing

### Run Tests
```bash
pytest
# OR
python manage.py test
```

### Check Coverage
```bash
coverage run -m pytest
coverage report
coverage html
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. GDAL Not Found
**Error:** `django.core.exceptions.ImproperlyConfigured: Could not find the GDAL library`

**Solution (Windows):**
- Install [OSGeo4W](https://trac.osgeo.org/osgeo4w/) or [QGIS](https://qgis.org/)
- Restart terminal
- Check `settings.py` GDAL configuration

**Solution (Linux):**
```bash
sudo apt install gdal-bin libgdal-dev
export GDAL_LIBRARY_PATH=/usr/lib/libgdal.so
```

#### 2. PostgreSQL Connection Error
**Error:** `FATAL: password authentication failed`

**Solution:**
- Check `.env` credentials
- Verify database exists: `psql -U tu_report_user -d tu_report_db`
- Check `pg_hba.conf` for proper authentication method

#### 3. Redis Connection Error
**Error:** `Error connecting to Redis`

**Solution:**
```bash
# Check Redis is running
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check port
sudo netstat -tulpn | grep 6379
```

#### 4. WebSocket Connection Failed
**Error:** `WebSocket connection failed`

**Solution:**
- Check Daphne is running: `sudo systemctl status tu_report_daphne`
- Verify Nginx WebSocket config (`Upgrade` headers)
- Check firewall allows WebSocket connections
- View logs: `sudo journalctl -u tu_report_daphne -f`

#### 5. Static Files Not Loading
**Solution:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

#### 6. Permission Denied on Media Files
**Solution:**
```bash
sudo chown -R www-data:www-data /var/www/tu_report/media/
sudo chmod -R 755 /var/www/tu_report/media/
```

---

## 📊 Monitoring

### Check Application Status
```bash
# Daphne service
sudo systemctl status tu_report_daphne

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server
```

### View Logs
```bash
# Daphne logs
sudo journalctl -u tu_report_daphne -f

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated
- [ ] Database credentials secured
- [ ] SSL certificate installed (HTTPS)
- [ ] Firewall configured (UFW)
- [ ] Regular backups scheduled
- [ ] Redis password set (if exposed)
- [ ] File upload size limits set
- [ ] CORS properly configured
- [ ] Security headers enabled (HSTS, CSP)

---

## 📝 Maintenance

### Update Application
```bash
cd /var/www/tu_report
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart tu_report_daphne
```

### Database Backup (Daily Cron)
```bash
# Add to crontab
0 2 * * * pg_dump -U tu_report_user tu_report_db > /backup/tu_report_$(date +\%Y\%m\%d).sql
```

---

## 📞 Support

For issues or questions:
- Check logs first
- Review this guide
- Check Django documentation: https://docs.djangoproject.com/
- Check Channels documentation: https://channels.readthedocs.io/

---

**System Status:** ✅ Ready for Production
**All Features:** 100% Complete
**Last Tested:** 2025-11-02
