# SciTrace - Research Data Lineage Platform

A modern web-based platform for managing research data workflows with DataLad integration, interactive dataflow visualization, and comprehensive project management. SciTrace provides researchers with powerful tools to track, manage, and restore their data through an intuitive web interface.

## ✨ Current Features

### 📊 Data Management & DataLad Integration
- **Full DataLad Integration**: Seamless integration with DataLad for robust data versioning and management
- **Interactive Dataflow Visualization**: Click on nodes to view metadata, access files, and explore data relationships
- **File Management**: View file content directly in the browser or download files with one click
- **Automatic Dataset Creation**: New dataflows automatically create properly structured DataLad datasets using `create-test-dataset`
- **Research Type Selection**: Choose from Environmental, Biomedical, Computational, or General research structures
- **Professional Directory Organization**: Automatic creation of `raw_data`, `scripts`, `results`, and `plots` directories
- **File Explorer Integration**: Open file locations in your system file explorer directly from the web interface
- **File Restoration**: Restore deleted files from previous commits with enhanced error handling and debugging
- **Web-based DataLad Operations**: Save files and commit changes directly through the web interface - no terminal required
- **Stage Management**: Save entire stages with custom commit messages through the web interface
- **Data Validation**: Basic file format validation and comprehensive metadata management
- **Direct DataLad Access**: Execute DataLad commands through the web interface
- **Commit History Management**: View and manage file commit history through the web interface
- **Git Log Visualization**: Interactive git log view with unified single-tab interface, real file diff support, and tree visualization
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

### 🔍 Git Log & Version Control Features
- **Unified Interface**: Single-tab design combining commit information and file changes
- **Real File Diffs**: Actual Git diff content with proper syntax highlighting and formatting
- **Tree Visualization**: Interactive commit tree showing branching and merging patterns
- **Streamlined Layout**: Single-line commit display with avatar, author, hash, date, and message
- **Smart File Tree**: Left panel showing changed files with status indicators (added, modified, deleted)
- **Live Diff View**: Right panel displaying real-time file differences as you select files
- **Enhanced Actions**: Right-aligned Copy Hash and Revert buttons for better UX
- **No Duplication**: Eliminated redundant information display for cleaner interface

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

To quickly explore SciTrace with sample data, you can set up a comprehensive demo environment using the new DataLad-based demo system:

1. **Start SciTrace**: Run `python run.py` and access the application
2. **Login**: Use admin/admin123 credentials
3. **Click "Load Demo Projects"**: Use the button in the dashboard
4. **Automatic Setup**: The system will create 3 realistic research datasets automatically

This creates **3 realistic research datasets** with proper DataLad integration:

### 🌊 **Environmental Research Dataset**
- **Structure**: Water quality, air quality, soil samples
- **Files**: Data cleaning scripts, statistical analysis, visualization tools
- **Spec**: `datalad create-test-dataset --spec "3-5/2-4" --seed 42`

### 🏥 **Biomedical Research Dataset**
- **Structure**: Patient records, lab results, clinical data
- **Files**: Data preprocessing, statistical tests, machine learning scripts
- **Spec**: `datalad create-test-dataset --spec "4-6/2-3" --seed 123`

### 🤖 **Computational Research Dataset**
- **Structure**: Training data, validation data, model evaluation
- **Files**: Model training, hyperparameter tuning, evaluation scripts
- **Spec**: `datalad create-test-dataset --spec "2-4/3-5" --seed 456`

### 🚀 **What You Get**
- **Professional Research Structure**: Realistic directory organization
- **Sample Scripts**: Python and R scripts for data analysis
- **DataLad Integration**: Full version control and data lineage tracking
- **Interactive Visualization**: Ready-to-explore dataflows in SciTrace
- **Demo Badges**: Clear identification of demo projects throughout the interface

The demo datasets are created in `~/scitrace_demo_datasets/` and provide a comprehensive testing environment for all SciTrace features.

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

### 📜 Git Log Visualization
1. Access the git log from any dataflow via the "Git Log" button
2. View commit history in a beautiful timeline format with tree visualization
3. **Unified Single-Tab Interface**: Combined commit information and file changes in one view
4. **Real File Diff Support**: View actual Git diff content instead of placeholder text
5. **Single-Line Commit Display**: Clean format showing avatar, author, hash, date, and message
6. **Right-Aligned Actions**: Copy Hash and Revert buttons positioned on the right side
7. **Interactive File Tree**: Left panel showing changed files with status indicators
8. **Live Diff View**: Right panel displaying real-time file differences
9. **Enhanced UX**: No duplicate information, streamlined interface, better space utilization
10. **Advanced Git Operations**: 
    - **Copy Hash**: Copy commit hash to clipboard
    - **View Files**: See exactly what files were modified in each commit
    - **Revert Commit**: Undo changes by creating a revert commit

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
- Dashboard: "Reset All Data" button in the user profile dropdown
- Projects Page: "Reset Projects" button
- Tasks Page: "Reset Tasks" button
- Dataflows Page: "Reset Dataflows" button

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
├── setup_demo_datalad.py   # New DataLad-based demo setup script
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
    │       └── dataflow/       # Dataflow templates
    │       ├── index.html
    │       ├── create.html
    │       ├── edit.html
    │       ├── view.html
    │       ├── lifecycle.html  # Data lifecycle conceptual workflow view
    │       └── git_log.html  # Git log visualization with unified interface
    └── assets/             # Static assets
        ├── js/             # JavaScript files
        │   └── vis.min.js
        └── css/            # CSS files
            └── vis.min.css
```

## 🆕 Recent Updates (Latest Version)

### 🎉 Major UI Overhaul & New Data Lifecycle View
SciTrace has undergone significant improvements with a new dedicated view and comprehensive UI standardization:

#### ✨ **New Features**
- **Data Lifecycle View**: Dedicated conceptual workflow visualization separate from repository structure
- **Interactive Workflow Stages**: Click on stages to view detailed research process descriptions
- **Unified Git Log Interface**: Single-tab design with real file diffs and streamlined commit display
- **Consistent Navigation**: Standardized "Repo View", "Data Lifecycle", and "Git Log" terminology

#### 🎨 **UI Improvements**
- **Header Standardization**: Consistent styling and iconography across all dataflow views
- **Icon Consistency**: Matching Font Awesome icons (fa-folder-tree, fa-sitemap, fa-code-branch)
- **Cleaner Interface**: Removed cluttered elements and improved visual hierarchy
- **Professional Design**: Bootstrap-standard containers and responsive layouts

#### 🔧 **Technical Enhancements**
- **New Route**: `/dataflow/<id>/lifecycle` for dedicated lifecycle visualization
- **Real File Diffs**: Actual Git diff content with proper syntax highlighting
- **Enhanced Navigation**: Improved button placement and user flow
- **Better Error Handling**: User-friendly messages and loading states

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
- **Data Lifecycle Visualization**: Interactive view of data through its complete lifecycle  ✅ **COMPLETED**
- **Git-like Log View**: Interactive commit history visualization  ✅ **COMPLETED**

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

