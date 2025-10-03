# Service Layer Documentation

This guide covers the service layer architecture, business logic implementation, and service patterns in SciTrace.

## 🏗️ Service Layer Architecture

### Service Organization

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

## 🔧 Base Service

### `services/base_service.py`
```python
from abc import ABC, abstractmethod
from flask import current_app
from sqlalchemy.orm import Session
import logging

class BaseService(ABC):
    """Base service class with common functionality"""
    
    def __init__(self, db_session: Session = None):
        self.db = db_session or current_app.db.session
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def validate_data(self, data: dict) -> tuple[bool, str]:
        """Validate input data"""
        pass
    
    def handle_error(self, error: Exception, context: str = "") -> dict:
        """Handle service errors consistently"""
        self.logger.error(f"Service error in {self.__class__.__name__}: {str(error)}")
        return {
            'success': False,
            'error': str(error),
            'context': context
        }
    
    def log_operation(self, operation: str, details: dict = None):
        """Log service operations"""
        self.logger.info(f"Operation: {operation}", extra=details or {})
```

## 📁 Project Management Service

### `services/project_management.py`
```python
from .base_service import BaseService
from models import Project, User
from sqlalchemy.exc import IntegrityError

class ProjectManagementService(BaseService):
    """Service for project management operations"""
    
    def create_project(self, project_data: dict, user_id: int) -> dict:
        """Create a new project"""
        try:
            # Validate data
            is_valid, error = self.validate_data(project_data)
            if not is_valid:
                return {'success': False, 'error': error}
            
            # Create project
            project = Project(
                name=project_data['name'],
                description=project_data.get('description', ''),
                research_type=project_data['research_type'],
                user_id=user_id
            )
            
            self.db.add(project)
            self.db.commit()
            
            self.log_operation('project_created', {'project_id': project.id})
            return {'success': True, 'project': project.to_dict()}
            
        except IntegrityError as e:
            self.db.rollback()
            return self.handle_error(e, "Project creation failed")
        except Exception as e:
            self.db.rollback()
            return self.handle_error(e, "Unexpected error in project creation")
    
    def validate_data(self, data: dict) -> tuple[bool, str]:
        """Validate project data"""
        required_fields = ['name', 'research_type']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"{field} is required"
        
        if len(data['name']) < 3:
            return False, "Project name must be at least 3 characters"
        
        valid_types = ['environmental', 'biomedical', 'computational']
        if data['research_type'] not in valid_types:
            return False, f"Invalid research type. Must be one of: {', '.join(valid_types)}"
        
        return True, ""
```

## 📊 Dataset Creation Service

### `services/dataset_creation.py`
```python
import subprocess
import os
from .base_service import BaseService

class DatasetCreationService(BaseService):
    """Service for DataLad dataset creation"""
    
    def create_dataset(self, dataset_path: str, dataset_name: str) -> dict:
        """Create a new DataLad dataset"""
        try:
            # Ensure directory exists
            os.makedirs(dataset_path, exist_ok=True)
            
            # Run datalad create command
            result = subprocess.run(
                ['datalad', 'create', dataset_name],
                cwd=dataset_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"DataLad creation failed: {result.stderr}"
                }
            
            self.log_operation('dataset_created', {'path': dataset_path})
            return {'success': True, 'output': result.stdout}
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Dataset creation timed out'}
        except Exception as e:
            return self.handle_error(e, "Dataset creation failed")
```

## 🔧 File Operations Service

### `services/file_operations.py`
```python
import os
import shutil
from pathlib import Path
from .base_service import BaseService

class FileOperationsService(BaseService):
    """Service for file system operations"""
    
    def create_directory(self, path: str) -> dict:
        """Create directory with proper permissions"""
        try:
            os.makedirs(path, exist_ok=True)
            os.chmod(path, 0o755)  # Read/write/execute for owner, read/execute for others
            
            self.log_operation('directory_created', {'path': path})
            return {'success': True, 'path': path}
            
        except PermissionError:
            return {'success': False, 'error': 'Permission denied'}
        except Exception as e:
            return self.handle_error(e, "Directory creation failed")
    
    def upload_file(self, file, destination_path: str) -> dict:
        """Upload file with validation"""
        try:
            # Validate file
            if not file or not file.filename:
                return {'success': False, 'error': 'No file provided'}
            
            # Check file size
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                return {'success': False, 'error': 'File too large'}
            
            # Save file
            file.save(destination_path)
            
            self.log_operation('file_uploaded', {'path': destination_path})
            return {'success': True, 'path': destination_path}
            
        except Exception as e:
            return self.handle_error(e, "File upload failed")
```

## 🔄 Git Operations Service

### `services/git_operations.py`
```python
import subprocess
from .base_service import BaseService

class GitOperationsService(BaseService):
    """Service for Git operations"""
    
    def initialize_repository(self, repo_path: str) -> dict:
        """Initialize Git repository"""
        try:
            result = subprocess.run(
                ['git', 'init'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {'success': False, 'error': f"Git init failed: {result.stderr}"}
            
            self.log_operation('git_repo_initialized', {'path': repo_path})
            return {'success': True, 'output': result.stdout}
            
        except Exception as e:
            return self.handle_error(e, "Git repository initialization failed")
    
    def create_commit(self, repo_path: str, message: str, files: list = None) -> dict:
        """Create Git commit"""
        try:
            # Add files if specified
            if files:
                for file_path in files:
                    subprocess.run(['git', 'add', file_path], cwd=repo_path)
            else:
                subprocess.run(['git', 'add', '.'], cwd=repo_path)
            
            # Create commit
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {'success': False, 'error': f"Git commit failed: {result.stderr}"}
            
            self.log_operation('git_commit_created', {'path': repo_path, 'message': message})
            return {'success': True, 'output': result.stdout}
            
        except Exception as e:
            return self.handle_error(e, "Git commit creation failed")
```

## 📋 Service Integration

### Service Factory Pattern
```python
class ServiceFactory:
    """Service factory for creating service instances"""
    
    _services = {}
    
    @classmethod
    def get_service(cls, service_name: str, db_session=None):
        """Get service instance (singleton pattern)"""
        if service_name not in cls._services:
            if service_name == 'project_management':
                from .project_management import ProjectManagementService
                cls._services[service_name] = ProjectManagementService(db_session)
            elif service_name == 'dataset_creation':
                from .dataset_creation import DatasetCreationService
                cls._services[service_name] = DatasetCreationService(db_session)
            elif service_name == 'file_operations':
                from .file_operations import FileOperationsService
                cls._services[service_name] = FileOperationsService(db_session)
            elif service_name == 'git_operations':
                from .git_operations import GitOperationsService
                cls._services[service_name] = GitOperationsService(db_session)
        
        return cls._services[service_name]
```

## 🎯 Service Usage Examples

### Route Integration
```python
from services import ServiceFactory

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create project using service layer"""
    project_service = ServiceFactory.get_service('project_management')
    
    result = project_service.create_project(
        project_data=request.json,
        user_id=current_user.id
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400
```

## 📊 Service Monitoring

### Service Metrics
```python
class ServiceMetrics:
    """Service performance metrics"""
    
    def __init__(self):
        self.operation_counts = {}
        self.operation_times = {}
        self.error_counts = {}
    
    def record_operation(self, service_name: str, operation: str, duration: float, success: bool):
        """Record service operation metrics"""
        key = f"{service_name}.{operation}"
        
        # Count operations
        self.operation_counts[key] = self.operation_counts.get(key, 0) + 1
        
        # Record timing
        if key not in self.operation_times:
            self.operation_times[key] = []
        self.operation_times[key].append(duration)
        
        # Count errors
        if not success:
            self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def get_metrics(self):
        """Get service metrics"""
        return {
            'operation_counts': self.operation_counts,
            'operation_times': self.operation_times,
            'error_counts': self.error_counts
        }
```

---

**Need help with service development?** Check out the [Developer Guide](README.md) for more technical details, or explore the [API Reference](../api/README.md) for service integration examples.
