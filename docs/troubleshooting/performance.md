# Performance Optimization Guide

This guide covers performance optimization strategies for SciTrace, including database optimization, caching, and system resource management.

## 🚀 Performance Overview

SciTrace is designed for high performance with research data workflows. This guide helps you optimize performance for your specific use case.

## 📊 Performance Metrics

### Key Performance Indicators (KPIs)

- **Page Load Time**: < 2 seconds for dashboard
- **API Response Time**: < 500ms for most endpoints
- **File Upload Speed**: > 10MB/s for local storage
- **Database Query Time**: < 100ms for complex queries
- **Memory Usage**: < 512MB for typical workloads

### Monitoring Performance

```bash
# Check system resources
htop
iostat -x 1
df -h

# Monitor SciTrace performance
tail -f /var/log/scitrace/performance.log
```

## 🗄️ Database Performance

### SQLite Optimization

#### Database Configuration
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'timeout': 20,
        'check_same_thread': False
    }
}
```

#### Query Optimization
```python
# Use eager loading for related objects
projects = Project.query.options(
    joinedload(Project.dataflows),
    joinedload(Project.tasks)
).all()

# Use indexes for frequently queried fields
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)  # Indexed
    research_type = db.Column(db.String(50), index=True)  # Indexed
    created_at = db.Column(db.DateTime, index=True)  # Indexed
```

#### Database Maintenance
```bash
# Optimize SQLite database
sqlite3 instance/scitrace.db "VACUUM;"
sqlite3 instance/scitrace.db "ANALYZE;"

# Check database size
du -h instance/scitrace.db
```

### PostgreSQL Optimization (Production)

#### Connection Pooling
```python
# Production configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}
```

#### Indexing Strategy
```sql
-- Create indexes for performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_dataflows_project_id ON dataflows(project_id);
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);

-- Composite indexes for complex queries
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at);
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
```

## 💾 Caching Strategies

### Application-Level Caching

#### Flask-Caching Configuration
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Use 'redis' for production
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Cache expensive operations
@cache.memoize(timeout=300)
def get_project_statistics(project_id):
    # Expensive database operations
    return statistics
```

#### Redis Caching (Production)
```python
# Redis configuration
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300
```

### Database Query Caching

#### Query Result Caching
```python
# Cache frequently accessed data
@cache.memoize(timeout=600)
def get_user_projects(user_id):
    return Project.query.filter_by(user_id=user_id).all()

# Cache expensive aggregations
@cache.memoize(timeout=300)
def get_project_file_count(project_id):
    return Dataflow.query.filter_by(project_id=project_id).count()
```

### Static Asset Caching

#### Browser Caching
```python
# Configure static file caching
@app.after_request
def after_request(response):
    if request.endpoint == 'static':
        response.cache_control.max_age = 31536000  # 1 year
    return response
```

#### CDN Configuration
```python
# Use CDN for static assets
app.config['STATIC_URL'] = 'https://cdn.example.com/static/'
```

## 🔧 System Resource Optimization

### Memory Management

#### Memory Usage Monitoring
```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

# Monitor memory usage
@app.before_request
def monitor_memory():
    if get_memory_usage() > 500:  # 500MB threshold
        app.logger.warning("High memory usage detected")
```

#### Memory Optimization
```python
# Use generators for large datasets
def get_large_file_list(dataflow_id):
    for file_path in os.listdir(dataflow_path):
        yield file_path

# Clear unused objects
import gc
gc.collect()
```

### CPU Optimization

#### Background Task Processing
```python
from celery import Celery

# Configure Celery for background tasks
celery = Celery('scitrace', broker='redis://localhost:6379')

@celery.task
def process_large_dataset(dataflow_id):
    # Long-running operations
    pass
```

#### Async Operations
```python
import asyncio
import aiofiles

async def process_files_async(file_paths):
    tasks = []
    for file_path in file_paths:
        task = asyncio.create_task(process_file(file_path))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## 📁 File System Performance

### DataLad Optimization

#### Dataset Configuration
```python
# Optimize DataLad operations
def optimize_datalad_dataset(path):
    # Configure DataLad for performance
    subprocess.run([
        'datalad', 'config', '--local', 
        'annex.auto-commit', 'false'
    ], cwd=path)
    
    subprocess.run([
        'datalad', 'config', '--local',
        'annex.largefiles', 'exclude=*.txt'
    ], cwd=path)
```

#### File System Monitoring
```bash
# Monitor disk I/O
iostat -x 1

# Check disk space
df -h

# Monitor file operations
inotifywait -m /path/to/datasets
```

### Storage Optimization

#### File Compression
```python
import gzip
import shutil

def compress_large_file(file_path):
    with open(file_path, 'rb') as f_in:
        with gzip.open(f'{file_path}.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
```

#### Cleanup Strategies
```python
def cleanup_old_files(days=30):
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in get_old_files(cutoff_date):
        if os.path.exists(file_path):
            os.remove(file_path)
```

## 🌐 Network Performance

### API Optimization

#### Response Compression
```python
from flask_compress import Compress

# Enable response compression
Compress(app)

# Configure compression
app.config['COMPRESS_MIMETYPES'] = [
    'text/html',
    'text/css',
    'application/json',
    'application/javascript'
]
```

#### API Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply rate limiting to specific endpoints
@app.route('/api/dataflows', methods=['POST'])
@limiter.limit("10 per minute")
def create_dataflow():
    pass
```

### CDN Configuration

#### Static Asset Optimization
```python
# Use CDN for static assets
app.config['STATIC_URL'] = 'https://cdn.example.com/static/'

# Optimize asset delivery
@app.route('/static/<path:filename>')
def static_file(filename):
    response = send_from_directory(app.static_folder, filename)
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response
```

## 📊 Monitoring and Profiling

### Performance Monitoring

#### Application Metrics
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        app.logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

# Apply to expensive operations
@monitor_performance
def process_large_dataset(dataflow_id):
    pass
```

#### Database Query Profiling
```python
# Enable SQL query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Profile slow queries
@app.before_request
def log_slow_queries():
    start_time = time.time()
    g.start_time = start_time

@app.teardown_request
def log_slow_queries_teardown(exception):
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        if duration > 1.0:  # Log queries taking more than 1 second
            app.logger.warning(f"Slow query detected: {duration:.2f}s")
```

### System Monitoring

#### Resource Monitoring
```python
import psutil

def get_system_metrics():
    return {
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'load_average': os.getloadavg()
    }

# Log system metrics
@app.before_request
def log_system_metrics():
    metrics = get_system_metrics()
    if metrics['memory_percent'] > 80:
        app.logger.warning("High memory usage detected")
```

## 🚀 Production Optimization

### WSGI Server Configuration

#### Gunicorn Configuration
```bash
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### Nginx Configuration
```nginx
# nginx.conf
upstream scitrace {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name scitrace.example.com;
    
    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Static file caching
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Proxy to application
    location / {
        proxy_pass http://scitrace;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Optimization

#### Connection Pooling
```python
# Production database configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600,
    'pool_timeout': 30
}
```

#### Query Optimization
```python
# Use database-specific optimizations
if app.config['DATABASE_URL'].startswith('postgresql'):
    # PostgreSQL-specific optimizations
    app.config['SQLALCHEMY_ENGINE_OPTIONS'].update({
        'connect_args': {
            'options': '-c default_transaction_isolation=read_committed'
        }
    })
```

## 🔍 Performance Testing

### Load Testing

#### Using Apache Bench
```bash
# Test API endpoints
ab -n 1000 -c 10 http://localhost:5000/api/projects

# Test with authentication
ab -n 100 -c 5 -H "Cookie: session=your_session_cookie" \
   http://localhost:5000/api/dataflows
```

#### Using Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class SciTraceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
    
    @task(3)
    def view_projects(self):
        self.client.get("/api/projects")
    
    @task(1)
    def create_project(self):
        self.client.post("/api/projects", json={
            "name": "Test Project",
            "description": "Load test project",
            "research_type": "environmental"
        })
```

### Performance Benchmarks

#### Benchmark Script
```python
import time
import requests
import statistics

def benchmark_endpoint(url, iterations=100):
    times = []
    
    for i in range(iterations):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        if response.status_code == 200:
            times.append(end_time - start_time)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'min': min(times),
        'max': max(times),
        'std_dev': statistics.stdev(times) if len(times) > 1 else 0
    }

# Run benchmarks
results = benchmark_endpoint('http://localhost:5000/api/projects')
print(f"Average response time: {results['mean']:.3f}s")
```

## 📋 Performance Checklist

### Pre-Deployment Checklist

- [ ] Database indexes created and optimized
- [ ] Caching configured and tested
- [ ] Static assets optimized and compressed
- [ ] API rate limiting configured
- [ ] Background task processing set up
- [ ] Monitoring and logging configured
- [ ] Load testing completed
- [ ] Performance benchmarks established

### Ongoing Optimization

- [ ] Monitor performance metrics regularly
- [ ] Review and optimize slow queries
- [ ] Clean up old data and files
- [ ] Update database statistics
- [ ] Review and update caching strategies
- [ ] Monitor system resource usage
- [ ] Update performance documentation

## 🆘 Troubleshooting Performance Issues

### Common Performance Problems

#### Slow Database Queries
```python
# Enable query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Use EXPLAIN ANALYZE for PostgreSQL
# EXPLAIN ANALYZE SELECT * FROM projects WHERE user_id = 1;
```

#### High Memory Usage
```python
# Monitor memory usage
import tracemalloc
tracemalloc.start()

# Take snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

#### Slow File Operations
```bash
# Monitor disk I/O
iostat -x 1

# Check for disk space issues
df -h

# Monitor file system operations
inotifywait -m /path/to/datasets
```

### Performance Debugging Tools

#### Flask Debug Toolbar
```python
from flask_debugtoolbar import DebugToolbarExtension

# Enable debug toolbar in development
if app.debug:
    toolbar = DebugToolbarExtension(app)
```

#### Profiling Tools
```python
# Use cProfile for performance profiling
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result
```

---

**Need help with performance issues?** Check out the [Troubleshooting Guide](README.md) for common problems, or explore the [Monitoring Guide](../deployment/monitoring.md) for system monitoring strategies.
