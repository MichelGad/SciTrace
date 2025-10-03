# Monitoring and Logging Guide

This guide covers monitoring strategies, logging configuration, and alerting systems for SciTrace in production environments.

## 📊 Monitoring Overview

Effective monitoring is crucial for maintaining SciTrace's performance and reliability. This guide covers application monitoring, system metrics, and alerting strategies.

## 🔍 Monitoring Architecture

### Monitoring Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Architecture                   │
├─────────────────────────────────────────────────────────────┤
│  Application Monitoring                                     │
│  ├── Flask Application Metrics                              │
│  ├── Database Query Performance                             │
│  ├── API Response Times                                      │
│  └── User Activity Tracking                                 │
├─────────────────────────────────────────────────────────────┤
│  System Monitoring                                          │
│  ├── CPU Usage Monitoring                                   │
│  ├── Memory Usage Tracking                                  │
│  ├── Disk I/O Performance                                   │
│  └── Network Connectivity                                   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Monitoring                                  │
│  ├── Database Performance                                    │
│  ├── File System Health                                      │
│  ├── DataLad Operation Status                                │
│  └── Git Repository Health                                  │
├─────────────────────────────────────────────────────────────┤
│  Alerting & Notification                                    │
│  ├── Error Rate Alerts                                      │
│  ├── Performance Degradation Alerts                        │
│  ├── Resource Usage Alerts                                  │
│  └── Service Availability Alerts                           │
└─────────────────────────────────────────────────────────────┘
```

## 📈 Application Monitoring

### Flask Application Metrics

#### Request Monitoring
```python
import time
from functools import wraps
from flask import request, g

def monitor_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Store request info
        g.request_start_time = start_time
        g.request_path = request.path
        g.request_method = request.method
        
        try:
            result = f(*args, **kwargs)
            return result
        finally:
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log request metrics
            app.logger.info(f"Request: {request.method} {request.path} - {duration:.3f}s")
            
            # Track slow requests
            if duration > 2.0:
                app.logger.warning(f"Slow request: {request.path} - {duration:.3f}s")
    
    return decorated_function

# Apply to all routes
@app.before_request
def before_request():
    g.request_start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'request_start_time'):
        duration = time.time() - g.request_start_time
        response.headers['X-Response-Time'] = str(duration)
    return response
```

#### Performance Metrics Collection
```python
class PerformanceMetrics:
    def __init__(self):
        self.request_counts = {}
        self.response_times = []
        self.error_counts = {}
    
    def record_request(self, endpoint, method, duration, status_code):
        key = f"{method} {endpoint}"
        
        # Count requests
        if key not in self.request_counts:
            self.request_counts[key] = 0
        self.request_counts[key] += 1
        
        # Record response time
        self.response_times.append({
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        # Track errors
        if status_code >= 400:
            if key not in self.error_counts:
                self.error_counts[key] = 0
            self.error_counts[key] += 1
    
    def get_metrics(self):
        return {
            'request_counts': self.request_counts,
            'avg_response_time': sum(r['duration'] for r in self.response_times) / len(self.response_times) if self.response_times else 0,
            'error_counts': self.error_counts,
            'total_requests': sum(self.request_counts.values())
        }

# Global metrics collector
metrics = PerformanceMetrics()
```

### Database Monitoring

#### Query Performance Tracking
```python
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configure SQL query logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    
    # Log slow queries
    if total > 1.0:  # Queries taking more than 1 second
        app.logger.warning(f"Slow query ({total:.3f}s): {statement[:100]}...")
    
    # Track query metrics
    metrics.record_database_query(statement, total)
```

#### Database Health Checks
```python
def check_database_health():
    try:
        # Test basic connectivity
        db.session.execute('SELECT 1')
        
        # Check database size
        if app.config['DATABASE_URL'].startswith('sqlite'):
            db_size = os.path.getsize('instance/scitrace.db')
            if db_size > 1024 * 1024 * 100:  # 100MB
                app.logger.warning(f"Database size is large: {db_size / 1024 / 1024:.1f}MB")
        
        # Check connection pool status
        pool = db.engine.pool
        return {
            'status': 'healthy',
            'pool_size': pool.size(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow()
        }
    except Exception as e:
        app.logger.error(f"Database health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
```

### API Monitoring

#### Endpoint Performance Tracking
```python
def track_api_performance(endpoint_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                
                # Record successful request
                duration = time.time() - start_time
                metrics.record_api_call(endpoint_name, duration, 200)
                
                return result
            except Exception as e:
                # Record failed request
                duration = time.time() - start_time
                metrics.record_api_call(endpoint_name, duration, 500)
                raise
        
        return decorated_function
    return decorator

# Usage
@app.route('/api/projects', methods=['GET'])
@track_api_performance('list_projects')
def list_projects():
    pass
```

## 🖥️ System Monitoring

### Resource Monitoring

#### CPU and Memory Monitoring
```python
import psutil
import os

def get_system_metrics():
    """Get current system resource usage"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent,
            'used': psutil.virtual_memory().used
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'used': psutil.disk_usage('/').used,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        },
        'load_average': os.getloadavg()
    }

def check_resource_health():
    """Check if system resources are within acceptable limits"""
    metrics = get_system_metrics()
    alerts = []
    
    # CPU usage check
    if metrics['cpu_percent'] > 80:
        alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
    
    # Memory usage check
    if metrics['memory']['percent'] > 85:
        alerts.append(f"High memory usage: {metrics['memory']['percent']:.1f}%")
    
    # Disk usage check
    if metrics['disk']['percent'] > 90:
        alerts.append(f"High disk usage: {metrics['disk']['percent']:.1f}%")
    
    # Load average check
    load_avg = metrics['load_average'][0]
    cpu_count = psutil.cpu_count()
    if load_avg > cpu_count * 2:
        alerts.append(f"High load average: {load_avg:.2f}")
    
    return {
        'status': 'healthy' if not alerts else 'warning',
        'alerts': alerts,
        'metrics': metrics
    }
```

#### Process Monitoring
```python
def monitor_application_process():
    """Monitor the SciTrace application process"""
    try:
        process = psutil.Process(os.getpid())
        
        return {
            'pid': process.pid,
            'cpu_percent': process.cpu_percent(),
            'memory_info': process.memory_info(),
            'memory_percent': process.memory_percent(),
            'num_threads': process.num_threads(),
            'create_time': process.create_time(),
            'status': process.status()
        }
    except Exception as e:
        app.logger.error(f"Failed to monitor process: {str(e)}")
        return None
```

### File System Monitoring

#### Disk Usage Monitoring
```python
def monitor_disk_usage(paths_to_monitor):
    """Monitor disk usage for specific paths"""
    disk_usage = {}
    
    for path in paths_to_monitor:
        try:
            if os.path.exists(path):
                usage = psutil.disk_usage(path)
                disk_usage[path] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                }
            else:
                disk_usage[path] = {'error': 'Path does not exist'}
        except Exception as e:
            disk_usage[path] = {'error': str(e)}
    
    return disk_usage

# Monitor key directories
def check_storage_health():
    paths_to_monitor = [
        'instance/',  # Database
        'scitrace/static/',  # Static files
        '/tmp/',  # Temporary files
    ]
    
    return monitor_disk_usage(paths_to_monitor)
```

#### File System Health Checks
```python
def check_file_system_health():
    """Check file system health and permissions"""
    checks = []
    
    # Check database directory
    db_dir = 'instance'
    if os.path.exists(db_dir):
        if os.access(db_dir, os.R_OK | os.W_OK):
            checks.append({'path': db_dir, 'status': 'healthy'})
        else:
            checks.append({'path': db_dir, 'status': 'permission_error'})
    else:
        checks.append({'path': db_dir, 'status': 'not_found'})
    
    # Check static files directory
    static_dir = 'scitrace/static'
    if os.path.exists(static_dir):
        if os.access(static_dir, os.R_OK):
            checks.append({'path': static_dir, 'status': 'healthy'})
        else:
            checks.append({'path': static_dir, 'status': 'permission_error'})
    else:
        checks.append({'path': static_dir, 'status': 'not_found'})
    
    return checks
```

## 📝 Logging Configuration

### Application Logging

#### Logging Setup
```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os

def setup_application_logging(app):
    """Configure comprehensive logging for the application"""
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Application logs
    app_handler = RotatingFileHandler(
        'logs/scitrace.log',
        maxBytes=10240000,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(app_handler)
    
    # Error logs
    error_handler = RotatingFileHandler(
        'logs/scitrace_error.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(error_handler)
    
    # Performance logs
    perf_handler = TimedRotatingFileHandler(
        'logs/scitrace_performance.log',
        when='midnight',
        interval=1,
        backupCount=7
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(message)s'
    ))
    
    # Create performance logger
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    
    # Database query logs
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_handler = RotatingFileHandler(
        'logs/database_queries.log',
        maxBytes=10240000,  # 10MB
        backupCount=3
    )
    db_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(message)s'
    ))
    db_logger.addHandler(db_handler)
    db_logger.setLevel(logging.INFO)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('SciTrace logging configured')
```

#### Structured Logging
```python
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def log_request(self, method, path, status_code, duration, user_id=None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'request',
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration': duration,
            'user_id': user_id
        }
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error_type, error_message, context=None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'context': context
        }
        self.logger.error(json.dumps(log_data))
    
    def log_performance(self, operation, duration, details=None):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'performance',
            'operation': operation,
            'duration': duration,
            'details': details
        }
        self.logger.info(json.dumps(log_data))

# Global structured logger
structured_logger = StructuredLogger(app.logger)
```

### DataLad and Git Monitoring

#### DataLad Operation Logging
```python
def log_datalad_operation(operation, dataset_path, success, duration, error=None):
    """Log DataLad operations for monitoring"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': 'datalad_operation',
        'operation': operation,
        'dataset_path': dataset_path,
        'success': success,
        'duration': duration,
        'error': str(error) if error else None
    }
    
    if success:
        app.logger.info(json.dumps(log_data))
    else:
        app.logger.error(json.dumps(log_data))

# Usage in DataLad operations
def safe_datalad_operation(operation, dataset_path):
    start_time = time.time()
    try:
        result = subprocess.run(operation, cwd=dataset_path, capture_output=True, text=True)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            log_datalad_operation(operation[0], dataset_path, True, duration)
            return {'success': True, 'output': result.stdout}
        else:
            log_datalad_operation(operation[0], dataset_path, False, duration, result.stderr)
            return {'success': False, 'error': result.stderr}
    except Exception as e:
        duration = time.time() - start_time
        log_datalad_operation(operation[0], dataset_path, False, duration, str(e))
        return {'success': False, 'error': str(e)}
```

#### Git Operation Monitoring
```python
def log_git_operation(operation, repo_path, success, duration, error=None):
    """Log Git operations for monitoring"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'type': 'git_operation',
        'operation': operation,
        'repo_path': repo_path,
        'success': success,
        'duration': duration,
        'error': str(error) if error else None
    }
    
    if success:
        app.logger.info(json.dumps(log_data))
    else:
        app.logger.error(json.dumps(log_data))
```

## 🚨 Alerting and Notifications

### Alert Configuration

#### Alert Rules
```python
class AlertManager:
    def __init__(self):
        self.alert_rules = {
            'high_error_rate': {
                'threshold': 0.1,  # 10% error rate
                'window': 300,  # 5 minutes
                'enabled': True
            },
            'slow_response_time': {
                'threshold': 2.0,  # 2 seconds
                'window': 60,  # 1 minute
                'enabled': True
            },
            'high_cpu_usage': {
                'threshold': 80,  # 80% CPU
                'window': 60,  # 1 minute
                'enabled': True
            },
            'high_memory_usage': {
                'threshold': 85,  # 85% memory
                'window': 60,  # 1 minute
                'enabled': True
            },
            'database_connection_failure': {
                'threshold': 1,  # Any failure
                'window': 60,  # 1 minute
                'enabled': True
            }
        }
        self.alert_history = []
    
    def check_alerts(self):
        """Check all configured alert rules"""
        current_alerts = []
        
        # Check error rate
        if self.alert_rules['high_error_rate']['enabled']:
            error_rate = self.calculate_error_rate()
            if error_rate > self.alert_rules['high_error_rate']['threshold']:
                current_alerts.append({
                    'type': 'high_error_rate',
                    'severity': 'critical',
                    'message': f'High error rate detected: {error_rate:.2%}',
                    'timestamp': datetime.utcnow()
                })
        
        # Check response times
        if self.alert_rules['slow_response_time']['enabled']:
            avg_response_time = self.calculate_avg_response_time()
            if avg_response_time > self.alert_rules['slow_response_time']['threshold']:
                current_alerts.append({
                    'type': 'slow_response_time',
                    'severity': 'warning',
                    'message': f'Slow response time: {avg_response_time:.2f}s',
                    'timestamp': datetime.utcnow()
                })
        
        # Check system resources
        system_metrics = get_system_metrics()
        
        if self.alert_rules['high_cpu_usage']['enabled']:
            if system_metrics['cpu_percent'] > self.alert_rules['high_cpu_usage']['threshold']:
                current_alerts.append({
                    'type': 'high_cpu_usage',
                    'severity': 'warning',
                    'message': f'High CPU usage: {system_metrics["cpu_percent"]:.1f}%',
                    'timestamp': datetime.utcnow()
                })
        
        if self.alert_rules['high_memory_usage']['enabled']:
            if system_metrics['memory']['percent'] > self.alert_rules['high_memory_usage']['threshold']:
                current_alerts.append({
                    'type': 'high_memory_usage',
                    'severity': 'critical',
                    'message': f'High memory usage: {system_metrics["memory"]["percent"]:.1f}%',
                    'timestamp': datetime.utcnow()
                })
        
        # Store alerts
        for alert in current_alerts:
            self.alert_history.append(alert)
            self.send_alert(alert)
        
        return current_alerts
    
    def send_alert(self, alert):
        """Send alert notification"""
        # Log alert
        app.logger.warning(f"ALERT: {alert['message']}")
        
        # Send email notification (if configured)
        if app.config.get('ALERT_EMAIL_ENABLED'):
            self.send_email_alert(alert)
        
        # Send webhook notification (if configured)
        if app.config.get('ALERT_WEBHOOK_URL'):
            self.send_webhook_alert(alert)
    
    def send_email_alert(self, alert):
        """Send email alert"""
        # Implementation for email alerts
        pass
    
    def send_webhook_alert(self, alert):
        """Send webhook alert"""
        # Implementation for webhook alerts
        pass

# Global alert manager
alert_manager = AlertManager()
```

### Health Check Endpoints

#### System Health Check
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Database health
    db_health = check_database_health()
    health_status['checks']['database'] = db_health
    
    # System resources
    resource_health = check_resource_health()
    health_status['checks']['resources'] = resource_health
    
    # File system health
    fs_health = check_file_system_health()
    health_status['checks']['filesystem'] = fs_health
    
    # Storage health
    storage_health = check_storage_health()
    health_status['checks']['storage'] = storage_health
    
    # Determine overall status
    if any(check.get('status') == 'unhealthy' for check in health_status['checks'].values()):
        health_status['status'] = 'unhealthy'
    elif any(check.get('status') == 'warning' for check in health_status['checks'].values()):
        health_status['status'] = 'warning'
    
    # Return appropriate HTTP status
    if health_status['status'] == 'healthy':
        return jsonify(health_status), 200
    elif health_status['status'] == 'warning':
        return jsonify(health_status), 200
    else:
        return jsonify(health_status), 503
```

#### Metrics Endpoint
```python
@app.route('/metrics', methods=['GET'])
def metrics_endpoint():
    """Prometheus-compatible metrics endpoint"""
    metrics_data = {
        'application': {
            'requests_total': sum(metrics.request_counts.values()),
            'errors_total': sum(metrics.error_counts.values()),
            'avg_response_time': metrics.get_avg_response_time()
        },
        'system': get_system_metrics(),
        'database': check_database_health(),
        'alerts': len(alert_manager.alert_history)
    }
    
    return jsonify(metrics_data)
```

## 📊 Monitoring Dashboard

### Real-time Monitoring

#### WebSocket Monitoring
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    """Send initial monitoring data to connected clients"""
    emit('monitoring_data', {
        'system_metrics': get_system_metrics(),
        'application_metrics': metrics.get_metrics(),
        'alerts': alert_manager.alert_history[-10:]  # Last 10 alerts
    })

@socketio.on('request_update')
def handle_update_request():
    """Send updated monitoring data"""
    emit('monitoring_data', {
        'system_metrics': get_system_metrics(),
        'application_metrics': metrics.get_metrics(),
        'alerts': alert_manager.alert_history[-10:]
    })
```

#### Monitoring Data Collection
```python
def collect_monitoring_data():
    """Collect comprehensive monitoring data"""
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'application': {
            'requests_per_minute': metrics.get_requests_per_minute(),
            'avg_response_time': metrics.get_avg_response_time(),
            'error_rate': metrics.get_error_rate(),
            'active_users': get_active_user_count()
        },
        'system': get_system_metrics(),
        'database': check_database_health(),
        'storage': check_storage_health(),
        'alerts': alert_manager.alert_history[-24:]  # Last 24 hours
    }
```

## 🔧 Monitoring Tools Integration

### Prometheus Integration

#### Metrics Export
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
REQUEST_COUNT = Counter('scitrace_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('scitrace_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('scitrace_active_users', 'Active users')
DATABASE_CONNECTIONS = Gauge('scitrace_database_connections', 'Database connections')

@app.route('/metrics/prometheus')
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain'}

# Update metrics in request handlers
@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        REQUEST_DURATION.observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    return response
```

### Grafana Dashboard Configuration

#### Dashboard JSON
```json
{
  "dashboard": {
    "title": "SciTrace Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(scitrace_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(scitrace_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Active Users",
        "type": "singlestat",
        "targets": [
          {
            "expr": "scitrace_active_users"
          }
        ]
      }
    ]
  }
}
```

## 📋 Monitoring Checklist

### Pre-Production Checklist

- [ ] Application logging configured
- [ ] System metrics collection set up
- [ ] Database monitoring configured
- [ ] File system monitoring enabled
- [ ] Alert rules defined and tested
- [ ] Health check endpoints implemented
- [ ] Monitoring dashboard configured
- [ ] Log rotation configured
- [ ] Error tracking implemented
- [ ] Performance metrics collection enabled

### Production Monitoring

- [ ] Real-time monitoring dashboard active
- [ ] Alert notifications configured
- [ ] Log aggregation set up
- [ ] Metrics collection running
- [ ] Health checks automated
- [ ] Performance baselines established
- [ ] Alert escalation procedures defined
- [ ] Monitoring documentation updated

## 🆘 Troubleshooting Monitoring Issues

### Common Monitoring Problems

#### Missing Metrics
```python
def diagnose_monitoring_issues():
    """Diagnose common monitoring problems"""
    issues = []
    
    # Check if metrics collection is working
    if not hasattr(app, 'metrics_collector'):
        issues.append("Metrics collection not initialized")
    
    # Check if logging is configured
    if not app.logger.handlers:
        issues.append("Logging not configured")
    
    # Check if health checks are responding
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code != 200:
            issues.append("Health check endpoint not responding")
    except:
        issues.append("Health check endpoint unreachable")
    
    return issues
```

#### Alert Fatigue
```python
def prevent_alert_fatigue():
    """Implement alert throttling to prevent spam"""
    alert_cooldown = 300  # 5 minutes
    
    def should_send_alert(alert_type):
        now = time.time()
        recent_alerts = [
            alert for alert in alert_manager.alert_history
            if alert['type'] == alert_type and 
            (now - alert['timestamp'].timestamp()) < alert_cooldown
        ]
        return len(recent_alerts) == 0
    
    return should_send_alert
```

---

**Need help with monitoring setup?** Check out the [Deployment Guide](README.md) for production setup, or explore the [Troubleshooting Guide](../troubleshooting/README.md) for common monitoring issues.
