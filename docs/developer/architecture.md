# Architecture Overview

This document provides a comprehensive overview of SciTrace's architecture, including system design, components, and their interactions.

## 🏗️ System Architecture

SciTrace follows a modern, modular architecture designed for scalability, maintainability, and extensibility.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SciTrace Application                     │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer (Templates + Static Assets)                │
│  ├── HTML Templates (Jinja2)                               │
│  ├── CSS (Bootstrap 5 + Custom)                            │
│  ├── JavaScript (jQuery + Custom Modules)                  │
│  └── Third-party Assets (Vis.js, Font Awesome)             │
├─────────────────────────────────────────────────────────────┤
│  Web Layer (Flask Routes + Blueprints)                     │
│  ├── Authentication Routes                                  │
│  ├── Dashboard Routes                                       │
│  ├── Project Management Routes                              │
│  ├── Dataflow Routes                                        │
│  ├── Task Management Routes                                 │
│  └── API Routes (RESTful)                                  │
├─────────────────────────────────────────────────────────────┤
│  Service Layer (Business Logic)                            │
│  ├── Project Management Service                             │
│  ├── Dataset Creation Service                               │
│  ├── File Operations Service                                │
│  ├── Git Operations Service                                 │
│  ├── Metadata Operations Service                            │
│  └── Base Service (Common Functionality)                   │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ├── Database (SQLite/PostgreSQL)                          │
│  ├── File System (DataLad Datasets)                        │
│  └── Git Repositories                                       │
├─────────────────────────────────────────────────────────────┤
│  External Integrations                                      │
│  ├── DataLad (Data Management)                             │
│  ├── Git (Version Control)                                 │
│  └── File System (OS Integration)                          │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Component Architecture

### 1. Web Layer (Flask Routes)

The web layer handles HTTP requests and responses using Flask blueprints for modular organization.

#### Blueprint Structure
```
routes/
├── auth.py              # Authentication and user management
├── dashboard.py         # Main dashboard and overview
├── projects.py          # Project management
├── dataflow.py          # Dataflow visualization and management
├── tasks.py             # Task management
└── api/                 # RESTful API endpoints
    ├── dataflow_api.py  # Dataflow-related API
    ├── git_api.py       # Git operations API
    ├── file_api.py      # File operations API
    ├── admin_api.py     # Admin and system operations
    └── project_api.py   # Project-related API
```

#### Route Responsibilities
- **Authentication**: User login, logout, registration, profile management
- **Dashboard**: Main application dashboard with statistics and quick actions
- **Projects**: Project creation, editing, deletion, and management
- **Dataflows**: Dataflow visualization, file management, and DataLad operations
- **Tasks**: Task creation, assignment, tracking, and completion
- **API**: RESTful endpoints for AJAX operations and external integrations

### 2. Service Layer (Business Logic)

The service layer contains the core business logic, separated from the web layer for better maintainability and testability.

#### Service Architecture
```
services/
├── base_service.py           # Base service with common functionality
├── project_management.py     # Project lifecycle management
├── dataset_creation.py       # DataLad dataset creation and setup
├── dataset_integration.py    # Dataset integration and management
├── file_operations.py        # File system operations
├── git_operations.py         # Git and version control operations
├── metadata_operations.py    # Metadata management
└── project_service.py        # Project-specific services
```

#### Service Responsibilities
- **Project Management**: Project creation, updates, deletion, and collaboration
- **Dataset Operations**: DataLad dataset creation, configuration, and management
- **File Operations**: File upload, download, organization, and validation
- **Git Operations**: Commit management, branch operations, and history tracking
- **Metadata Management**: File metadata extraction, validation, and storage

### 3. Data Layer

The data layer manages data persistence and external system integration.

#### Database Models
```
models.py
├── User                    # User accounts and authentication
├── Project                 # Research projects
├── Task                    # Project tasks and deadlines
└── Dataflow               # Dataflow representations
```

#### Data Relationships
- **User** → **Project** (One-to-Many): Users can have multiple projects
- **Project** → **Dataflow** (One-to-Many): Projects can have multiple dataflows
- **Project** → **Task** (One-to-Many): Projects can have multiple tasks
- **User** → **Task** (One-to-Many): Users can be assigned multiple tasks

### 4. Utility Layer

The utility layer provides common functionality used across the application.

#### Utility Modules
```
utils/
├── api_validation.py      # API request validation
├── auth_helpers.py        # Authentication helper functions
├── datalad_utils.py       # DataLad operation utilities
├── file_utils.py          # File system utilities
├── flash_utils.py         # Flash message utilities
├── logging_utils.py       # Logging configuration
├── path_validation.py     # Path validation and security
├── response_utils.py      # API response formatting
└── validation_utils.py    # General validation utilities
```

## 🔄 Data Flow Architecture

### 1. User Request Flow

```
User Request → Flask Route → Service Layer → Data Layer → Response
     ↓              ↓            ↓            ↓           ↓
  Browser      Route Handler  Business    Database    JSON/HTML
  Interface    (Blueprint)    Logic       Models      Response
```

### 2. DataLad Integration Flow

```
User Action → Web Interface → Service Layer → DataLad → File System
     ↓             ↓              ↓            ↓           ↓
  Click Save   JavaScript      File Ops    DataLad     Dataset
  Button       AJAX Call       Service     Commands    Update
```

### 3. Dataflow Visualization Flow

```
Dataset → Service Layer → Data Processing → Visualization → User Interface
   ↓           ↓              ↓                ↓              ↓
DataLad    Metadata Ops    File Analysis   Network Graph   Interactive
Dataset    Service         & Processing    Generation      Display
```

## 🎨 Frontend Architecture

### Template Structure
```
templates/
├── base.html              # Base template with common layout
├── auth/                  # Authentication templates
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── dashboard/             # Dashboard templates
│   └── index.html
├── projects/              # Project management templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   ├── view.html
│   └── create_task.html
├── dataflow/              # Dataflow templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   ├── view.html
│   ├── lifecycle.html
│   └── git_log.html
├── tasks/                 # Task management templates
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   └── view.html
└── partials/              # Reusable template components
    ├── _project_card.html
    ├── _stats_card.html
    ├── _status_badge.html
    └── _error_boundary.html
```

### Static Assets Structure
```
static/
├── css/
│   └── utils/             # Custom CSS utilities
│       ├── colors.css
│       ├── components.css
│       ├── layout.css
│       └── scitrace-utils.css
└── js/
    └── utils/             # JavaScript utility modules
        ├── api.js
        ├── error-handling.js
        ├── forms.js
        ├── scitrace-utils.js
        ├── ui.js
        └── visualization.js
```

### JavaScript Architecture
- **Modular Design**: JavaScript code is organized into focused modules
- **jQuery Integration**: Uses jQuery for DOM manipulation and AJAX calls
- **Event Handling**: Centralized event handling for better maintainability
- **Error Handling**: Comprehensive error handling with user-friendly messages

## 🔐 Security Architecture

### Authentication & Authorization
- **Flask-Login**: Session-based authentication
- **Password Hashing**: Werkzeug password hashing
- **Role-Based Access**: User roles and permissions
- **Session Management**: Secure session handling

### Data Security
- **Path Validation**: Prevents directory traversal attacks
- **Input Validation**: Comprehensive input validation and sanitization
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **XSS Prevention**: Template escaping and content security

### File Security
- **File Type Validation**: Validates file types and extensions
- **Path Sanitization**: Sanitizes file paths and names
- **Access Control**: File access permissions and restrictions
- **DataLad Security**: Leverages DataLad's security features

## 📊 Performance Architecture

### Caching Strategy
- **Database Query Caching**: SQLAlchemy query caching
- **Static Asset Caching**: Browser caching for static assets
- **Session Caching**: In-memory session storage
- **DataLad Caching**: DataLad's built-in caching mechanisms

### Optimization Techniques
- **Lazy Loading**: Load data on demand
- **Pagination**: Paginate large datasets
- **Background Processing**: Handle long-running operations asynchronously
- **Resource Monitoring**: Monitor system resources and performance

## 🔄 Integration Architecture

### DataLad Integration
- **Dataset Management**: Automatic dataset creation and configuration
- **File Operations**: Seamless file operations through DataLad
- **Version Control**: Git-based version control for data
- **Metadata Management**: Comprehensive metadata handling

### Git Integration
- **Repository Management**: Git repository creation and management
- **Commit Operations**: Commit creation, viewing, and management
- **Branch Operations**: Branch creation, switching, and merging
- **History Tracking**: Complete commit history and diff viewing

### File System Integration
- **Cross-Platform Support**: Works on macOS, Linux, and Windows
- **Path Handling**: Robust path handling across different operating systems
- **File Operations**: File creation, reading, writing, and deletion
- **Directory Management**: Directory creation, navigation, and organization

## 🚀 Scalability Architecture

### Horizontal Scaling
- **Stateless Design**: Stateless application design for easy scaling
- **Database Scaling**: Support for database clustering and replication
- **Load Balancing**: Ready for load balancer integration
- **Microservices Ready**: Modular design supports microservices architecture

### Vertical Scaling
- **Resource Optimization**: Efficient resource usage
- **Memory Management**: Proper memory management and garbage collection
- **CPU Optimization**: Optimized algorithms and data structures
- **I/O Optimization**: Efficient file and database I/O operations

## 🔧 Configuration Architecture

### Environment Configuration
- **Environment Variables**: Configuration through environment variables
- **Configuration Files**: Support for configuration files
- **Default Settings**: Sensible default configurations
- **Runtime Configuration**: Dynamic configuration updates

### Database Configuration
- **Multiple Databases**: Support for different database backends
- **Connection Pooling**: Database connection pooling
- **Migration Support**: Database migration and versioning
- **Backup and Recovery**: Database backup and recovery strategies

---

**Next Steps**: Explore the [Service Layer Documentation](service-layer.md) to understand the business logic implementation, or check out the [API Reference](../api/README.md) for detailed API documentation.
