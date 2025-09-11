# Features Overview

SciTrace provides a comprehensive suite of features for research data management, from project organization to advanced data lineage tracking. This guide covers all the features available in SciTrace.

## 📊 Data Management & DataLad Integration

### Full DataLad Integration
SciTrace seamlessly integrates with DataLad for robust data versioning and management:
- **Automatic Dataset Creation**: New dataflows automatically create properly structured DataLad datasets
- **Version Control**: Track all changes to your data with Git-based versioning
- **Data Lineage**: Complete traceability of data transformations and processing steps
- **Cross-Platform Compatibility**: Works with existing DataLad datasets and workflows

### Interactive Dataflow Visualization
- **Network Diagrams**: Visual representation of your data pipeline as interactive network graphs
- **Color-Coded Nodes**: Different colors for files, directories, and processing steps
- **Click-to-Explore**: Click on any node to view metadata, file content, or download files
- **Real-Time Updates**: Visualization automatically reflects all DataLad changes
- **Zoom and Pan**: Navigate large dataflows with intuitive controls

### File Management
- **Web-Based File Operations**: Upload, download, and manage files directly through the web interface
- **File Content Viewing**: View file content directly in the browser with syntax highlighting
- **File Explorer Integration**: Open file locations in your system file explorer with one click
- **Batch Operations**: Handle multiple files efficiently
- **File Restoration**: Restore deleted files from previous commits with enhanced error handling

### Enhanced File Operations
- **Robust File Path Handling**: Reliable file addition to DataLad datasets
- **Automatic Directory Creation**: Professional directory organization with `raw_data`, `scripts`, `results`, and `plots` folders
- **Research Type Selection**: Choose from Environmental, Biomedical, Computational, or General research structures
- **File Validation**: Basic file format validation and comprehensive metadata management

## 👥 Project & Task Management

### Project Management
- **Project Creation**: Create and manage research projects with detailed metadata
- **Collaborator Support**: Add team members and manage project access
- **Project Organization**: Organize projects by research type and status
- **Project Dashboard**: Comprehensive overview of all your projects
- **Project Templates**: Pre-configured structures for different research types

### Task Tracking
- **Task Creation**: Create tasks with deadlines, priorities, and descriptions
- **Progress Tracking**: Monitor task completion and project progress
- **Deadline Management**: Set and track important deadlines
- **Priority Levels**: Organize tasks by importance and urgency
- **Task Assignment**: Assign tasks to team members

### User Authentication & Access Control
- **Secure Login System**: Role-based access control with secure authentication
- **User Profiles**: Manage user accounts and preferences
- **Project Permissions**: Control access to projects and dataflows
- **Session Management**: Secure session handling with automatic logout

## 🔍 Git Operations & Version Control

### Interactive Git Log Visualization
- **Unified Interface**: Single-tab design combining commit information and file changes
- **Real File Diffs**: Actual Git diff content with proper syntax highlighting and formatting
- **Tree Visualization**: Interactive commit tree showing branching and merging patterns
- **Streamlined Layout**: Single-line commit display with avatar, author, hash, date, and message
- **Smart File Tree**: Left panel showing changed files with status indicators (added, modified, deleted)
- **Live Diff View**: Right panel displaying real-time file differences as you select files

### Advanced Git Operations
- **Copy Hash**: Copy commit hash to clipboard for referencing
- **View Files**: See exactly what files were modified in each commit
- **Revert Commit**: Undo changes by creating a revert commit
- **Branch Management**: Visualize and manage Git branches
- **Merge Tracking**: Track merge commits and conflicts

### Web-based DataLad Operations
- **Save Files**: Save files and commit changes directly through the web interface
- **Stage Management**: Save entire stages with custom commit messages
- **Direct DataLad Access**: Execute DataLad commands through the web interface
- **Commit History Management**: View and manage file commit history
- **No Terminal Required**: All operations available through the web interface

## 🛠️ Development & Debugging Tools

### Data Reset Tools
- **Comprehensive Reset**: Complete filesystem cleanup for development and testing
- **Page-Specific Reset**: Individual reset options for projects, tasks, and dataflows
- **Safe Reset**: Confirmation dialogs to prevent accidental data loss
- **Selective Cleanup**: Choose what to reset and what to preserve

### Demo Environment
- **Quick Setup**: Sample research data for testing and exploration
- **Environmental Research**: Water quality research dataset with realistic structure
- **Sample Scripts**: Python and R scripts for data analysis
- **Professional Structure**: Realistic research directory organization
- **Demo Badges**: Clear identification of demo projects throughout the interface

### Debug Endpoints
- **Built-in Debugging**: Tools for troubleshooting DataLad and Git operations
- **Enhanced Error Handling**: Clear error messages with debugging information and suggestions
- **Logging**: Comprehensive logging of operations and errors
- **Web-based Shutdown**: One-click Flask application shutdown via web interface

## 🎨 User Interface & Experience

### Modern Web Interface
- **Bootstrap 5**: Modern, responsive design framework
- **Font Awesome Icons**: Clean, professional iconography
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark/Light Themes**: Customizable interface themes
- **Accessibility**: WCAG compliant interface design

### Interactive Visualizations
- **Vis.js Integration**: Advanced network visualization for dataflows
- **Real-Time Updates**: Live updates to visualizations as data changes
- **Customizable Views**: Different visualization modes and layouts
- **Export Options**: Save visualizations as images or data files

### Dashboard & Navigation
- **Comprehensive Dashboard**: Statistics and quick access to key functions
- **Intuitive Navigation**: Easy-to-use menu system
- **Quick Actions**: Fast access to common operations
- **Recent Activity**: Track latest changes and updates
- **Search Functionality**: Find projects, files, and dataflows quickly

## 🔧 Advanced Features

### Data Validation
- **File Format Validation**: Automatic validation of uploaded data formats
- **Metadata Management**: Comprehensive metadata exploration and management
- **Data Integrity**: Checksums and validation for data integrity
- **Format Support**: Support for various scientific data formats

### Performance & Scalability
- **Efficient Processing**: Optimized for large datasets and complex workflows
- **Caching**: Smart caching for improved performance
- **Background Processing**: Long-running operations handled in background
- **Resource Monitoring**: Track system resources and performance

### Integration & Extensibility
- **RESTful API**: Complete API for external tool integration
- **Webhook Support**: Real-time notifications and integrations
- **Plugin Architecture**: Extensible architecture for custom features
- **Export/Import**: Data export and import capabilities

## 🚀 Upcoming Features

### Version 2.0 - Interactive Research Platform
- **Direct Data Upload**: Drag & drop interface for file uploads
- **Built-in Code Editor**: Web-based code editor with syntax highlighting
- **Interactive Code Execution**: Execute code and automatically trace output files
- **Advanced Analytics**: Built-in statistical analysis and visualization tools
- **Real-time Collaboration**: Live collaboration on research workflows
- **AI-Powered Insights**: Machine learning recommendations for data analysis

### Future Enhancements
- **Cloud Deployment**: Multi-cloud deployment options
- **Advanced Security**: Enhanced security features and encryption
- **Mobile App**: Native mobile applications
- **Integration APIs**: Enhanced APIs for external tool integration

## 📈 Feature Comparison

| Feature | Basic | Advanced | Enterprise |
|---------|-------|----------|------------|
| Project Management | ✅ | ✅ | ✅ |
| DataLad Integration | ✅ | ✅ | ✅ |
| Interactive Visualization | ✅ | ✅ | ✅ |
| Git Operations | ✅ | ✅ | ✅ |
| User Authentication | ✅ | ✅ | ✅ |
| Task Management | ✅ | ✅ | ✅ |
| File Management | ✅ | ✅ | ✅ |
| Demo Environment | ✅ | ✅ | ✅ |
| API Access | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ |
| Cloud Deployment | ❌ | ❌ | ✅ |
| Enterprise Support | ❌ | ❌ | ✅ |

---

**Ready to explore these features?** Check out the [Quick Start Guide](quick-start.md) to begin using SciTrace, or dive deeper with the [User Guide](README.md).
