# Error Handling Guide

This guide covers SciTrace's error handling mechanisms, common error scenarios, and troubleshooting strategies for resolving issues.

## 🚨 Error Handling Overview

SciTrace implements comprehensive error handling across all layers of the application, from user interface to database operations and external integrations.

## 🔧 Error Handling Architecture

### Error Handling Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Error Handling Layers                    │
├─────────────────────────────────────────────────────────────┤
│  Frontend Error Handling (JavaScript)                      │
│  ├── Form Validation Errors                                │
│  ├── API Response Errors                                   │
│  ├── Network Connectivity Errors                           │
│  └── User Input Validation                                 │
├─────────────────────────────────────────────────────────────┤
│  Web Layer Error Handling (Flask)                         │
│  ├── HTTP Error Responses                                  │
│  ├── Route Exception Handling                              │
│  ├── Authentication Errors                                 │
│  └── Request Validation Errors                            │
├─────────────────────────────────────────────────────────────┤
│  Service Layer Error Handling (Business Logic)            │
│  ├── DataLad Operation Errors                              │
│  ├── File System Errors                                    │
│  ├── Git Operation Errors                                  │
│  └── Business Logic Validation Errors                     │
├─────────────────────────────────────────────────────────────┤
│  Data Layer Error Handling (Database)                     │
│  ├── Database Connection Errors                            │
│  ├── Query Execution Errors                                │
│  ├── Data Integrity Errors                                 │
│  └── Transaction Rollback Errors                           │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Error Categories

### 1. User Input Errors

#### Form Validation Errors
```python
# Example: Project creation validation
class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[
        DataRequired(message="Project name is required"),
        Length(min=3, max=100, message="Name must be 3-100 characters"),
        Regexp(r'^[a-zA-Z0-9\s\-_]+$', message="Invalid characters in name")
    ])
    
    research_type = SelectField('Research Type', validators=[
        DataRequired(message="Research type is required")
    ], choices=[
        ('environmental', 'Environmental'),
        ('biomedical', 'Biomedical'),
        ('computational', 'Computational')
    ])
```

#### API Validation Errors
```python
from marshmallow import Schema, fields, ValidationError

class ProjectSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=3, max=100))
    description = fields.Str(validate=Length(max=500))
    research_type = fields.Str(required=True, validate=OneOf(['environmental', 'biomedical', 'computational']))

# Usage in API endpoint
@app.route('/api/projects', methods=['POST'])
def create_project():
    try:
        data = ProjectSchema().load(request.json)
    except ValidationError as err:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': err.messages
        }), 400
```

### 2. Authentication & Authorization Errors

#### Login Errors
```python
@app.route('/auth/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        login_user(user)
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        })
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed due to server error'
        }), 500
```

#### Permission Errors
```python
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_permission(permission):
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'code': 'PERMISSION_DENIED'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route('/api/admin/reset-all', methods=['POST'])
@require_permission('admin')
def reset_all_data():
    pass
```

### 3. Database Errors

#### Connection Errors
```python
from sqlalchemy.exc import OperationalError, IntegrityError

def handle_database_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except OperationalError as e:
            app.logger.error(f"Database connection error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Database connection failed',
                'code': 'DB_CONNECTION_ERROR'
            }), 500
        except IntegrityError as e:
            app.logger.error(f"Database integrity error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Data integrity violation',
                'code': 'DB_INTEGRITY_ERROR'
            }), 400
    return decorated_function
```

#### Query Errors
```python
def safe_query(query_func, *args, **kwargs):
    try:
        return query_func(*args, **kwargs)
    except Exception as e:
        app.logger.error(f"Query error: {str(e)}")
        return None

# Usage
def get_project_by_id(project_id):
    return safe_query(
        lambda: Project.query.get_or_404(project_id)
    )
```

### 4. File System Errors

#### File Operation Errors
```python
import os
import shutil
from pathlib import Path

def safe_file_operation(operation, *args, **kwargs):
    try:
        return operation(*args, **kwargs)
    except FileNotFoundError as e:
        app.logger.error(f"File not found: {str(e)}")
        return {
            'success': False,
            'error': 'File not found',
            'code': 'FILE_NOT_FOUND'
        }
    except PermissionError as e:
        app.logger.error(f"Permission denied: {str(e)}")
        return {
            'success': False,
            'error': 'Permission denied',
            'code': 'PERMISSION_DENIED'
        }
    except OSError as e:
        app.logger.error(f"File system error: {str(e)}")
        return {
            'success': False,
            'error': 'File system error',
            'code': 'FILE_SYSTEM_ERROR'
        }

# Usage
def create_directory(path):
    return safe_file_operation(os.makedirs, path, exist_ok=True)
```

#### DataLad Operation Errors
```python
import subprocess
import json

def safe_datalad_operation(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'DataLad operation failed: {result.stderr}',
                'code': 'DATALAD_ERROR',
                'stderr': result.stderr
            }
        
        return {
            'success': True,
            'output': result.stdout
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'DataLad operation timed out',
            'code': 'DATALAD_TIMEOUT'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'DataLad operation failed: {str(e)}',
            'code': 'DATALAD_ERROR'
        }

# Usage
def create_datalad_dataset(path):
    return safe_datalad_operation(['datalad', 'create', path])
```

### 5. Git Operation Errors

#### Git Command Errors
```python
def safe_git_operation(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Git operation failed: {result.stderr}',
                'code': 'GIT_ERROR',
                'stderr': result.stderr
            }
        
        return {
            'success': True,
            'output': result.stdout
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Git operation timed out',
            'code': 'GIT_TIMEOUT'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Git operation failed: {str(e)}',
            'code': 'GIT_ERROR'
        }

# Usage
def git_commit(repo_path, message):
    return safe_git_operation(
        ['git', 'commit', '-m', message],
        cwd=repo_path
    )
```

## 🎨 Frontend Error Handling

### JavaScript Error Handling

#### API Error Handling
```javascript
// utils/error-handling.js
class ErrorHandler {
    static handleApiError(response) {
        if (!response.ok) {
            const error = response.json();
            throw new Error(error.error || 'API request failed');
        }
        return response.json();
    }
    
    static displayError(message, container = '.error-container') {
        const errorDiv = document.querySelector(container);
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <strong>Error:</strong> ${message}
                </div>
            `;
            errorDiv.style.display = 'block';
        }
    }
    
    static clearErrors(container = '.error-container') {
        const errorDiv = document.querySelector(container);
        if (errorDiv) {
            errorDiv.innerHTML = '';
            errorDiv.style.display = 'none';
        }
    }
}

// Usage in API calls
async function createProject(projectData) {
    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(projectData)
        });
        
        const result = await ErrorHandler.handleApiError(response);
        
        if (result.success) {
            ErrorHandler.clearErrors();
            return result.project;
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        ErrorHandler.displayError(error.message);
        throw error;
    }
}
```

#### Form Validation Errors
```javascript
// utils/forms.js
class FormValidator {
    static validateProjectForm(formData) {
        const errors = {};
        
        if (!formData.name || formData.name.trim().length < 3) {
            errors.name = 'Project name must be at least 3 characters';
        }
        
        if (!formData.research_type) {
            errors.research_type = 'Research type is required';
        }
        
        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
    
    static displayFormErrors(errors, formElement) {
        // Clear previous errors
        formElement.querySelectorAll('.error-message').forEach(el => el.remove());
        
        // Display new errors
        Object.keys(errors).forEach(field => {
            const fieldElement = formElement.querySelector(`[name="${field}"]`);
            if (fieldElement) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message text-danger small mt-1';
                errorDiv.textContent = errors[field];
                fieldElement.parentNode.appendChild(errorDiv);
            }
        });
    }
}
```

### Template Error Handling

#### Error Display Templates
```html
<!-- templates/partials/_error_boundary.html -->
<div class="error-boundary" style="display: none;">
    <div class="alert alert-danger" role="alert">
        <h4 class="alert-heading">Something went wrong!</h4>
        <p class="error-message">An unexpected error occurred. Please try again.</p>
        <hr>
        <button class="btn btn-outline-danger btn-sm" onclick="location.reload()">
            Reload Page
        </button>
    </div>
</div>

<script>
// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    document.querySelector('.error-boundary').style.display = 'block';
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    document.querySelector('.error-boundary').style.display = 'block';
});
</script>
```

## 🔍 Error Logging and Monitoring

### Application Logging

#### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler for errors
        file_handler = RotatingFileHandler(
            'logs/scitrace_error.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('SciTrace startup')
```

#### Error Logging Decorator
```python
import functools
import traceback

def log_errors(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {f.__name__}: {str(e)}")
            app.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return decorated_function

# Usage
@log_errors
def create_dataflow(dataflow_data):
    # Dataflow creation logic
    pass
```

### Error Monitoring

#### Error Tracking
```python
class ErrorTracker:
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
    
    def track_error(self, error_type, error_message, context=None):
        # Increment error count
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store error details
        error_record = {
            'timestamp': datetime.now(),
            'type': error_type,
            'message': error_message,
            'context': context
        }
        self.error_history.append(error_record)
        
        # Log error
        app.logger.error(f"Error tracked: {error_type} - {error_message}")
    
    def get_error_summary(self):
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': self.error_counts,
            'recent_errors': self.error_history[-10:]  # Last 10 errors
        }

# Global error tracker
error_tracker = ErrorTracker()
```

## 🚨 Common Error Scenarios

### 1. Database Connection Errors

#### Symptoms
- "Database connection failed" errors
- Slow response times
- Timeout errors

#### Solutions
```python
# Check database connection
def check_database_connection():
    try:
        db.session.execute('SELECT 1')
        return True
    except Exception as e:
        app.logger.error(f"Database connection failed: {str(e)}")
        return False

# Retry mechanism
def retry_database_operation(operation, max_retries=3):
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. DataLad Operation Errors

#### Symptoms
- "DataLad operation failed" errors
- Dataset creation failures
- File synchronization issues

#### Solutions
```python
def diagnose_datalad_issue(dataset_path):
    # Check if DataLad is installed
    try:
        subprocess.run(['datalad', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'issue': 'DataLad not installed',
            'solution': 'Install DataLad: pip install datalad'
        }
    
    # Check dataset integrity
    try:
        result = subprocess.run(
            ['datalad', 'status', dataset_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return {
                'issue': 'Dataset integrity problem',
                'solution': 'Run: datalad install --recursive ' + dataset_path
            }
    except Exception as e:
        return {
            'issue': 'Dataset access problem',
            'solution': f'Check permissions and path: {str(e)}'
        }
    
    return {'issue': 'No issues detected'}
```

### 3. File System Errors

#### Symptoms
- "Permission denied" errors
- "File not found" errors
- Disk space issues

#### Solutions
```python
def diagnose_file_system_issue(file_path):
    issues = []
    
    # Check if path exists
    if not os.path.exists(file_path):
        issues.append({
            'issue': 'Path does not exist',
            'solution': f'Create directory: mkdir -p {os.path.dirname(file_path)}'
        })
    
    # Check permissions
    if os.path.exists(file_path):
        if not os.access(file_path, os.R_OK):
            issues.append({
                'issue': 'Read permission denied',
                'solution': f'Fix permissions: chmod +r {file_path}'
            })
        
        if not os.access(file_path, os.W_OK):
            issues.append({
                'issue': 'Write permission denied',
                'solution': f'Fix permissions: chmod +w {file_path}'
            })
    
    # Check disk space
    statvfs = os.statvfs(os.path.dirname(file_path))
    free_space = statvfs.f_frsize * statvfs.f_available
    if free_space < 1024 * 1024 * 100:  # Less than 100MB
        issues.append({
            'issue': 'Low disk space',
            'solution': 'Free up disk space or move to different location'
        })
    
    return issues
```

## 🔧 Error Recovery Strategies

### Automatic Recovery

#### Database Recovery
```python
def recover_database_connection():
    try:
        # Close existing connections
        db.session.close()
        
        # Recreate database engine
        db.create_all()
        
        # Test connection
        db.session.execute('SELECT 1')
        
        app.logger.info("Database connection recovered")
        return True
    except Exception as e:
        app.logger.error(f"Database recovery failed: {str(e)}")
        return False
```

#### File System Recovery
```python
def recover_file_system_access(path):
    try:
        # Check and fix permissions
        if os.path.exists(path):
            os.chmod(path, 0o755)
        
        # Create missing directories
        os.makedirs(path, exist_ok=True)
        
        # Test access
        with open(os.path.join(path, 'test.txt'), 'w') as f:
            f.write('test')
        os.remove(os.path.join(path, 'test.txt'))
        
        app.logger.info(f"File system access recovered for {path}")
        return True
    except Exception as e:
        app.logger.error(f"File system recovery failed: {str(e)}")
        return False
```

### Manual Recovery

#### Reset Application State
```python
@app.route('/api/admin/reset-errors', methods=['POST'])
@require_permission('admin')
def reset_errors():
    try:
        # Clear error tracking
        error_tracker.error_counts.clear()
        error_tracker.error_history.clear()
        
        # Reset database connections
        db.session.close()
        db.create_all()
        
        # Clear caches
        cache.clear()
        
        return jsonify({
            'success': True,
            'message': 'Error state reset successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Reset failed: {str(e)}'
        }), 500
```

## 📋 Error Handling Checklist

### Development Checklist

- [ ] Input validation implemented for all forms
- [ ] API error responses standardized
- [ ] Database error handling configured
- [ ] File system error handling implemented
- [ ] DataLad operation error handling added
- [ ] Git operation error handling added
- [ ] Frontend error display implemented
- [ ] Error logging configured
- [ ] Error monitoring set up
- [ ] Recovery mechanisms implemented

### Production Checklist

- [ ] Error logging to files configured
- [ ] Error monitoring and alerting set up
- [ ] Database connection pooling configured
- [ ] File system permissions verified
- [ ] DataLad installation verified
- [ ] Git configuration verified
- [ ] Error recovery procedures documented
- [ ] Support contact information available
- [ ] Error escalation procedures defined

## 🆘 Getting Help with Errors

### Error Reporting

When reporting errors, please include:

1. **Error Message**: The exact error message
2. **Steps to Reproduce**: What you were doing when the error occurred
3. **Environment**: Operating system, Python version, browser
4. **Logs**: Relevant log entries from the application
5. **Screenshots**: If applicable, screenshots of the error

### Error Codes Reference

| Code | Description | Solution |
|------|-------------|----------|
| `VALIDATION_ERROR` | Input validation failed | Check form data and try again |
| `AUTH_REQUIRED` | Authentication required | Log in to the application |
| `PERMISSION_DENIED` | Insufficient permissions | Contact administrator |
| `DB_CONNECTION_ERROR` | Database connection failed | Check database status |
| `DATALAD_ERROR` | DataLad operation failed | Check DataLad installation |
| `GIT_ERROR` | Git operation failed | Check Git configuration |
| `FILE_SYSTEM_ERROR` | File system operation failed | Check file permissions |

---

**Need help with a specific error?** Check out the [FAQ](faq.md) for common solutions, or explore the [Troubleshooting Guide](README.md) for comprehensive problem-solving strategies.
