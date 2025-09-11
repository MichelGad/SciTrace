# Frequently Asked Questions (FAQ)

This FAQ addresses the most common questions about SciTrace. If you don't find your question here, check the [Troubleshooting Guide](README.md) or create an issue in the repository.

## 🚀 Installation & Setup

### Q: What are the system requirements for SciTrace?
**A:** SciTrace requires:
- **Operating System**: macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Python**: Python 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free disk space
- **Network**: Internet connection for initial setup

### Q: Do I need to install DataLad separately?
**A:** No, the installation script automatically installs DataLad if it's not present. However, you can install it manually:
```bash
pip install datalad
```

### Q: Can I install SciTrace on Windows?
**A:** Yes, SciTrace works on Windows 10+. Use the installation script with bash:
```bash
bash install.sh
```

### Q: What if the installation script fails?
**A:** Try manual installation:
1. Create virtual environment: `python3 -m venv venv`
2. Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Install DataLad: `pip install datalad`
5. Run the application: `python run.py`

## 🔐 Authentication & Users

### Q: What are the default login credentials?
**A:** The default admin credentials are:
- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change these credentials immediately after installation for security.

### Q: How do I change the admin password?
**A:** 
1. Login to SciTrace
2. Click on your username in the top navigation
3. Go to "Profile" or "Settings"
4. Change your password
5. Save the changes

### Q: Can I create additional users?
**A:** Yes, you can create additional users through the registration page or by adding them as collaborators to projects.

### Q: How do I reset a forgotten password?
**A:** Currently, you need to reset the password through the database or recreate the admin user. This feature will be added in future versions.

## 📁 Projects & Dataflows

### Q: What's the difference between a project and a dataflow?
**A:** 
- **Project**: A research project that can contain multiple dataflows, tasks, and collaborators
- **Dataflow**: A specific data workflow within a project, represented as an interactive visualization

### Q: How many projects can I create?
**A:** There's no hard limit on the number of projects. The limit depends on your system resources and storage space.

### Q: Can I delete a project?
**A:** Yes, you can delete projects through the project management interface. **Warning**: This will also delete all associated dataflows and DataLad datasets.

### Q: What research types are available?
**A:** SciTrace supports four research types:
- **Environmental**: Water quality, climate data, ecological studies
- **Biomedical**: Medical research, clinical trials, health studies
- **Computational**: Machine learning, simulations, data analysis
- **General**: Custom research projects, interdisciplinary studies

## 🔄 DataLad Integration

### Q: Do I need to know DataLad to use SciTrace?
**A:** No, SciTrace provides a web interface for all DataLad operations. However, knowing DataLad can help you understand what's happening behind the scenes.

### Q: Can I use existing DataLad datasets?
**A:** Yes, you can import existing DataLad datasets into SciTrace. This feature is available through the dataflow creation interface.

### Q: Where are my datasets stored?
**A:** By default, datasets are stored in your home directory under `~/scitrace_demo_datasets/` for demo data, or in the location you specify when creating dataflows.

### Q: Can I move or rename datasets?
**A:** Yes, but you should do this through SciTrace's interface to maintain proper tracking. Moving datasets manually may break the integration.

### Q: What happens if DataLad is not installed?
**A:** SciTrace will show an error and guide you through installing DataLad. The installation script should handle this automatically.

## 📊 File Management

### Q: What file types are supported?
**A:** SciTrace supports all file types. It provides special handling for:
- **Text files**: View content in browser
- **Images**: Display in browser
- **Data files**: CSV, JSON, etc.
- **Code files**: Python, R, etc. with syntax highlighting

### Q: Is there a file size limit?
**A:** The default limit is 100MB per file, but this can be configured in your web server settings. Large files are handled efficiently through DataLad's Git-annex system.

### Q: Can I upload multiple files at once?
**A:** Currently, you can upload files one at a time through the web interface. Batch upload functionality is planned for future versions.

### Q: How do I restore deleted files?
**A:** 
1. Go to your dataflow visualization
2. Look for red nodes (deleted files)
3. Click the restore button
4. Select the commit to restore from
5. The file will be restored and committed

### Q: Can I view file differences between versions?
**A:** Yes, use the Git Log feature to view commit history and file differences between versions.

## 🔍 Visualization & Interface

### Q: What do the different colors in the dataflow visualization mean?
**A:** 
- **Blue nodes**: Directories
- **Green nodes**: Tracked files
- **Gray nodes**: Untracked files
- **Red nodes**: Deleted files
- **Yellow nodes**: Modified files

### Q: Can I customize the visualization?
**A:** The visualization automatically reflects your data structure. Customization options are planned for future versions.

### Q: Why is my dataflow visualization empty?
**A:** This usually means:
1. No files have been added to the dataset yet
2. Files are not being tracked by DataLad
3. There's an issue with the dataset path

### Q: Can I export the visualization?
**A:** Currently, you can take screenshots of the visualization. Export functionality is planned for future versions.

## 🛠️ Technical Issues

### Q: Why is SciTrace running slowly?
**A:** Common causes:
1. **Large datasets**: Many files or large files
2. **System resources**: Insufficient RAM or CPU
3. **Database issues**: Corrupted database or large database
4. **Network issues**: Slow network connections

### Q: How do I update SciTrace?
**A:** 
1. Stop the application: `python stop_flask.py`
2. Pull latest changes: `git pull origin main`
3. Update dependencies: `pip install -r requirements.txt --upgrade`
4. Restart: `python run.py`

### Q: Can I run SciTrace on a different port?
**A:** Yes, set the port environment variable:
```bash
export FLASK_RUN_PORT=5002
python run.py
```

### Q: How do I backup my data?
**A:** 
1. **Database**: Copy `instance/scitrace.db`
2. **Datasets**: Copy your dataset directories
3. **Configuration**: Save your configuration files

### Q: Can I use a different database?
**A:** Yes, SciTrace supports PostgreSQL, MySQL, and other databases supported by SQLAlchemy. Change the `DATABASE_URL` environment variable.

## 🔄 Demo & Testing

### Q: How do I load demo data?
**A:** 
1. Login to SciTrace
2. Click "Load Demo Projects" on the dashboard
3. Wait for the setup to complete
4. Explore the sample environmental research project

### Q: Can I reset all data?
**A:** Yes, use the reset options:
- **Dashboard**: "Reset All Data" button
- **Individual pages**: Reset buttons for projects, dataflows, or tasks
- **API**: Reset endpoints for programmatic access

### Q: What's included in the demo data?
**A:** The demo includes:
- 1 Environmental Water Quality Research project
- Sample Python and R scripts
- Realistic data structure
- Full DataLad integration
- Interactive dataflow visualization

### Q: Can I modify the demo data?
**A:** Yes, the demo data is fully functional. You can modify, add, or delete files as needed.

## 🚀 Advanced Usage

### Q: Can I integrate SciTrace with other tools?
**A:** Yes, SciTrace provides a RESTful API for integration with external tools. Check the [API Documentation](../api/README.md) for details.

### Q: Can I use SciTrace in a team environment?
**A:** Yes, SciTrace supports:
- Multiple users
- Project collaboration
- User roles and permissions
- Shared datasets

### Q: Is there a command-line interface?
**A:** Currently, SciTrace is web-based only. A CLI is planned for future versions.

### Q: Can I deploy SciTrace on a server?
**A:** Yes, check the [Deployment Guide](../deployment/README.md) for production deployment instructions.

## 🔒 Security & Privacy

### Q: Is my data secure?
**A:** SciTrace implements several security measures:
- User authentication
- Session management
- Input validation
- Path sanitization
- DataLad's security features

### Q: Where is my data stored?
**A:** Your data is stored locally on your system:
- **Database**: `instance/scitrace.db`
- **Datasets**: In the directories you specify
- **No cloud storage**: Data stays on your machine

### Q: Can I encrypt my datasets?
**A:** Yes, you can use DataLad's encryption features or encrypt your dataset directories using your operating system's encryption tools.

### Q: Is there audit logging?
**A:** Basic logging is available. Comprehensive audit logging is planned for future versions.

## 🆘 Getting Help

### Q: Where can I get help?
**A:** 
1. **Documentation**: Check this FAQ and other documentation
2. **GitHub Issues**: Create an issue in the repository
3. **Community**: Join discussions in the repository
4. **Troubleshooting**: Check the [Troubleshooting Guide](README.md)

### Q: How do I report a bug?
**A:** 
1. Check if it's already reported
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - System information
   - Error messages
   - Screenshots if applicable

### Q: Can I request new features?
**A:** Yes, create an issue with the "enhancement" label. Include:
- Clear description of the feature
- Use case and benefits
- Any relevant examples or mockups

### Q: How often is SciTrace updated?
**A:** SciTrace is actively developed. Updates are released regularly with new features, bug fixes, and improvements.

---

**Still have questions?** Check the [Troubleshooting Guide](README.md) for more detailed help, or create an issue in the repository with your specific question.
