#!/bin/bash

# SciTrace Installation Script
# This script installs and sets up SciTrace

set -e

echo "🚀 SciTrace Installation Script"
echo "====================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Check if DataLad is installed
if ! command -v datalad &> /dev/null; then
    echo "⚠️  DataLad is not installed. Installing DataLad..."
    pip3 install datalad
    echo "✅ DataLad installed"
else
    echo "✅ DataLad found"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create database
echo "🗄️  Initializing database..."
python3 -c "
from scitrace import create_app
from scitrace.models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('Database initialized successfully')
"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start SciTrace:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo "3. Open your browser and go to: http://localhost:5000"
echo "4. Login with: admin / admin123"
echo ""
echo "Happy researching! 🧪"
