# Security Guide

This guide covers security best practices, threat mitigation, and security configuration for SciTrace in production environments.

## 🔒 Security Overview

SciTrace handles sensitive research data and requires robust security measures. This guide covers authentication, authorization, data protection, and security monitoring.

## 🛡️ Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Architecture                   │
├─────────────────────────────────────────────────────────────┤
│  Network Security                                          │
│  ├── HTTPS/TLS Encryption                                  │
│  ├── Firewall Configuration                                │
│  ├── VPN Access Control                                     │
│  └── DDoS Protection                                        │
├─────────────────────────────────────────────────────────────┤
│  Application Security                                       │
│  ├── Authentication & Authorization                        │
│  ├── Input Validation & Sanitization                       │
│  ├── Session Management                                     │
│  └── API Security                                           │
├─────────────────────────────────────────────────────────────┤
│  Data Security                                             │
│  ├── Database Encryption                                    │
│  ├── File System Encryption                                │
│  ├── Backup Security                                        │
│  └── Data Classification                                    │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Security                                    │
│  ├── Server Hardening                                       │
│  ├── Access Control                                         │
│  ├── Monitoring & Logging                                   │
│  └── Incident Response                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Authentication & Authorization

### User Authentication

#### Password Security
```python
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

class UserSecurity:
    @staticmethod
    def hash_password(password):
        """Hash password with salt"""
        return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify password against hash"""
        return check_password_hash(password_hash, password)
    
    @staticmethod
    def generate_secure_password(length=12):
        """Generate secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain digit"
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain special character"
        
        return True, "Password is secure"

# Usage in user model
class User(db.Model):
    def set_password(self, password):
        """Set password with security validation"""
        is_valid, message = UserSecurity.validate_password_strength(password)
        if not is_valid:
            raise ValueError(message)
        
        self.password_hash = UserSecurity.hash_password(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return UserSecurity.verify_password(self.password_hash, password)
```

#### Session Security
```python
from flask_login import LoginManager, UserMixin
from flask import session
import secrets

# Configure secure session
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # Prevent XSS
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8)  # Session timeout
)

# Session management
class SecureSession:
    @staticmethod
    def create_session(user_id):
        """Create secure session"""
        session['user_id'] = user_id
        session['session_id'] = secrets.token_hex(32)
        session['created_at'] = datetime.utcnow().isoformat()
        session['last_activity'] = datetime.utcnow().isoformat()
        session.permanent = True
    
    @staticmethod
    def validate_session():
        """Validate session security"""
        if 'user_id' not in session:
            return False
        
        # Check session timeout
        last_activity = datetime.fromisoformat(session.get('last_activity', '1970-01-01'))
        if datetime.utcnow() - last_activity > timedelta(hours=8):
            session.clear()
            return False
        
        # Update last activity
        session['last_activity'] = datetime.utcnow().isoformat()
        return True
    
    @staticmethod
    def destroy_session():
        """Securely destroy session"""
        session.clear()
```

### Role-Based Access Control

#### Permission System
```python
class Permission:
    READ_PROJECT = 'read_project'
    WRITE_PROJECT = 'write_project'
    DELETE_PROJECT = 'delete_project'
    ADMIN_USERS = 'admin_users'
    ADMIN_SYSTEM = 'admin_system'

class Role:
    USER = 'user'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

# Role permissions mapping
ROLE_PERMISSIONS = {
    Role.USER: [
        Permission.READ_PROJECT,
        Permission.WRITE_PROJECT
    ],
    Role.ADMIN: [
        Permission.READ_PROJECT,
        Permission.WRITE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.ADMIN_USERS
    ],
    Role.SUPER_ADMIN: [
        Permission.READ_PROJECT,
        Permission.WRITE_PROJECT,
        Permission.DELETE_PROJECT,
        Permission.ADMIN_USERS,
        Permission.ADMIN_SYSTEM
    ]
}

class User(db.Model):
    role = db.Column(db.String(20), default=Role.USER)
    
    def has_permission(self, permission):
        """Check if user has specific permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, [])
    
    def can_access_project(self, project):
        """Check if user can access specific project"""
        if self.role in [Role.ADMIN, Role.SUPER_ADMIN]:
            return True
        return project.user_id == self.id

# Permission decorator
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.has_permission(permission):
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

## 🛡️ Input Validation & Sanitization

### Data Validation

#### Input Sanitization
```python
import bleach
import re
from marshmallow import Schema, fields, validate, ValidationError

class SecurityValidator:
    @staticmethod
    def sanitize_html(text):
        """Sanitize HTML content"""
        if not text:
            return ""
        
        # Allowed HTML tags and attributes
        allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
        allowed_attributes = {}
        
        return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes)
    
    @staticmethod
    def validate_file_path(path):
        """Validate file path to prevent directory traversal"""
        # Normalize path
        normalized_path = os.path.normpath(path)
        
        # Check for directory traversal attempts
        if '..' in normalized_path or normalized_path.startswith('/'):
            raise ValueError("Invalid file path")
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in normalized_path for char in dangerous_chars):
            raise ValueError("Invalid characters in file path")
        
        return normalized_path
    
    @staticmethod
    def validate_project_name(name):
        """Validate project name"""
        if not name or len(name.strip()) < 3:
            raise ValueError("Project name must be at least 3 characters")
        
        if len(name) > 100:
            raise ValueError("Project name too long")
        
        # Only allow alphanumeric, spaces, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            raise ValueError("Project name contains invalid characters")
        
        return name.strip()

# Schema validation
class ProjectSchema(Schema):
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=100),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_]+$', error="Invalid characters")
        ]
    )
    description = fields.Str(
        validate=validate.Length(max=500)
    )
    research_type = fields.Str(
        required=True,
        validate=validate.OneOf(['environmental', 'biomedical', 'computational'])
    )
    
    def validate_name(self, value):
        """Custom validation for project name"""
        return SecurityValidator.validate_project_name(value)
```

### SQL Injection Prevention

#### Parameterized Queries
```python
# Always use parameterized queries
def get_project_by_id(project_id):
    """Safe database query"""
    return Project.query.get(project_id)

def get_user_projects(user_id, limit=10):
    """Safe query with parameters"""
    return Project.query.filter_by(user_id=user_id).limit(limit).all()

# Never do this (vulnerable to SQL injection)
def unsafe_query(user_input):
    # DON'T DO THIS
    query = f"SELECT * FROM projects WHERE name = '{user_input}'"
    return db.session.execute(query)

# Do this instead
def safe_query(project_name):
    return Project.query.filter_by(name=project_name).first()
```

#### Database Security
```python
# Database connection security
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    # Additional security settings
    SQLALCHEMY_ENGINE_OPTIONS={
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'connect_args': {
            'sslmode': 'require'  # For PostgreSQL
        }
    }
)
```

## 🔒 Data Protection

### Encryption at Rest

#### Database Encryption
```python
# For SQLite with encryption
import sqlcipher3

def create_encrypted_database():
    """Create encrypted SQLite database"""
    conn = sqlcipher3.connect('instance/scitrace_encrypted.db')
    conn.execute("PRAGMA key = 'your-encryption-key'")
    conn.execute("PRAGMA cipher_page_size = 4096")
    conn.execute("PRAGMA kdf_iter = 64000")
    conn.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA1")
    conn.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA1")
    return conn

# For PostgreSQL with encryption
# Use pgcrypto extension
def setup_database_encryption():
    """Setup database encryption"""
    db.session.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    db.session.commit()
```

#### File System Encryption
```python
import cryptography
from cryptography.fernet import Fernet
import os

class FileEncryption:
    def __init__(self):
        self.key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.key)
    
    def encrypt_file(self, file_path):
        """Encrypt file content"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(f"{file_path}.enc", 'wb') as f:
            f.write(encrypted_data)
        
        return f"{file_path}.enc"
    
    def decrypt_file(self, encrypted_file_path):
        """Decrypt file content"""
        with open(encrypted_file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        original_path = encrypted_file_path.replace('.enc', '')
        with open(original_path, 'wb') as f:
            f.write(decrypted_data)
        
        return original_path

# Global encryption handler
file_encryption = FileEncryption()
```

### Data Classification

#### Data Sensitivity Levels
```python
class DataClassification:
    PUBLIC = 'public'
    INTERNAL = 'internal'
    CONFIDENTIAL = 'confidential'
    RESTRICTED = 'restricted'

class Project(db.Model):
    data_classification = db.Column(db.String(20), default=DataClassification.INTERNAL)
    
    def get_access_requirements(self):
        """Get access requirements based on classification"""
        requirements = {
            DataClassification.PUBLIC: [],
            DataClassification.INTERNAL: ['authenticated_user'],
            DataClassification.CONFIDENTIAL: ['authenticated_user', 'project_member'],
            DataClassification.RESTRICTED: ['authenticated_user', 'project_member', 'admin_approval']
        }
        return requirements.get(self.data_classification, [])
    
    def can_user_access(self, user):
        """Check if user can access based on classification"""
        requirements = self.get_access_requirements()
        
        if 'authenticated_user' in requirements and not user.is_authenticated:
            return False
        
        if 'project_member' in requirements and not self.can_user_access_project(user):
            return False
        
        if 'admin_approval' in requirements and not user.has_permission(Permission.ADMIN_SYSTEM):
            return False
        
        return True
```

## 🌐 Network Security

### HTTPS Configuration

#### SSL/TLS Setup
```python
# Flask SSL configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Nginx SSL configuration
nginx_ssl_config = """
server {
    listen 443 ssl http2;
    server_name scitrace.example.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL security settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
```

### Security Headers

#### HTTP Security Headers
```python
from flask_talisman import Talisman

# Configure security headers
Talisman(app, {
    'force_https': True,
    'strict_transport_security': True,
    'strict_transport_security_max_age': 31536000,
    'strict_transport_security_include_subdomains': True,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self'",
        'connect-src': "'self'",
        'frame-ancestors': "'none'"
    },
    'content_security_policy_nonce_in': ['script-src'],
    'referrer_policy': 'strict-origin-when-cross-origin'
})

# Additional security headers
@app.after_request
def security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

## 🔍 Security Monitoring

### Audit Logging

#### Security Event Logging
```python
import logging
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_login_attempt(self, username, ip_address, success):
        """Log login attempts"""
        self.logger.info(f"Login attempt: user={username}, ip={ip_address}, success={success}")
    
    def log_permission_denied(self, user_id, resource, action):
        """Log permission denied events"""
        self.logger.warning(f"Permission denied: user={user_id}, resource={resource}, action={action}")
    
    def log_suspicious_activity(self, user_id, activity, details):
        """Log suspicious activities"""
        self.logger.warning(f"Suspicious activity: user={user_id}, activity={activity}, details={details}")
    
    def log_data_access(self, user_id, data_type, action):
        """Log data access events"""
        self.logger.info(f"Data access: user={user_id}, data_type={data_type}, action={action}")

# Global security logger
security_logger = SecurityLogger()
```

#### Failed Login Protection
```python
from collections import defaultdict
import time

class LoginProtection:
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
    
    def record_failed_attempt(self, ip_address):
        """Record failed login attempt"""
        now = time.time()
        self.failed_attempts[ip_address].append(now)
        
        # Clean old attempts
        cutoff = now - self.lockout_duration
        self.failed_attempts[ip_address] = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt > cutoff
        ]
    
    def is_ip_locked(self, ip_address):
        """Check if IP is locked due to failed attempts"""
        now = time.time()
        recent_attempts = [
            attempt for attempt in self.failed_attempts[ip_address]
            if attempt > now - self.lockout_duration
        ]
        return len(recent_attempts) >= self.max_attempts
    
    def record_successful_login(self, ip_address):
        """Clear failed attempts on successful login"""
        self.failed_attempts[ip_address] = []

# Global login protection
login_protection = LoginProtection()

# Usage in login endpoint
@app.route('/auth/login', methods=['POST'])
def login():
    ip_address = request.remote_addr
    
    # Check if IP is locked
    if login_protection.is_ip_locked(ip_address):
        security_logger.log_suspicious_activity(
            None, 'login_attempt_locked_ip', f'IP {ip_address} is locked'
        )
        return jsonify({'error': 'Too many failed attempts'}), 429
    
    # Process login
    username = request.json.get('username')
    password = request.json.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_protection.record_successful_login(ip_address)
        security_logger.log_login_attempt(username, ip_address, True)
        login_user(user)
        return jsonify({'success': True})
    else:
        login_protection.record_failed_attempt(ip_address)
        security_logger.log_login_attempt(username, ip_address, False)
        return jsonify({'error': 'Invalid credentials'}), 401
```

### Intrusion Detection

#### Anomaly Detection
```python
class SecurityAnomalyDetector:
    def __init__(self):
        self.user_activity = defaultdict(list)
        self.suspicious_patterns = []
    
    def analyze_user_behavior(self, user_id, action, ip_address):
        """Analyze user behavior for anomalies"""
        now = datetime.utcnow()
        
        # Record activity
        self.user_activity[user_id].append({
            'action': action,
            'ip_address': ip_address,
            'timestamp': now
        })
        
        # Keep only recent activity (last 24 hours)
        cutoff = now - timedelta(hours=24)
        self.user_activity[user_id] = [
            activity for activity in self.user_activity[user_id]
            if activity['timestamp'] > cutoff
        ]
        
        # Check for anomalies
        anomalies = self.detect_anomalies(user_id)
        if anomalies:
            security_logger.log_suspicious_activity(
                user_id, 'behavioral_anomaly', anomalies
            )
    
    def detect_anomalies(self, user_id):
        """Detect behavioral anomalies"""
        activities = self.user_activity[user_id]
        if len(activities) < 5:  # Not enough data
            return []
        
        anomalies = []
        
        # Check for rapid successive actions
        recent_actions = [a for a in activities if a['timestamp'] > datetime.utcnow() - timedelta(minutes=5)]
        if len(recent_actions) > 20:
            anomalies.append('Rapid successive actions detected')
        
        # Check for unusual IP addresses
        unique_ips = set(a['ip_address'] for a in activities)
        if len(unique_ips) > 3:
            anomalies.append('Multiple IP addresses detected')
        
        # Check for unusual access patterns
        admin_actions = [a for a in activities if 'admin' in a['action']]
        if len(admin_actions) > 5 and user_id not in [u.id for u in User.query.filter_by(role='admin').all()]:
            anomalies.append('Unauthorized admin actions detected')
        
        return anomalies

# Global anomaly detector
anomaly_detector = SecurityAnomalyDetector()
```

## 🔧 Security Configuration

### Environment Security

#### Secure Configuration
```python
# Security configuration
class SecurityConfig:
    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    
    # Session security
    SESSION_TIMEOUT = 8 * 60 * 60  # 8 hours
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000
    
    # File upload security
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES = ['.csv', '.txt', '.json', '.py', '.r', '.md']
    SCAN_UPLOADS_FOR_VIRUSES = True
    
    # Database security
    DB_CONNECTION_TIMEOUT = 30
    DB_QUERY_TIMEOUT = 60
    DB_ENCRYPTION_ENABLED = True

# Apply security configuration
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY'),
    'SESSION_COOKIE_SECURE': SecurityConfig.SESSION_COOKIE_SECURE,
    'SESSION_COOKIE_HTTPONLY': SecurityConfig.SESSION_COOKIE_HTTPONLY,
    'SESSION_COOKIE_SAMESITE': SecurityConfig.SESSION_COOKIE_SAMESITE,
    'MAX_CONTENT_LENGTH': SecurityConfig.MAX_FILE_SIZE
})
```

### File Upload Security

#### Secure File Handling
```python
import magic
import hashlib

class SecureFileHandler:
    @staticmethod
    def validate_file_type(file_path):
        """Validate file type using magic numbers"""
        try:
            file_type = magic.from_file(file_path, mime=True)
            allowed_types = [
                'text/plain',
                'text/csv',
                'application/json',
                'text/x-python',
                'text/x-r',
                'text/markdown'
            ]
            return file_type in allowed_types
        except Exception:
            return False
    
    @staticmethod
    def scan_file_content(file_path):
        """Scan file content for malicious patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Read first 1KB
                
                # Check for suspicious patterns
                suspicious_patterns = [
                    r'<script',
                    r'javascript:',
                    r'eval\(',
                    r'exec\(',
                    r'import os',
                    r'subprocess',
                    r'__import__'
                ]
                
                for pattern in suspicious_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return False, f"Suspicious pattern detected: {pattern}"
                
                return True, "File content is safe"
        except Exception as e:
            return False, f"Error scanning file: {str(e)}"
    
    @staticmethod
    def generate_file_hash(file_path):
        """Generate secure hash for file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

# Secure file upload endpoint
@app.route('/api/upload', methods=['POST'])
@require_permission(Permission.WRITE_PROJECT)
def secure_file_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file size
    if len(file.read()) > SecurityConfig.MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 413
    
    file.seek(0)  # Reset file pointer
    
    # Save file temporarily
    temp_path = f"/tmp/{secrets.token_hex(16)}"
    file.save(temp_path)
    
    try:
        # Validate file type
        if not SecureFileHandler.validate_file_type(temp_path):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Scan file content
        is_safe, message = SecureFileHandler.scan_file_content(temp_path)
        if not is_safe:
            return jsonify({'error': message}), 400
        
        # Generate file hash
        file_hash = SecureFileHandler.generate_file_hash(temp_path)
        
        # Move to secure location
        secure_path = f"uploads/{file_hash}"
        os.makedirs(os.path.dirname(secure_path), exist_ok=True)
        os.rename(temp_path, secure_path)
        
        return jsonify({
            'success': True,
            'file_hash': file_hash,
            'message': 'File uploaded securely'
        })
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

## 📋 Security Checklist

### Pre-Production Security Checklist

- [ ] HTTPS/TLS configured and tested
- [ ] Security headers implemented
- [ ] Input validation and sanitization configured
- [ ] Authentication and authorization implemented
- [ ] Password security requirements enforced
- [ ] Session security configured
- [ ] Database security implemented
- [ ] File upload security configured
- [ ] Security logging enabled
- [ ] Rate limiting implemented
- [ ] Error handling secured
- [ ] Backup security configured

### Production Security Checklist

- [ ] Security monitoring active
- [ ] Intrusion detection configured
- [ ] Security incident response plan ready
- [ ] Regular security updates scheduled
- [ ] Security audit completed
- [ ] Penetration testing performed
- [ ] Security documentation updated
- [ ] Team security training completed
- [ ] Security policies documented
- [ ] Compliance requirements met

## 🆘 Security Incident Response

### Incident Response Plan

#### Security Incident Classification
```python
class SecurityIncident:
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'

class IncidentResponse:
    def __init__(self):
        self.incident_log = []
    
    def report_incident(self, incident_type, severity, description, user_id=None):
        """Report security incident"""
        incident = {
            'id': secrets.token_hex(8),
            'type': incident_type,
            'severity': severity,
            'description': description,
            'user_id': user_id,
            'timestamp': datetime.utcnow(),
            'status': 'open'
        }
        
        self.incident_log.append(incident)
        
        # Log incident
        security_logger.log_suspicious_activity(
            user_id, f"security_incident_{incident_type}", description
        )
        
        # Take immediate action based on severity
        if severity in [SecurityIncident.HIGH, SecurityIncident.CRITICAL]:
            self.take_immediate_action(incident)
        
        return incident['id']
    
    def take_immediate_action(self, incident):
        """Take immediate action for high-severity incidents"""
        if incident['type'] == 'unauthorized_access':
            # Lock affected user account
            if incident['user_id']:
                user = User.query.get(incident['user_id'])
                if user:
                    user.is_active = False
                    db.session.commit()
        
        elif incident['type'] == 'data_breach':
            # Notify administrators
            self.notify_administrators(incident)
        
        elif incident['type'] == 'system_compromise':
            # Initiate emergency procedures
            self.initiate_emergency_procedures(incident)
```

### Security Monitoring Dashboard

#### Real-time Security Monitoring
```python
@app.route('/admin/security-dashboard')
@require_permission(Permission.ADMIN_SYSTEM)
def security_dashboard():
    """Security monitoring dashboard"""
    return render_template('admin/security_dashboard.html', {
        'recent_incidents': incident_response.incident_log[-10:],
        'failed_logins': login_protection.failed_attempts,
        'security_metrics': {
            'total_incidents': len(incident_response.incident_log),
            'active_users': User.query.filter_by(is_active=True).count(),
            'locked_accounts': User.query.filter_by(is_active=False).count()
        }
    })
```

---

**Need help with security configuration?** Check out the [Deployment Guide](README.md) for production setup, or explore the [Troubleshooting Guide](../troubleshooting/README.md) for security-related issues.
