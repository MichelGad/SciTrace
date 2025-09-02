# SciTrace - Research Data Lineage Platform

A modern web-based platform for managing research data workflows with DataLad integration, interactive dataflow visualization, and comprehensive project management. SciTrace provides researchers with powerful tools to track, manage, and restore their data through an intuitive web interface.

## ✨ Current Features

### 📊 Data Management & DataLad Integration
- **Full DataLad Integration**: Seamless integration with DataLad for robust data versioning and management
- **Interactive Dataflow Visualization**: Click on nodes to view metadata, access files, and explore data relationships
- **File Management**: View file content directly in the browser or download files with one click
- **Automatic Dataset Creation**: New dataflows automatically create properly structured DataLad datasets
- **File Explorer Integration**: Open file locations in your system file explorer directly from the web interface
- **File Restoration**: Restore deleted files from previous commits with enhanced error handling and debugging
- **Web-based DataLad Operations**: Save files and commit changes directly through the web interface - no terminal required
- **Stage Management**: Save entire stages with custom commit messages through the web interface
- **Data Validation**: Basic file format validation and comprehensive metadata management
- **Direct DataLad Access**: Execute DataLad commands through the web interface
- **Commit History Management**: View and manage file commit history through the web interface
- **Real-time Updates**: Dataflow visualization automatically reflects all DataLad changes in real-time

### 👥 Project & Task Management
- **Project Management**: Create and manage research projects with collaborator support
- **Task Tracking**: Track tasks, deadlines, and progress for research projects
- **User Authentication**: Secure login system with role-based access control
- **Dashboard Overview**: Comprehensive statistics and quick access to key functions
- **Project Access Control**: User-based project permissions and access management

### 🛠️ Development & Debugging Tools
- **Data Reset Tools**: Comprehensive tools for development and testing environments
- **Page-Specific Reset**: Individual reset options for projects, tasks, and dataflows
- **Demo Environment**: Quick setup with sample research data for testing and exploration
- **Debug Endpoints**: Built-in debugging tools for troubleshooting DataLad and git operations
- **Enhanced Error Handling**: Clear error messages with debugging information and suggestions

## 🚀 Quick Start

### 📋 Prerequisites
1. **Python**: Python 3.8 or higher
2. **pip**: Python package installer (usually comes with Python)

**Note**: The installation script will automatically install DataLad if it's not present on your system.

### ⚙️ Installation
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

   The installation script will:
   - Check for Python 3.8+ and pip
   - Install DataLad if not present
   - Create a virtual environment
   - Install all dependencies from `requirements.txt`
   - Initialize the database
   - Provide startup instructions

3. **Start the application**:
   ```bash
   source venv/bin/activate
   python run.py
   ```

4. Access at `http://localhost:5001`

## 🔑 Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 🎯 Demo Setup

To quickly explore SciTrace with sample data, you can set up a comprehensive demo environment:

```bash
# Run the complete demo setup
python setup_demo.py
```

This creates a demo DataLad dataset with sample research files in your home directory, allowing you to immediately test all features.

## 📖 Usage Guide

### 📁 Creating a Project
1. Log in to the application
2. Click "Create Project" from the dashboard
3. Fill in project details (name, description, collaborators)
4. The project will be created in the database and ready for use

### 🔄 Creating Dataflows
1. Navigate to the "Dataflows" section
2. Click "Create Dataflow"
3. Select a project and choose storage location
4. The system will automatically create a DataLad dataset and generate an interactive visualization

### 🔍 Interactive Dataflow Exploration
1. View the dataflow as an interactive diagram with color-coded nodes
2. Click on nodes to view metadata, file content, or download files
3. Access files directly in the browser or download them
4. Explore metadata including file sizes, modification dates, and tracking status
5. Open file locations in your system file explorer with one click

### 📎 Adding and Managing Files
1. **Web Interface**: Use the built-in DataLad save functionality directly in the web app
2. **Stage Management**: Save entire stages with commit messages through the web interface
3. **Automatic Updates**: The dataflow visualization automatically reflects all changes
4. **Terminal Alternative**: You can also use DataLad commands in your terminal if preferred

### 🔄 File Restoration
1. Identify deleted files in the dataflow visualization (marked with red indicators)
2. Click the restore button to view available commits
3. Select the commit to restore from
4. The system automatically restores the file and commits the change
5. Enhanced error handling provides clear feedback for any issues

### 🔄 Resetting Data

#### 🌐 Web Interface
- Dashboard: "Reset All Data" button in the user profile dropdown
- Projects Page: "Reset Projects" button
- Tasks Page: "Reset Tasks" button
- Dataflows Page: "Reset Dataflows" button

#### 💻 Command Line
```bash
# List all users and their project counts
python reset_data.py list

# Reset all data for all users
python reset_data.py all

# Reset data for a specific user
python reset_data.py user <user_id>
```

**Warning**: Reset functionality permanently deletes all projects, dataflows, tasks, and their associated DataLad dataset directories.

## 🏗️ Architecture

### ⚙️ Backend
- **Flask Web Framework**: Modern web framework with blueprint architecture
- **SQLAlchemy ORM**: Robust database management with relationship handling
- **Flask-Login**: Secure user authentication and session management
- **Modular Service Architecture**: Separated DataLad and project services for better maintainability
- **Enhanced Error Handling**: Comprehensive error reporting and debugging capabilities

### 🎨 Frontend
- **Bootstrap 5**: Modern, responsive design framework
- **Font Awesome Icons**: Clean, professional iconography
- **Vis.js**: Advanced network visualization for dataflows
- **jQuery**: JavaScript utilities and AJAX integration

### 🗄️ Database Models
- **User**: User accounts, authentication, and profile management
- **Project**: Research projects with metadata and collaborator support
- **Task**: Project tasks with deadlines, status tracking, and priority management
- **Dataflow**: Visual workflow representations with interactive capabilities

## 🔗 DataLad Integration

SciTrace provides comprehensive DataLad integration:

- **Automatic Dataset Creation**: New dataflows automatically create properly structured DataLad datasets
- **File Tree Visualization**: Complete dataset structure with metadata and tracking status
- **Dataflow Generation**: Automatic visualization creation from dataset structure
- **File Content Serving**: View and download files directly through the web interface
- **Metadata Management**: Comprehensive file metadata exploration and management
- **Dynamic File System Integration**: Real-time updates reflecting all DataLad changes
- **Web-based Operations**: All DataLad operations available through the web interface

## 🛠️ Development

### 📁 Project Structure
```
SciTrace/
├── run.py                    # Application entry point
├── install.sh               # Installation script
├── requirements.txt         # Python dependencies
├── setup_demo.py           # Demo data setup script
├── reset_data.py           # Data reset utilities
├── LICENSE                 # Apache License 2.0
├── README.md               # Project documentation
├── .gitignore             # Git ignore rules
├── instance/               # Instance-specific files (database, etc.)
├── venv/                   # Virtual environment
└── scitrace/               # Main application package
    ├── __init__.py         # Package initialization
    ├── app.py              # Flask application factory
    ├── models.py           # Database models and relationships
    ├── services.py         # Backward compatibility layer
    ├── datalad_services.py # DataLad operations and dataset management
    ├── project_services.py # Project management and file restoration
    ├── routes/             # Route blueprints
    │   ├── __init__.py     # Routes package initialization
    │   ├── auth.py         # Authentication routes
    │   ├── dashboard.py    # Dashboard routes
    │   ├── projects.py     # Project management
    │   ├── dataflow.py     # Dataflow visualization and file serving
    │   ├── tasks.py        # Task management
    │   └── api.py          # API endpoints including debug and restore functionality
    ├── templates/          # HTML templates
    │   ├── base.html       # Base template with responsive design
    │   ├── auth/           # Authentication templates
    │   │   ├── login.html
    │   │   ├── register.html
    │   │   └── profile.html
    │   ├── dashboard/      # Dashboard templates
    │   │   └── index.html
    │   ├── projects/       # Project templates
    │   │   ├── index.html
    │   │   ├── create.html
    │   │   ├── edit.html
    │   │   ├── view.html
    │   │   └── create_task.html
    │   ├── tasks/          # Task templates
    │   │   ├── index.html
    │   │   ├── create.html
    │   │   ├── edit.html
    │   │   └── view.html
    │   └── dataflow/       # Dataflow templates
    │       ├── index.html
    │       ├── create.html
    │       ├── edit.html
    │       └── view.html
    └── assets/             # Static assets
        ├── js/             # JavaScript files
        │   └── vis.min.js
        └── css/            # CSS files
            └── vis.min.css
```

### 🔧 Key Features Implementation

#### 🔍 Interactive Dataflow Visualization
- **Node Click Handling**: JavaScript event listeners for interactive node exploration
- **Modal System**: Rich modal dialogs for displaying node details and file content
- **File Serving Routes**: Direct file content and metadata access
- **AJAX Integration**: Dynamic content loading without page refreshes
- **File Explorer Integration**: One-click access to file locations

#### 📊 Data Management
- **DataLad Dataset Creation**: Automatic dataset setup with proper structure
- **File Tree Visualization**: Complete dataset exploration with metadata
- **Dynamic File Content Serving**: Real-time file access and download
- **Metadata Exploration**: Comprehensive file information display

### ➕ Adding New Features
1. Add new routes in the appropriate blueprint
2. Define new database models in `models.py`
3. Add business logic in the appropriate service file (`datalad_services.py` or `project_services.py`)
4. Create HTML templates in the appropriate directory
5. Add CSS/JS files to the static directory

## 🗺️ Roadmap

### Version 2.0 - Interactive Research Platform (Coming Soon)

#### 📤 Direct Data Upload & Management
- **Drag & Drop Interface**: Upload files and datasets directly through the web interface
- **Batch Upload**: Support for multiple file uploads with progress tracking
- **Data Validation**: Automatic validation of uploaded data formats and structures
- **Storage Management**: Integrated storage management with DataLad datasets
- **Custom Project Location**: Choose where to set up your project on your local drive for better organization

#### 🔧 Interactive Code Execution
- **Built-in Code Editor**: Web-based code editor with syntax highlighting
- **DataLad Function Integration**: Direct access to DataLad commands through the interface
- **Script Management**: Create, edit, and manage Python/R scripts within projects
- **Execution Environment**: Secure code execution environment with resource monitoring

#### 🔍 Advanced Traceability & Analysis
- **Run Function Integration**: Execute code and automatically trace output files
- **Dependency Tracking**: Automatic tracking of data dependencies and transformations
- **Execution History**: Complete history of code runs with input/output mapping
- **Performance Monitoring**: Track execution time and resource usage

#### 📊 Enhanced Visualization & Reporting
- **Real-time Dataflow Updates**: Live updates to dataflow visualization as code executes
- **Execution Graphs**: Visual representation of code execution and data transformations
- **Interactive Reports**: Generate and export comprehensive research reports
- **Collaborative Features**: Real-time collaboration on research workflows
- **Data Lifecycle Visualization**: Interactive view of data through its complete lifecycle
- **Git-like Log View**: Interactive commit history visualization with branching and merging display

#### 🔐 Advanced Security & Access Control
- **Role-based Permissions**: Granular access control for different user roles
- **Execution Sandboxing**: Secure code execution with resource limits
- **Audit Logging**: Comprehensive logging of all user actions and code executions
- **Data Encryption**: Enhanced security for sensitive research data

### Future Enhancements
- **AI-Powered Insights**: Machine learning recommendations for data analysis
- **Integration APIs**: RESTful APIs for external tool integration
- **Cloud Deployment**: Multi-cloud deployment options
- **Advanced Analytics**: Built-in statistical analysis and visualization tools

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact me

## 🙏 Acknowledgments
- Built on top of **DataLad** for robust data management
- Inspired by modern research data management needs
- Uses open-source libraries and frameworks
- Designed for researchers and data scientists

