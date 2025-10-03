# Configuration Guide

This guide covers all configuration options for SciTrace, including environment variables, configuration files, and deployment settings.

## ⚙️ Configuration Overview

SciTrace uses a flexible configuration system that supports multiple environments (development, testing, production) with environment-specific settings.

## 🔧 Configuration Architecture

### Configuration Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                Configuration Hierarchy                      │
├─────────────────────────────────────────────────────────────┤
│  1. Environment Variables (Highest Priority)               │
│     ├── Production secrets                                  │
│     ├── Database credentials                                │
│     └── API keys                                           │
├─────────────────────────────────────────────────────────────┤
│  2. Configuration Files                                    │
│     ├── config/production.py                               │
│     ├── config/development.py                              │
│     └── config/testing.py                                  │
├─────────────────────────────────────────────────────────────┤
│  3. Default Settings (Lowest Priority)                     │
│     ├── Base configuration                                  │
│     ├── Default values                                      │
│     └── Fallback settings                                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Configuration Files

### Base Configuration

#### `config/config.py`
```python
import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/scitrace.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'timeout': 20
        }
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'json', 'py', 'r', 'md'}
    
    # DataLad configuration
    DATALAD_PATH = os.environ.get('DATALAD_PATH', '/usr/local/bin/datalad')
    DATALAD_TIMEOUT = 300  # 5 minutes
    
    # Git configuration
    GIT_PATH = os.environ.get('GIT_PATH', '/usr/bin/git')
    GIT_TIMEOUT = 60  # 1 minute
    
    # Security settings
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGITS = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per minute"
    
    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/scitrace.log')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Monitoring
    MONITORING_ENABLED = os.environ.get('MONITORING_ENABLED', 'false').lower() in ['true', 'on', '1']
    METRICS_ENDPOINT = os.environ.get('METRICS_ENDPOINT', '/metrics')
    
    # API configuration
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '1000 per hour')
    API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 30))
    
    # Data retention
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 365))
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', 30))
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass
```

### Environment-Specific Configuration

#### Development Configuration
```python
# config/development.py
from .config import Config

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Development database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/scitrace_dev.db'
    
    # Relaxed security for development
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Development-specific settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Logging for development
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/scitrace_dev.log'
    
    # Development tools
    FLASK_DEBUG_TOOLBAR = True
    FLASK_DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Caching disabled for development
    CACHE_TYPE = 'null'
    
    # Rate limiting relaxed
    RATELIMIT_DEFAULT = "1000 per minute"
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Enable debug toolbar in development
        if app.debug:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
```

#### Production Configuration
```python
# config/production.py
from .config import Config
import os

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Production logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/scitrace/scitrace.log')
    
    # Production caching
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    if not CACHE_REDIS_URL:
        raise ValueError("REDIS_URL environment variable is required for production")
    
    # Production rate limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    
    # Production monitoring
    MONITORING_ENABLED = True
    METRICS_ENDPOINT = '/metrics'
    
    # Production email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Production data retention
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 2555))  # 7 years
    LOG_RETENTION_DAYS = int(os.environ.get('LOG_RETENTION_DAYS', 90))
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # File logging
            if not os.path.exists(os.path.dirname(ProductionConfig.LOG_FILE)):
                os.makedirs(os.path.dirname(ProductionConfig.LOG_FILE))
            
            file_handler = RotatingFileHandler(
                ProductionConfig.LOG_FILE,
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.WARNING)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.WARNING)
            app.logger.info('SciTrace production startup')
```

#### Testing Configuration
```python
# config/testing.py
from .config import Config
import tempfile
import os

class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = False
    TESTING = True
    
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Testing-specific settings
    LOG_LEVEL = 'ERROR'
    LOG_FILE = None
    
    # Disable caching for testing
    CACHE_TYPE = 'null'
    
    # Disable rate limiting for testing
    RATELIMIT_DEFAULT = "10000 per minute"
    
    # Testing data retention
    DATA_RETENTION_DAYS = 1
    LOG_RETENTION_DAYS = 1
    
    # Temporary directories for testing
    UPLOAD_FOLDER = tempfile.mkdtemp()
    DATALAD_PATH = '/bin/true'  # Mock DataLad for testing
    GIT_PATH = '/bin/true'  # Mock Git for testing
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Testing-specific initialization
        import tempfile
        import shutil
        
        # Create temporary directories
        app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
        app.config['DATALAD_PATH'] = '/bin/true'
        app.config['GIT_PATH'] = '/bin/true'
        
        # Cleanup function
        def cleanup():
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                shutil.rmtree(app.config['UPLOAD_FOLDER'])
        
        import atexit
        atexit.register(cleanup)
```

## 🌍 Environment Variables

### Required Environment Variables

#### Production Environment
```bash
# Database
export DATABASE_URL="postgresql://user:password@localhost:5432/scitrace"
export REDIS_URL="redis://localhost:6379/0"

# Security
export SECRET_KEY="your-secret-key-here"
export SESSION_SECRET="your-session-secret-here"

# Email
export MAIL_SERVER="smtp.gmail.com"
export MAIL_PORT="587"
export MAIL_USERNAME="your-email@gmail.com"
export MAIL_PASSWORD="your-app-password"
export MAIL_DEFAULT_SENDER="SciTrace <noreply@scitrace.org>"

# Monitoring
export MONITORING_ENABLED="true"
export LOG_LEVEL="WARNING"
export LOG_FILE="/var/log/scitrace/scitrace.log"

# DataLad and Git
export DATALAD_PATH="/usr/local/bin/datalad"
export GIT_PATH="/usr/bin/git"

# API Configuration
export API_RATE_LIMIT="100 per minute"
export API_TIMEOUT="30"

# Data Retention
export DATA_RETENTION_DAYS="2555"
export LOG_RETENTION_DAYS="90"
```

#### Development Environment
```bash
# Database
export DATABASE_URL="sqlite:///instance/scitrace_dev.db"

# Security (use different keys for development)
export SECRET_KEY="dev-secret-key"
export SESSION_SECRET="dev-session-secret"

# Logging
export LOG_LEVEL="DEBUG"
export LOG_FILE="logs/scitrace_dev.log"

# Development tools
export FLASK_DEBUG="1"
export FLASK_ENV="development"
```

### Optional Environment Variables

#### Advanced Configuration
```bash
# Caching
export CACHE_TYPE="redis"
export CACHE_REDIS_URL="redis://localhost:6379/1"
export CACHE_DEFAULT_TIMEOUT="300"

# File Upload
export MAX_CONTENT_LENGTH="104857600"  # 100MB
export UPLOAD_FOLDER="uploads"
export ALLOWED_EXTENSIONS="txt,csv,json,py,r,md"

# Security
export PASSWORD_MIN_LENGTH="8"
export PASSWORD_REQUIRE_UPPERCASE="true"
export PASSWORD_REQUIRE_LOWERCASE="true"
export PASSWORD_REQUIRE_DIGITS="true"
export PASSWORD_REQUIRE_SPECIAL="true"

# Session
export PERMANENT_SESSION_LIFETIME="28800"  # 8 hours
export SESSION_COOKIE_SECURE="true"
export SESSION_COOKIE_HTTPONLY="true"
export SESSION_COOKIE_SAMESITE="Lax"

# Rate Limiting
export RATELIMIT_DEFAULT="100 per minute"
export RATELIMIT_STORAGE_URL="redis://localhost:6379/2"

# DataLad Configuration
export DATALAD_TIMEOUT="300"
export DATALAD_CONFIG_PATH="/etc/datalad/config"

# Git Configuration
export GIT_TIMEOUT="60"
export GIT_CONFIG_PATH="/etc/gitconfig"

# Monitoring
export METRICS_ENDPOINT="/metrics"
export HEALTH_CHECK_ENDPOINT="/health"

# Backup
export BACKUP_ENABLED="true"
export BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
export BACKUP_RETENTION_DAYS="30"
export BACKUP_STORAGE_PATH="/backups/scitrace"
```

## 📋 Configuration Management

### Configuration Loading

#### Application Factory Pattern
```python
# app.py
from flask import Flask
from config import config

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    from extensions import db, login_manager, cache, limiter
    db.init_app(app)
    login_manager.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    
    # Register blueprints
    from routes import auth, dashboard, projects, dataflow, tasks, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(dataflow.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(api.bp)
    
    return app

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
```

#### Environment Detection
```python
# config/settings.py
import os

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

def validate_config(config):
    """Validate configuration settings"""
    errors = []
    
    # Check required settings
    if not config.SECRET_KEY or config.SECRET_KEY == 'dev-secret-key-change-in-production':
        errors.append("SECRET_KEY must be set to a secure value")
    
    if config.SQLALCHEMY_DATABASE_URI.startswith('sqlite') and env == 'production':
        errors.append("SQLite database not recommended for production")
    
    if not config.MAIL_SERVER and env == 'production':
        errors.append("MAIL_SERVER must be configured for production")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True
```

### Configuration Validation

#### Settings Validation
```python
# config/validation.py
import os
import re
from urllib.parse import urlparse

class ConfigValidator:
    @staticmethod
    def validate_database_url(url):
        """Validate database URL format"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                return False, "Database URL must include scheme (sqlite://, postgresql://, etc.)"
            
            if parsed.scheme not in ['sqlite', 'postgresql', 'mysql']:
                return False, f"Unsupported database scheme: {parsed.scheme}"
            
            return True, "Valid database URL"
        except Exception as e:
            return False, f"Invalid database URL: {str(e)}"
    
    @staticmethod
    def validate_redis_url(url):
        """Validate Redis URL format"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['redis', 'rediss']:
                return False, "Redis URL must use redis:// or rediss:// scheme"
            return True, "Valid Redis URL"
        except Exception as e:
            return False, f"Invalid Redis URL: {str(e)}"
    
    @staticmethod
    def validate_email_config(config):
        """Validate email configuration"""
        if not config.MAIL_SERVER:
            return False, "MAIL_SERVER is required"
        
        if not config.MAIL_USERNAME:
            return False, "MAIL_USERNAME is required"
        
        if not config.MAIL_PASSWORD:
            return False, "MAIL_PASSWORD is required"
        
        if not config.MAIL_DEFAULT_SENDER:
            return False, "MAIL_DEFAULT_SENDER is required"
        
        return True, "Valid email configuration"
    
    @staticmethod
    def validate_security_settings(config):
        """Validate security settings"""
        if not config.SECRET_KEY or len(config.SECRET_KEY) < 32:
            return False, "SECRET_KEY must be at least 32 characters"
        
        if config.SECRET_KEY == 'dev-secret-key-change-in-production':
            return False, "SECRET_KEY must be changed from default value"
        
        if not config.SESSION_COOKIE_SECURE and os.environ.get('FLASK_ENV') == 'production':
            return False, "SESSION_COOKIE_SECURE must be True in production"
        
        return True, "Valid security settings"
    
    @classmethod
    def validate_all(cls, config):
        """Validate all configuration settings"""
        errors = []
        
        # Validate database
        is_valid, message = cls.validate_database_url(config.SQLALCHEMY_DATABASE_URI)
        if not is_valid:
            errors.append(message)
        
        # Validate Redis (if configured)
        if config.CACHE_TYPE == 'redis' and config.CACHE_REDIS_URL:
            is_valid, message = cls.validate_redis_url(config.CACHE_REDIS_URL)
            if not is_valid:
                errors.append(message)
        
        # Validate email
        if os.environ.get('FLASK_ENV') == 'production':
            is_valid, message = cls.validate_email_config(config)
            if not is_valid:
                errors.append(message)
        
        # Validate security
        is_valid, message = cls.validate_security_settings(config)
        if not is_valid:
            errors.append(message)
        
        return len(errors) == 0, errors
```

## 🔧 Runtime Configuration

### Dynamic Configuration

#### Configuration Updates
```python
# config/dynamic.py
import json
import os
from datetime import datetime

class DynamicConfig:
    def __init__(self, app):
        self.app = app
        self.config_file = os.path.join(app.instance_path, 'dynamic_config.json')
        self.load_config()
    
    def load_config(self):
        """Load dynamic configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.app.config.update(config_data)
            except Exception as e:
                self.app.logger.error(f"Failed to load dynamic config: {e}")
    
    def save_config(self, config_data):
        """Save dynamic configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            self.app.config.update(config_data)
            return True
        except Exception as e:
            self.app.logger.error(f"Failed to save dynamic config: {e}")
            return False
    
    def update_setting(self, key, value):
        """Update a single configuration setting"""
        config_data = self.get_all_settings()
        config_data[key] = value
        return self.save_config(config_data)
    
    def get_all_settings(self):
        """Get all current configuration settings"""
        return {
            'api_rate_limit': self.app.config.get('API_RATE_LIMIT'),
            'session_timeout': self.app.config.get('PERMANENT_SESSION_LIFETIME'),
            'max_file_size': self.app.config.get('MAX_CONTENT_LENGTH'),
            'data_retention_days': self.app.config.get('DATA_RETENTION_DAYS'),
            'log_retention_days': self.app.config.get('LOG_RETENTION_DAYS')
        }

# API endpoint for configuration management
@app.route('/api/admin/config', methods=['GET', 'POST'])
@require_permission(Permission.ADMIN_SYSTEM)
def manage_config():
    """Manage application configuration"""
    if request.method == 'GET':
        return jsonify(dynamic_config.get_all_settings())
    
    elif request.method == 'POST':
        config_data = request.json
        if dynamic_config.save_config(config_data):
            return jsonify({'success': True, 'message': 'Configuration updated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to update configuration'}), 500
```

### Configuration Templates

#### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  scitrace:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://scitrace:password@db:5432/scitrace
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - MAIL_SERVER=${MAIL_SERVER}
      - MAIL_USERNAME=${MAIL_USERNAME}
      - MAIL_PASSWORD=${MAIL_PASSWORD}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=scitrace
      - POSTGRES_USER=scitrace
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### Kubernetes Configuration
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scitrace-config
data:
  FLASK_ENV: "production"
  LOG_LEVEL: "WARNING"
  API_RATE_LIMIT: "100 per minute"
  DATA_RETENTION_DAYS: "2555"
  LOG_RETENTION_DAYS: "90"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: scitrace-secrets
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  DATABASE_URL: <base64-encoded-db-url>
  REDIS_URL: <base64-encoded-redis-url>
  MAIL_PASSWORD: <base64-encoded-mail-password>
```

## 📊 Configuration Monitoring

### Configuration Health Check

#### Settings Validation Endpoint
```python
@app.route('/health/config', methods=['GET'])
def config_health_check():
    """Configuration health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Check database configuration
    try:
        db.session.execute('SELECT 1')
        health_status['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check Redis configuration
    if app.config.get('CACHE_TYPE') == 'redis':
        try:
            cache.get('health_check')
            health_status['checks']['redis'] = {'status': 'healthy'}
        except Exception as e:
            health_status['checks']['redis'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_status['status'] = 'unhealthy'
    
    # Check file system permissions
    try:
        test_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test.txt')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        health_status['checks']['filesystem'] = {'status': 'healthy'}
    except Exception as e:
        health_status['checks']['filesystem'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check external dependencies
    try:
        subprocess.run([app.config['DATALAD_PATH'], '--version'], 
                      capture_output=True, timeout=10)
        health_status['checks']['datalad'] = {'status': 'healthy'}
    except Exception as e:
        health_status['checks']['datalad'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    return jsonify(health_status)
```

## 📋 Configuration Checklist

### Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] Redis connection tested (if used)
- [ ] Email configuration tested
- [ ] Security settings validated
- [ ] File upload settings configured
- [ ] Logging configuration tested
- [ ] Monitoring configuration enabled
- [ ] Backup configuration set up
- [ ] SSL/TLS certificates configured

### Production Checklist

- [ ] Production configuration loaded
- [ ] Environment variables secured
- [ ] Database credentials secured
- [ ] API keys and secrets secured
- [ ] Monitoring configuration active
- [ ] Logging configuration optimized
- [ ] Performance settings tuned
- [ ] Security settings hardened
- [ ] Backup procedures tested
- [ ] Configuration documentation updated

---

**Need help with configuration?** Check out the [Deployment Guide](README.md) for production setup, or explore the [Troubleshooting Guide](../troubleshooting/README.md) for configuration-related issues.
