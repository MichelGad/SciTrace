# Deployment Guide

This guide covers deploying SciTrace in production environments, including configuration, security, and monitoring considerations.

## 🚀 Deployment Options

### 1. Traditional Server Deployment

#### Prerequisites
- **Operating System**: Ubuntu 20.04+ LTS, CentOS 8+, or similar
- **Python**: Python 3.8 or higher
- **Web Server**: Nginx or Apache
- **Process Manager**: systemd, supervisor, or similar
- **Database**: PostgreSQL (recommended) or SQLite
- **SSL Certificate**: Let's Encrypt or commercial certificate

#### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB+ SSD recommended
- **Network**: Stable internet connection

### 2. Docker Deployment

#### Docker Compose Setup
```yaml
version: '3.8'

services:
  scitrace:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/scitrace
      - SECRET_KEY=your-secret-key
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=scitrace
      - POSTGRES_USER=scitrace
      - POSTGRES_PASSWORD=your-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - scitrace

volumes:
  postgres_data:
  redis_data:
```

### 3. Cloud Deployment

#### AWS Deployment
- **EC2**: Use t3.medium or larger instances
- **RDS**: PostgreSQL database service
- **S3**: File storage for datasets
- **CloudFront**: CDN for static assets
- **Route 53**: DNS management

#### Google Cloud Deployment
- **Compute Engine**: VM instances
- **Cloud SQL**: Managed PostgreSQL
- **Cloud Storage**: File storage
- **Cloud CDN**: Content delivery
- **Cloud DNS**: DNS management

#### Azure Deployment
- **Virtual Machines**: Azure VMs
- **Azure Database**: PostgreSQL service
- **Blob Storage**: File storage
- **CDN**: Content delivery network
- **DNS**: Azure DNS

## 🔧 Production Configuration

### Environment Variables

#### Required Variables
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/scitrace

# DataLad Configuration
DATALAD_CONFIG_PATH=/opt/scitrace/datalad
DATALAD_DATASET_PATH=/opt/scitrace/datasets

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/scitrace/app.log

# Performance
WORKERS=4
TIMEOUT=30
```

#### Optional Variables
```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=True
```

### Database Configuration

#### PostgreSQL Setup
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE scitrace;
CREATE USER scitrace WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE scitrace TO scitrace;
\q
```

#### Database Migration
```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
flask db upgrade

# Create initial admin user
python -c "
from scitrace import create_app, db
from scitrace.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User(
        username='admin',
        email='admin@yourdomain.com',
        password_hash=generate_password_hash('secure-password'),
        role='admin',
        name='Administrator'
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created')
"
```

### Web Server Configuration

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /static {
        alias /opt/scitrace/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /assets {
        alias /opt/scitrace/assets;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Apache Configuration
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/cert.pem
    SSLCertificateKeyFile /etc/ssl/private/key.pem
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    ProxyPass /static /opt/scitrace/static
    ProxyPassReverse /static /opt/scitrace/static
    
    ProxyPass /assets /opt/scitrace/assets
    ProxyPassReverse /assets /opt/scitrace/assets
</VirtualHost>
```

### Process Management

#### systemd Service
```ini
[Unit]
Description=SciTrace Web Application
After=network.target postgresql.service

[Service]
Type=exec
User=scitrace
Group=scitrace
WorkingDirectory=/opt/scitrace
Environment=PATH=/opt/scitrace/venv/bin
ExecStart=/opt/scitrace/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 30 --access-logfile /var/log/scitrace/access.log --error-logfile /var/log/scitrace/error.log scitrace:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Supervisor Configuration
```ini
[program:scitrace]
command=/opt/scitrace/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 30 scitrace:app
directory=/opt/scitrace
user=scitrace
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/scitrace/supervisor.log
```

## 🔐 Security Configuration

### SSL/TLS Setup

#### Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Manual SSL Certificate
```bash
# Generate private key
openssl genrsa -out key.pem 2048

# Generate certificate signing request
openssl req -new -key key.pem -out csr.pem

# Generate self-signed certificate (for testing)
openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem
```

### Security Headers
```python
# In your Flask app configuration
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, {
    'force_https': True,
    'strict_transport_security': True,
    'strict_transport_security_max_age': 31536000,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self' https://fonts.gstatic.com",
    }
})
```

### Firewall Configuration
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5000/tcp  # Block direct access to Flask

# iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 5000 -j DROP
```

## 📊 Monitoring and Logging

### Application Logging
```python
# In your Flask app
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/scitrace.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SciTrace startup')
```

### System Monitoring

#### Prometheus Metrics
```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
metrics.info('scitrace_info', 'SciTrace application info', version='0.1.0')
```

#### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '0.1.0'
    })
```

### Log Rotation
```bash
# /etc/logrotate.d/scitrace
/var/log/scitrace/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 scitrace scitrace
    postrotate
        systemctl reload scitrace
    endscript
}
```

## 🔄 Backup and Recovery

### Database Backup
```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/opt/backups/scitrace"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scitrace_$DATE.sql"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U scitrace scitrace > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### File System Backup
```bash
#!/bin/bash
# backup_files.sh

BACKUP_DIR="/opt/backups/scitrace"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/scitrace_files_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

tar -czf $BACKUP_FILE /opt/scitrace/datasets /opt/scitrace/static

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Automated Backup
```bash
# Add to crontab
0 2 * * * /opt/scitrace/scripts/backup_db.sh
0 3 * * * /opt/scitrace/scripts/backup_files.sh
```

## 🚀 Deployment Scripts

### Production Deployment Script
```bash
#!/bin/bash
# deploy.sh

set -e

echo "Starting SciTrace deployment..."

# Update code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Collect static files
python -c "from scitrace import create_app; app = create_app(); app.app_context().push()"

# Restart services
sudo systemctl restart scitrace
sudo systemctl restart nginx

# Check status
sudo systemctl status scitrace
sudo systemctl status nginx

echo "Deployment completed successfully!"
```

### Rollback Script
```bash
#!/bin/bash
# rollback.sh

set -e

echo "Rolling back SciTrace..."

# Get previous commit
PREVIOUS_COMMIT=$(git log --oneline -n 2 | tail -1 | cut -d' ' -f1)

# Reset to previous commit
git reset --hard $PREVIOUS_COMMIT

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Restart services
sudo systemctl restart scitrace

echo "Rollback completed successfully!"
```

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo journalctl -u scitrace -f

# Check configuration
python -c "from scitrace import create_app; app = create_app(); print('Config OK')"

# Check database connection
python -c "from scitrace import create_app, db; app = create_app(); app.app_context().push(); db.engine.execute('SELECT 1')"
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U scitrace -d scitrace -c "SELECT 1"

# Check database permissions
psql -h localhost -U scitrace -d scitrace -c "\l"
```

#### Performance Issues
```bash
# Check system resources
htop
df -h
free -h

# Check application logs
tail -f /var/log/scitrace/error.log

# Check database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Monitoring Commands
```bash
# Check service status
sudo systemctl status scitrace nginx postgresql

# Check logs
sudo journalctl -u scitrace --since "1 hour ago"
tail -f /var/log/scitrace/access.log

# Check disk usage
df -h
du -sh /opt/scitrace/datasets/*

# Check memory usage
free -h
ps aux --sort=-%mem | head
```

---

**Need help with deployment?** Check out the [Troubleshooting Guide](../troubleshooting/README.md) for common issues, or explore the [Configuration Guide](configuration.md) for detailed configuration options.
