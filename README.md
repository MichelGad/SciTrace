# SciTrace - Research Data Lineage Platform

**Version 0.1.0** | **Released: September 2025**

A modern, production-ready web-based platform for managing research data workflows with comprehensive DataLad integration, interactive dataflow visualization, and advanced project management. SciTrace provides researchers with powerful tools to track, manage, and restore their data through an intuitive web interface.

## ✨ Key Features

### 📊 Data Management & DataLad Integration
- **Full DataLad Integration**: Seamless integration with DataLad for robust data versioning and management
- **Interactive Dataflow Visualization**: Click on nodes to view metadata, access files, and explore data relationships
- **File Management**: View file content directly in the browser or download files with one click
- **Enhanced File Operations**: Robust file path handling and reliable file addition to DataLad datasets
- **Automatic Dataset Creation**: New dataflows automatically create properly structured DataLad datasets using `datalad create`
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
- **Data Reset Tools**: Comprehensive tools for development and testing environments with complete filesystem cleanup
- **Page-Specific Reset**: Individual reset options for projects, tasks, and dataflows
- **Demo Environment**: Quick setup with sample research data for testing and exploration
- **Debug Endpoints**: Built-in debugging tools for troubleshooting DataLad and git operations
- **Enhanced Error Handling**: Clear error messages with debugging information and suggestions
- **Web-based Shutdown**: One-click Flask application shutdown via web interface with confirmation dialog

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

### 🔧 DataLad Installation

SciTrace requires DataLad for data management functionality. DataLad is a data management tool, so we recommend installing it wherever you'll be working with actual data. This may not be your laptop, but a server that you connect to with your laptop. In that case, please consider installing DataLad on that server. Installation on such systems does not require administrator privileges and works with regular user accounts.

#### Step 1: DataLad needs Git

Many systems have Git already installed. Try running `git --version` in a terminal to check.

If you do not have Git installed, visit https://git-scm.com/downloads, pick your operating system, download, and run the Git installer.

If you are using Conda, Brew, or a system with another package manager, there are simpler ways to install Git, and you likely know how.

#### Step 2: Install UV

UV is a smart little helper that is available for all platforms and offers the simplest way to install DataLad. DataLad is written in Python and UV takes care of automatically creating the right environment for DataLad to run, whether or not you know or have Python already.

Visit https://docs.astral.sh/uv/getting-started/installation/#standalone-installer and run the standalone installer. Experts can also use any other method listed on that page.

#### Step 3: Install git-annex

With UV installed, you can now install the git-annex software, a core tool that DataLad builds upon. Run:

```bash
uv tool install git-annex
```

Afterwards run:

```bash
git annex version
```

to verify that you have a functional installation.

#### Step 4: Install DataLad

DataLad is installed exactly like git-annex. However, we also install a particular DataLad extension package, like so:

```bash
uv tool install datalad --with datalad-container --with-executables-from datalad-next
git config --global --add datalad.extensions.load next
```

Verify the installation by running:

```bash
datalad wtf
```

(it should report all kinds of information on your system).

### ⚙️ SciTrace Installation
1. **Clone the repository**:
   ```bash
   git clone https://codeberg.org/MichelGad/SciTrace.git
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

### 🛑 Stopping the Flask Application

There are multiple ways to stop the Flask application:

#### 🌐 **Web Interface (Recommended)**
- **Shutdown Button**: Click the red power button (⚡) in the top navigation bar next to your user profile
- **Confirmation**: A dialog will ask for confirmation before shutting down
- **Automatic**: Uses the `stop_flask.py` script automatically
- **User-Friendly**: No terminal commands required

#### 💻 **Command Line**
If you need to stop the Flask application from the terminal (for example, when you get an "Address already in use" error), you can use the provided `stop_flask.py` script:

```bash
python3 stop_flask.py
```

This script will:
- Automatically find any process running on port 5001
- Stop it without requiring manual port checking
- Provide feedback about what it's doing

**Alternative**: You can also manually stop the process by finding the PID and killing it:
```bash
lsof -ti:5001 | xargs kill
```

## 🔑 Default Login
- **Username**: `admin`
- **Password**: `admin123`

## 🎯 Demo Setup

To quickly explore SciTrace with sample data, you can set up a focused demo environment using the DataLad-based demo system:

1. **Start SciTrace**: Run `python run.py` and access the application
2. **Login**: Use admin/admin123 credentials
3. **Click "Load Demo Projects"**: Use the button in the dashboard
4. **Automatic Setup**: The system will create 1 Environmental Water Quality Research dataset automatically

This creates **1 comprehensive Environmental Water Quality Research dataset** with proper DataLad integration:

### 🌊 **Environmental Water Quality Research Dataset**
- **Structure**: Water quality parameters, environmental monitoring data
- **Files**: Data cleaning scripts, statistical analysis, visualization tools
- **Creation**: `datalad create` (simple, clean dataset without nested subdatasets)
- **Focus**: Comprehensive water quality analysis across multiple sampling sites

### 🚀 **What You Get**
- **Professional Research Structure**: Realistic environmental research directory organization
- **Sample Scripts**: Python and R scripts for water quality data analysis
- **DataLad Integration**: Full version control and data lineage tracking
- **Interactive Visualization**: Ready-to-explore environmental dataflow in SciTrace
- **Demo Badges**: Clear identification of demo project throughout the interface

The demo dataset is created in `~/scitrace_demo_datasets/` and provides a comprehensive testing environment for all SciTrace features focused on environmental research.

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
- **Modular API Architecture**: Organized API endpoints into focused modules for improved maintainability
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

SciTrace follows a modern, modular architecture designed for scalability and maintainability:

```
SciTrace/
├── 📄 Core Application Files
│   ├── run.py                    # 🚀 Application entry point - starts Flask server
│   ├── install.sh               # ⚙️ Automated installation script for all platforms
│   ├── stop_flask.py            # 🛑 Graceful Flask application shutdown utility
│   ├── requirements.txt         # 📦 Python dependencies and versions
│   ├── setup_demo_datalad.py   # 🎯 DataLad-based demo environment setup
│   ├── reset_data.py           # 🔄 Development data reset utilities
│   ├── LICENSE                 # 📜 Apache License 2.0
│   ├── README.md               # 📖 Main project documentation
│   └── server.log              # 📊 Application runtime logs
│
├── 📁 Documentation & Resources
│   ├── docs/                   # 📚 Comprehensive documentation
│   │   ├── README.md           # Main documentation hub
│   │   ├── CHANGELOG.md        # Version history and changes
│   │   ├── api/                # API documentation
│   │   │   ├── README.md       # Complete API reference
│   │   │   ├── CHANGELOG.md    # API version history
│   │   │   └── error-handling.md # Error handling guide
│   │   ├── user-guide/         # User documentation
│   │   │   ├── quick-start.md  # Getting started guide
│   │   │   ├── features.md     # Feature overview
│   │   │   ├── project-management.md # Project management guide
│   │   │   └── datalad-integration.md # DataLad integration guide
│   │   ├── developer/          # Developer documentation
│   │   │   ├── architecture.md # System architecture
│   │   │   └── README.md       # Development setup
│   │   ├── installation/       # Installation guides
│   │   ├── deployment/         # Deployment documentation
│   │   ├── contributing/       # Contribution guidelines
│   │   ├── troubleshooting/    # FAQ and troubleshooting
│   │   └── glossary.md         # Technical terms and definitions
│   │
│   └── demo_scripts/           # 🎭 Sample analysis scripts
│       ├── sample_analysis.py  # Python analysis example
│       ├── sample_analysis.R   # R analysis example
│       ├── sample_data.csv     # Sample dataset
│       └── sample_r_data.csv   # R-specific sample data
│
├── 🗄️ Data & Configuration
│   ├── instance/               # 💾 Instance-specific data
│   │   └── scitrace.db        # SQLite database file
│   └── venv/                   # 🐍 Python virtual environment
│
└── 🏗️ Main Application Package (scitrace/)
    ├── 📄 Core Application
    │   ├── __init__.py         # Package initialization
    │   ├── app.py              # 🏭 Flask application factory
    │   ├── models.py           # 🗃️ Database models and relationships
    │   └── exceptions.py       # ⚠️ Custom exception definitions
    │
    ├── ⚙️ Configuration Management
    │   └── config/             # 🔧 Application configuration
    │       ├── __init__.py     # Config package initialization
    │       ├── config.py       # Main configuration settings
    │       └── settings.py     # Environment-specific settings
    │
    ├── 🏛️ Repository Layer (Data Access)
    │   └── repositories/       # 📊 Data access layer
    │       ├── __init__.py     # Repository package initialization
    │       ├── base_repository.py     # 🏗️ Base repository with common operations
    │       ├── user_repository.py     # 👤 User data access
    │       ├── project_repository.py  # 📁 Project data access
    │       ├── task_repository.py     # ✅ Task data access
    │       └── dataflow_repository.py # 🔄 Dataflow data access
    │
    ├── 🔧 Service Layer (Business Logic)
    │   └── services/           # 🎯 Business logic and operations
    │       ├── __init__.py     # Services package initialization
    │       ├── base_service.py         # 🏗️ Base service with common functionality
    │       ├── project_service.py      # 📁 Project management services
    │       ├── project_management.py   # 📋 Project lifecycle management
    │       ├── dataset_creation.py     # 🆕 Dataset creation and initialization
    │       ├── dataset_integration.py  # 🔗 Dataset integration and management
    │       ├── file_operations.py      # 📄 File operations and management
    │       ├── git_operations.py       # 🌿 Git operations and version control
    │       └── metadata_operations.py  # 📊 Metadata management and operations
    │
    ├── 🛠️ Utility Layer
    │   └── utils/              # 🔧 Utility functions and helpers
    │       ├── __init__.py     # Utils package initialization
    │       ├── api_validation.py       # ✅ API request validation
    │       ├── auth_helpers.py         # 🔐 Authentication helper functions
    │       ├── datalad_utils.py        # 📦 DataLad operation utilities
    │       ├── file_utils.py           # 📄 File system utilities
    │       ├── flash_utils.py          # 💬 Flash message utilities
    │       ├── logging_utils.py        # 📊 Logging configuration
    │       ├── path_validation.py      # 🛡️ Path validation and security
    │       ├── response_utils.py       # 📤 API response formatting
    │       └── validation_utils.py     # ✅ General validation utilities
    │
    ├── 🌐 Route Layer (Web Interface)
    │   └── routes/             # 🛣️ Web routes and API endpoints
    │       ├── __init__.py     # Routes package initialization
    │       ├── auth.py         # 🔐 Authentication routes (login, register)
    │       ├── dashboard.py    # 📊 Dashboard and overview routes
    │       ├── projects.py     # 📁 Project management routes
    │       ├── dataflow.py     # 🔄 Dataflow visualization routes
    │       ├── tasks.py        # ✅ Task management routes
    │       ├── api_old.py      # 📜 Legacy API (backward compatibility)
    │       └── api/            # 🚀 Modern modular API endpoints
    │           ├── __init__.py     # API package initialization
    │           ├── admin_api.py     # 👑 Admin operations and demo setup
    │           ├── dataflow_api.py  # 🔄 Dataflow-related API endpoints
    │           ├── file_api.py      # 📄 File operations API endpoints
    │           ├── git_api.py       # 🌿 Git operations API endpoints
    │           └── project_api.py   # 📁 Project-related API endpoints
    │
    ├── 🎨 Frontend Assets
    │   ├── assets/             # 📦 Third-party assets
    │   │   ├── js/             # JavaScript libraries
    │   │   │   └── vis.min.js  # Vis.js network visualization library
    │   │   └── css/            # CSS libraries
    │   │       └── vis.min.css # Vis.js styling
    │   │
    │   └── static/             # 🎨 Custom static assets
    │       ├── css/            # Custom stylesheets
    │       │   └── utils/      # Modular CSS utilities
    │       │       ├── colors.css        # Color scheme definitions
    │       │       ├── components.css    # Reusable component styles
    │       │       ├── error-boundaries.css # Error handling styles
    │       │       ├── layout.css        # Layout and grid systems
    │       │       └── scitrace-utils.css # SciTrace-specific utilities
    │       └── js/             # Custom JavaScript
    │           └── utils/      # Modular JavaScript utilities
    │               ├── api.js             # API communication utilities
    │               ├── error-handling.js  # Client-side error handling
    │               ├── forms.js           # Form validation and handling
    │               ├── scitrace-utils.js  # SciTrace-specific utilities
    │               ├── ui.js              # User interface utilities
    │               └── visualization.js   # Dataflow visualization logic
    │
    └── 📄 Templates (HTML Views)
        └── templates/          # 🖼️ HTML templates and views
            ├── base.html       # 🏗️ Base template with responsive design
            ├── auth/           # 🔐 Authentication templates
            │   ├── login.html      # User login page
            │   ├── register.html   # User registration page
            │   └── profile.html    # User profile management
            ├── dashboard/      # 📊 Dashboard templates
            │   └── index.html      # Main dashboard view
            ├── projects/       # 📁 Project management templates
            │   ├── index.html      # Project listing
            │   ├── create.html     # Project creation form
            │   ├── edit.html       # Project editing form
            │   ├── view.html       # Project detail view
            │   └── create_task.html # Task creation form
            ├── tasks/          # ✅ Task management templates
            │   ├── index.html      # Task listing
            │   ├── create.html     # Task creation form
            │   ├── edit.html       # Task editing form
            │   └── view.html       # Task detail view
            ├── dataflow/       # 🔄 Dataflow visualization templates
            │   ├── index.html      # Dataflow listing
            │   ├── create.html     # Dataflow creation form
            │   ├── edit.html       # Dataflow editing form
            │   ├── view.html       # Interactive dataflow visualization
            │   ├── lifecycle.html  # Data lifecycle conceptual view
            │   └── git_log.html    # Git log visualization interface
            └── partials/       # 🧩 Reusable template components
                ├── _demo_badge.html        # Demo project indicators
                ├── _demo_info_alert.html   # Demo information alerts
                ├── _empty_state.html       # Empty state placeholders
                ├── _empty_state_error.html # Error state placeholders
                ├── _error_boundary.html    # Error boundary components
                ├── _form_error.html        # Form error displays
                ├── _loading_error.html     # Loading error displays
                ├── _priority_badge.html    # Task priority indicators
                ├── _project_card.html      # Project card components
                ├── _stats_card.html        # Statistics display cards
                ├── _status_badge.html      # Status indicators
                └── _task_row.html          # Task row components
```

### 🏗️ Architecture Overview

SciTrace follows a **layered architecture** with clear separation of concerns:

#### 🔄 **Data Flow Architecture**
1. **🌐 Frontend Layer**: Templates + Static Assets (User Interface)
2. **🛣️ Route Layer**: Web routes and API endpoints (Request Handling)
3. **🔧 Service Layer**: Business logic and operations (Core Functionality)
4. **🏛️ Repository Layer**: Data access and database operations (Data Persistence)
5. **🗃️ Model Layer**: Database models and relationships (Data Structure)

#### 🎯 **Key Design Principles**
- **📦 Modular Design**: Each component has a single responsibility
- **🔄 Separation of Concerns**: Clear boundaries between layers
- **🛡️ Security First**: Path validation and input sanitization
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring
- **🎨 Responsive UI**: Modern, mobile-friendly interface
- **🔧 Extensible**: Easy to add new features and modules

## 🆕 Version 0.1.0 - Stable Release

### 🏗️ Production-Ready Architecture
SciTrace 0.1.0 features a modern, modular architecture designed for production use:

#### ✨ **Modular API Structure**
- **Focused API Modules**: Specialized modules for different functionality:
  - `dataflow_api.py`: Dataflow-related operations and file management
  - `git_api.py`: Git operations, commit history, and version control
  - `file_api.py`: File operations, directory browsing, and file management
  - `admin_api.py`: Demo setup, system operations, and data reset
  - `project_api.py`: Project-related operations and management
- **Improved Maintainability**: Each API module focuses on specific functionality
- **Better Code Organization**: Clear separation of concerns and responsibilities
- **Enhanced Error Handling**: Specialized error handling for each API domain

#### 🔧 **Enhanced Service Layer**
- **Modular Services**: Organized service layer with specialized modules:
  - `FileOperationsService`: File management and DataLad integration
  - `GitOperationsService`: Git operations and version control
  - `ProjectManagementService`: Project lifecycle management
  - `DatasetCreationService`: Dataset initialization and setup
  - `MetadataOperationsService`: Metadata management and operations
- **Base Service Class**: Common functionality shared across all services
- **Utility Modules**: Comprehensive utility layer for validation, authentication, and operations

#### 🛠️ **Technical Improvements**
- **Blueprint Architecture**: Proper Flask blueprint organization for scalable routing
- **Service-Oriented Design**: Clean separation between API endpoints and business logic
- **Enhanced Error Handling**: Comprehensive error reporting with debugging information
- **Improved File Path Handling**: Fixed file path construction issues for better reliability
- **Robust DataLad Integration**: Enhanced DataLad operations with proper error handling

#### 🎯 **Benefits of Production Architecture**
- **Maintainability**: Easier to maintain and extend individual components
- **Scalability**: Modular design supports future feature additions
- **Debugging**: Clear separation makes troubleshooting more efficient
- **Testing**: Individual modules can be tested in isolation
- **Code Reusability**: Services can be reused across different API endpoints
- **Performance**: Optimized error handling and response formatting

#### 🐛 **Stability Improvements**
- **File Path Construction Fix**: Resolved "File does not exist" errors when adding files to DataLad
- **Enhanced File Operations**: Improved file path handling using actual directory names vs display names
- **Robust DataLad Integration**: Fixed symbolic link handling for script execution
- **Improved Error Messages**: Better error reporting and debugging information
- **Enhanced Reset Functionality**: Comprehensive dataset cleanup including filesystem removal

## 🗺️ Roadmap

### Version 1.1 - Enhanced User Experience (Planned)

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

#### 📊 Enhanced Visualization & Reporting
- **Real-time Dataflow Updates**: Live updates to dataflow visualization as code executes
- **Execution Graphs**: Visual representation of code execution and data transformations
- **Interactive Reports**: Generate and export comprehensive research reports
- **Collaborative Features**: Real-time collaboration on research workflows
- **Data Lifecycle Visualization**: Interactive view of data through its complete lifecycle  


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

---

**SciTrace 0.1.0** - *Released September 2025* | *Production Ready*