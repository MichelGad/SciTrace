# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with SciTrace. If you don't find your issue here, check the [FAQ](faq.md) or create an issue in the repository.

## 🚨 Common Issues

### Installation Issues

#### Python Version Problems
**Problem**: "Python 3.8+ required" error
**Symptoms**: Installation script fails with version error
**Solutions**:
```bash
# Check Python version
python3 --version

# Install Python 3.8+ if needed
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-venv python3.8-pip

# macOS
brew install python@3.8

# Use specific Python version
python3.8 -m venv venv
source venv/bin/activate
```

#### DataLad Installation Issues
**Problem**: DataLad installation fails
**Symptoms**: "datalad command not found" or installation errors
**Solutions**:
```bash
# Install DataLad manually
pip install datalad

# Or use conda
conda install -c conda-forge datalad

# Verify installation
datalad --version

# Check Git configuration (required for DataLad)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### Permission Issues
**Problem**: Permission denied errors during installation
**Symptoms**: "Permission denied" or "Access denied" errors
**Solutions**:
```bash
# Fix script permissions
chmod +x install.sh

# Run with proper permissions
sudo chmod 755 /path/to/scitrace
sudo chown -R $USER:$USER /path/to/scitrace

# Use user installation
python3 -m venv venv --user
```

### Application Startup Issues

#### Port Already in Use
**Problem**: "Address already in use" error
**Symptoms**: Flask app won't start on port 5001
**Solutions**:
```bash
# Use the provided stop script
python stop_flask.py

# Or manually find and kill the process
lsof -ti:5001 | xargs kill

# Or use a different port
export FLASK_RUN_PORT=5002
python run.py
```

#### Database Connection Issues
**Problem**: Database connection fails
**Symptoms**: "Database connection error" or SQLite errors
**Solutions**:
```bash
# Check database file permissions
ls -la instance/scitrace.db

# Fix permissions if needed
chmod 664 instance/scitrace.db
chown $USER:$USER instance/scitrace.db

# Recreate database
rm instance/scitrace.db
python run.py
```

#### Virtual Environment Issues
**Problem**: Virtual environment not activating or missing packages
**Symptoms**: "Module not found" errors or activation failures
**Solutions**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### DataLad Integration Issues

#### Dataset Creation Fails
**Problem**: DataLad dataset creation fails
**Symptoms**: "Failed to create dataset" or DataLad errors
**Solutions**:
```bash
# Check DataLad installation
datalad --version

# Check Git configuration
git config --global user.name
git config --global user.email

# Check directory permissions
ls -la /path/to/dataset/location

# Try manual dataset creation
datalad create /path/to/dataset
```

#### File Tracking Issues
**Problem**: Files not being tracked by DataLad
**Symptoms**: Files appear as "untracked" in visualization
**Solutions**:
```bash
# Add files manually
cd /path/to/dataset
datalad add raw_data/data.csv

# Check file permissions
ls -la raw_data/data.csv

# Verify file is not in .gitignore
cat .gitignore

# Check DataLad status
datalad status
```

#### Commit Failures
**Problem**: Commits fail or are rejected
**Symptoms**: "Commit failed" or Git errors
**Solutions**:
```bash
# Check Git configuration
git config --global user.name
git config --global user.email

# Check repository status
git status

# Check for merge conflicts
git diff

# Try manual commit
git add .
git commit -m "Manual commit"
```

### File Management Issues

#### File Upload Failures
**Problem**: File uploads fail or timeout
**Symptoms**: "Upload failed" or timeout errors
**Solutions**:
```bash
# Check file size limits
# Increase in nginx/apache configuration
client_max_body_size 100M;

# Check disk space
df -h

# Check file permissions
ls -la /path/to/upload/directory

# Try smaller files first
```

#### File Access Issues
**Problem**: Can't access or download files
**Symptoms**: "File not found" or permission errors
**Solutions**:
```bash
# Check file existence
ls -la /path/to/file

# Check file permissions
chmod 644 /path/to/file

# Check directory permissions
chmod 755 /path/to/directory

# Verify file path in database
sqlite3 instance/scitrace.db "SELECT * FROM dataflows WHERE id=1;"
```

#### File Restoration Issues
**Problem**: File restoration fails
**Symptoms**: "Restore failed" or Git errors
**Solutions**:
```bash
# Check Git history
git log --oneline

# Check file in specific commit
git show commit_hash:path/to/file

# Try manual restoration
git checkout commit_hash -- path/to/file
git add path/to/file
git commit -m "Restored file"
```

### Performance Issues

#### Slow Application Response
**Problem**: Application responds slowly
**Symptoms**: Long loading times or timeouts
**Solutions**:
```bash
# Check system resources
htop
free -h
df -h

# Check database performance
sqlite3 instance/scitrace.db "PRAGMA integrity_check;"

# Check for large files
find /path/to/datasets -size +100M

# Restart application
python stop_flask.py
python run.py
```

#### Memory Issues
**Problem**: High memory usage or out of memory errors
**Symptoms**: System slowdown or crashes
**Solutions**:
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
# Restart application regularly
# Consider using production WSGI server (gunicorn)

# Monitor DataLad operations
datalad status --annex
```

#### Disk Space Issues
**Problem**: Running out of disk space
**Symptoms**: "No space left on device" errors
**Solutions**:
```bash
# Check disk usage
df -h
du -sh /path/to/datasets/*

# Clean up old files
find /path/to/datasets -name "*.tmp" -delete
find /path/to/datasets -name "*.log" -delete

# Remove old datasets
rm -rf /path/to/old/datasets
```

### User Interface Issues

#### JavaScript Errors
**Problem**: JavaScript errors in browser console
**Symptoms**: Features not working or console errors
**Solutions**:
```bash
# Check browser console for errors
# Clear browser cache
# Try different browser
# Check JavaScript files
ls -la scitrace/static/js/
```

#### CSS Styling Issues
**Problem**: Styling not loading or broken layout
**Symptoms**: Missing styles or broken UI
**Solutions**:
```bash
# Check CSS files
ls -la scitrace/static/css/

# Clear browser cache
# Check for CSS syntax errors
# Verify Bootstrap loading
```

#### Template Rendering Issues
**Problem**: Templates not rendering correctly
**Symptoms**: Missing content or template errors
**Solutions**:
```bash
# Check template files
ls -la scitrace/templates/

# Check for template syntax errors
# Verify Jinja2 installation
pip show Jinja2

# Check template inheritance
```

## 🔍 Debugging Techniques

### Enable Debug Mode
```bash
# Set debug mode
export FLASK_DEBUG=1
export FLASK_ENV=development

# Run with debug
python run.py
```

### Check Logs
```bash
# Application logs
tail -f server.log

# System logs
sudo journalctl -u scitrace -f

# Database logs
tail -f /var/log/postgresql/postgresql-*.log
```

### Database Debugging
```bash
# Check database integrity
sqlite3 instance/scitrace.db "PRAGMA integrity_check;"

# Check table structure
sqlite3 instance/scitrace.db ".schema"

# Check data
sqlite3 instance/scitrace.db "SELECT * FROM users;"
sqlite3 instance/scitrace.db "SELECT * FROM projects;"
```

### DataLad Debugging
```bash
# Check DataLad configuration
datalad configuration

# Check dataset status
datalad status

# Check Git status
git status

# Check annex status
datalad status --annex
```

## 🛠️ Diagnostic Tools

### System Information
```bash
# System info
uname -a
lsb_release -a

# Python info
python3 --version
pip list

# DataLad info
datalad --version
git --version
```

### Application Information
```bash
# Check installed packages
pip list

# Check application structure
ls -la scitrace/

# Check configuration
python -c "from scitrace import create_app; app = create_app(); print(app.config)"
```

### Network Diagnostics
```bash
# Check port availability
netstat -tlnp | grep 5001

# Check network connectivity
ping localhost
curl http://localhost:5001

# Check firewall
sudo ufw status
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Check the FAQ** for common questions
3. **Search existing issues** in the repository
4. **Try the diagnostic tools** above
5. **Gather relevant information**:
   - Operating system and version
   - Python version
   - DataLad version
   - Error messages
   - Steps to reproduce

### Creating an Issue

When creating an issue, include:

1. **Clear title** describing the problem
2. **Detailed description** of the issue
3. **Steps to reproduce** the problem
4. **Expected behavior** vs actual behavior
5. **System information**:
   - OS and version
   - Python version
   - DataLad version
   - SciTrace version
6. **Error messages** and logs
7. **Screenshots** if applicable

### Community Support

- **GitHub Issues**: [Create an issue](https://github.com/MichelGad/SciTrace/issues)
- **Discussions**: [Join discussions](https://github.com/MichelGad/SciTrace/discussions)
- **Documentation**: Check the [User Guide](../user-guide/README.md)
- **API Documentation**: Check the [API Reference](../api/README.md)

## 🔄 Recovery Procedures

### Complete Reset
```bash
# Stop application
python stop_flask.py

# Remove database
rm instance/scitrace.db

# Remove datasets
rm -rf ~/scitrace_demo_datasets/

# Restart application
python run.py
```

### Partial Reset
```bash
# Reset specific components
# Projects only
curl -X POST http://localhost:5001/api/admin/reset-projects

# Dataflows only
curl -X POST http://localhost:5001/api/admin/reset-dataflows

# Tasks only
curl -X POST http://localhost:5001/api/admin/reset-tasks
```

### Data Recovery
```bash
# Restore from backup
cp backup/scitrace.db instance/scitrace.db

# Restore datasets
cp -r backup/datasets/ ~/scitrace_demo_datasets/

# Restart application
python run.py
```

---

**Still having issues?** Check out the [FAQ](faq.md) for more answers, or create an issue in the repository with detailed information about your problem.
