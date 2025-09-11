# Installation Guide

This guide will walk you through installing SciTrace on your system. SciTrace is designed to work on macOS, Linux, and Windows systems.

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS 10.14+, Ubuntu 18.04+, Windows 10+
- **Python**: Python 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free disk space
- **Network**: Internet connection for initial setup

### Required Software
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Usually comes with Python
- **Git**: [Download Git](https://git-scm.com/downloads)

**Note**: The installation script will automatically install DataLad if it's not present on your system.

## 🚀 Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install SciTrace is using the provided installation script:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MichelGad/SciTrace
   cd SciTrace
   ```

2. **Run the installation script**:

   **macOS/Linux**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   **Windows**:
   ```bash
   bash install.sh
   ```

3. **Follow the prompts**: The script will guide you through the installation process.

### Method 2: Manual Installation

If you prefer to install manually or need more control over the process:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MichelGad/SciTrace
   cd SciTrace
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   
   **macOS/Linux**:
   ```bash
   source venv/bin/activate
   ```
   
   **Windows**:
   ```bash
   venv\Scripts\activate
   ```

4. **Install DataLad** (if not already installed):
   ```bash
   pip install datalad
   ```

5. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Initialize the database**:
   ```bash
   python run.py
   ```
   (This will create the database and default admin user)

## 🔧 What the Installation Script Does

The automated installation script performs the following steps:

1. **System Check**: Verifies Python 3.8+ and pip are installed
2. **DataLad Installation**: Installs DataLad if not present
3. **Virtual Environment**: Creates an isolated Python environment
4. **Dependencies**: Installs all required Python packages
5. **Database Setup**: Initializes the SQLite database
6. **Default User**: Creates admin user (username: `admin`, password: `admin123`)
7. **Verification**: Tests the installation

## ✅ Verification

After installation, verify everything is working:

1. **Start SciTrace**:
   ```bash
   source venv/bin/activate  # Activate virtual environment
   python run.py
   ```

2. **Access the application**: Open your browser and go to `http://localhost:5001`

3. **Login**: Use the default credentials:
   - Username: `admin`
   - Password: `admin123`

4. **Check the dashboard**: You should see the SciTrace dashboard with project management options.

## 🛠️ Post-Installation Setup

### 1. Change Default Password
For security, change the default admin password:
1. Login to SciTrace
2. Go to your profile (click on your username)
3. Change the password to something secure

### 2. Configure DataLad (Optional)
If you want to use custom DataLad settings:
```bash
# Configure Git (required for DataLad)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Configure DataLad
datalad configuration
```

### 3. Set Up Demo Data (Optional)
To explore SciTrace with sample data:
1. Login to SciTrace
2. Click "Load Demo Projects" on the dashboard
3. This creates sample research projects with DataLad datasets

## 🐛 Troubleshooting

### Common Installation Issues

#### Python Version Issues
**Problem**: "Python 3.8+ required"
**Solution**: 
- Update Python to version 3.8 or higher
- Use `python3` instead of `python` if you have multiple versions

#### Permission Issues
**Problem**: Permission denied errors
**Solution**:
```bash
# macOS/Linux
sudo chmod +x install.sh
./install.sh

# Or run with proper permissions
python3 -m venv venv --user
```

#### DataLad Installation Issues
**Problem**: DataLad installation fails
**Solution**:
```bash
# Install DataLad manually
pip install datalad

# Or use conda
conda install -c conda-forge datalad
```

#### Port Already in Use
**Problem**: "Address already in use" error
**Solution**:
```bash
# Stop any existing Flask processes
python stop_flask.py

# Or manually find and kill the process
lsof -ti:5001 | xargs kill
```

#### Virtual Environment Issues
**Problem**: Virtual environment not activating
**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting Guide](../troubleshooting/README.md)
2. Review the [FAQ](../troubleshooting/faq.md)
3. Search existing issues in the repository
4. Create a new issue with detailed error information

## 🔄 Updating SciTrace

To update to a newer version:

1. **Backup your data** (if you have important projects):
   ```bash
   cp -r instance/ instance_backup/
   ```

2. **Pull the latest changes**:
   ```bash
   git pull origin main
   ```

3. **Update dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```

4. **Restart SciTrace**:
   ```bash
   python run.py
   ```

## 🗑️ Uninstalling SciTrace

To completely remove SciTrace:

1. **Stop the application**:
   ```bash
   python stop_flask.py
   ```

2. **Remove the directory**:
   ```bash
   cd ..
   rm -rf SciTrace
   ```

3. **Remove DataLad datasets** (if you want to clean up demo data):
   ```bash
   rm -rf ~/scitrace_demo_datasets/
   ```

---

**Next Steps**: After installation, check out the [Quick Start Guide](../user-guide/quick-start.md) to begin using SciTrace.
