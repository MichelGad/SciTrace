# Developer Guide

Welcome to the SciTrace developer documentation! This guide provides comprehensive information for developers who want to contribute to SciTrace or integrate it into their own projects.

## 📚 Table of Contents

1. [Architecture Overview](architecture.md) - System design and components
2. [API Reference](../api/README.md) - Complete API documentation
3. [Database Schema](database-schema.md) - Data models and relationships
4. [Service Layer](service-layer.md) - Business logic and services
5. [Frontend Components](frontend.md) - UI components and templates
6. [Contributing Guidelines](../contributing/README.md) - How to contribute
7. [Development Setup](development-setup.md) - Setting up development environment
8. [Testing](testing.md) - Testing strategies and guidelines
9. [Deployment](deployment.md) - Production deployment guide

## 🏗️ Architecture Overview

SciTrace is built with a modern, modular architecture designed for scalability and maintainability:

### Backend Architecture
- **Flask Web Framework**: Modern web framework with blueprint architecture
- **SQLAlchemy ORM**: Robust database management with relationship handling
- **Flask-Login**: Secure user authentication and session management
- **Modular Service Architecture**: Separated business logic into focused services
- **RESTful API**: Clean API design with proper HTTP methods and status codes

### Frontend Architecture
- **Bootstrap 5**: Modern, responsive design framework
- **Font Awesome Icons**: Clean, professional iconography
- **Vis.js**: Advanced network visualization for dataflows
- **jQuery**: JavaScript utilities and AJAX integration
- **Modular JavaScript**: Organized JavaScript modules for maintainability

### Data Layer
- **SQLite Database**: Lightweight database for development and small deployments
- **DataLad Integration**: Seamless integration with DataLad for data versioning
- **File System**: Direct file system access for data management
- **Git Integration**: Full Git support for version control

## 🔧 Development Setup

### Prerequisites
- **Python 3.8+**: Required for development
- **Git**: For version control
- **DataLad**: For data management features
- **Node.js** (optional): For frontend development tools

### Quick Setup
```bash
# Clone the repository
git clone https://github.com/MichelGad/SciTrace
cd SciTrace

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Initialize database
python run.py
```

### Development Dependencies
```bash
# Install additional development tools
pip install pytest pytest-cov black flake8 mypy
pip install datalad  # If not already installed
```

## 🏛️ Project Structure

```
SciTrace/
├── run.py                    # Application entry point
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── scitrace/                # Main application package
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask application factory
│   ├── models.py            # Database models
│   ├── services/            # Business logic services
│   │   ├── base_service.py  # Base service class
│   │   ├── dataset_creation.py
│   │   ├── dataset_integration.py
│   │   ├── file_operations.py
│   │   ├── git_operations.py
│   │   ├── metadata_operations.py
│   │   ├── project_management.py
│   │   └── project_service.py
│   ├── routes/              # Route blueprints
│   │   ├── auth.py          # Authentication routes
│   │   ├── dashboard.py     # Dashboard routes
│   │   ├── projects.py      # Project management
│   │   ├── dataflow.py      # Dataflow visualization
│   │   ├── tasks.py         # Task management
│   │   └── api/             # API endpoints
│   │       ├── dataflow_api.py
│   │       ├── git_api.py
│   │       ├── file_api.py
│   │       ├── admin_api.py
│   │       └── project_api.py
│   ├── utils/               # Utility modules
│   │   ├── api_validation.py
│   │   ├── auth_helpers.py
│   │   ├── datalad_utils.py
│   │   ├── file_utils.py
│   │   ├── flash_utils.py
│   │   ├── logging_utils.py
│   │   ├── path_validation.py
│   │   ├── response_utils.py
│   │   └── validation_utils.py
│   ├── templates/           # HTML templates
│   ├── static/              # Static assets
│   └── assets/              # Third-party assets
├── tests/                   # Test suite
├── docs/                    # Documentation
└── instance/                # Instance-specific files
```

## 🔌 API Development

### API Design Principles
- **RESTful Design**: Follow REST principles for API endpoints
- **Consistent Responses**: Use consistent response formats
- **Error Handling**: Proper HTTP status codes and error messages
- **Authentication**: Secure API endpoints with proper authentication
- **Documentation**: Comprehensive API documentation

### Adding New API Endpoints
1. **Create Blueprint**: Add new blueprint in `routes/api/`
2. **Define Routes**: Create route handlers with proper HTTP methods
3. **Add Validation**: Implement request validation
4. **Business Logic**: Use service layer for business logic
5. **Error Handling**: Implement proper error handling
6. **Documentation**: Update API documentation

### Example API Endpoint
```python
from flask import Blueprint, request, jsonify
from ..services.project_service import ProjectService
from ..utils.api_validation import validate_request

project_api_bp = Blueprint('project_api', __name__, url_prefix='/api/projects')

@project_api_bp.route('/', methods=['POST'])
def create_project():
    """Create a new project."""
    try:
        # Validate request
        data = validate_request(request, required_fields=['name', 'description'])
        
        # Use service layer
        project_service = ProjectService()
        project = project_service.create_project(
            name=data['name'],
            description=data['description'],
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
```

## 🗄️ Database Development

### Model Development
- **SQLAlchemy Models**: Use SQLAlchemy for database models
- **Relationships**: Define proper relationships between models
- **Validation**: Implement model-level validation
- **Migrations**: Use Flask-Migrate for database migrations

### Adding New Models
1. **Define Model**: Create new model class in `models.py`
2. **Add Relationships**: Define relationships with other models
3. **Add Validation**: Implement model validation
4. **Create Migration**: Generate database migration
5. **Update Services**: Update service layer to use new model

### Example Model
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    user = relationship('User', backref='projects')
    dataflows = relationship('Dataflow', backref='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }
```

## 🎨 Frontend Development

### Template Development
- **Jinja2 Templates**: Use Jinja2 for template rendering
- **Bootstrap Components**: Leverage Bootstrap for UI components
- **Responsive Design**: Ensure mobile-friendly design
- **Accessibility**: Follow WCAG guidelines

### JavaScript Development
- **Modular JavaScript**: Organize JavaScript into modules
- **jQuery Integration**: Use jQuery for DOM manipulation
- **AJAX Requests**: Handle API calls with proper error handling
- **Event Handling**: Implement proper event handling

### Adding New Features
1. **Create Template**: Add new HTML template
2. **Add Route**: Create route handler
3. **Implement JavaScript**: Add client-side functionality
4. **Style Components**: Add CSS styling
5. **Test Functionality**: Test across different browsers

## 🧪 Testing

### Test Structure
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **API Tests**: Test API endpoints
- **Frontend Tests**: Test user interface

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scitrace

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Writing Tests
```python
import pytest
from scitrace.models import Project, User
from scitrace.services.project_service import ProjectService

class TestProjectService:
    def test_create_project(self, app, user):
        """Test project creation."""
        with app.app_context():
            service = ProjectService()
            project = service.create_project(
                name='Test Project',
                description='Test Description',
                user_id=user.id
            )
            
            assert project.name == 'Test Project'
            assert project.description == 'Test Description'
            assert project.user_id == user.id
```

## 🚀 Deployment

### Production Setup
- **Environment Variables**: Configure production environment
- **Database**: Set up production database
- **Web Server**: Configure web server (nginx, Apache)
- **Process Manager**: Use process manager (systemd, supervisor)
- **SSL Certificate**: Set up HTTPS

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "run.py"]
```

## 📝 Code Style

### Python Style
- **PEP 8**: Follow PEP 8 style guidelines
- **Black**: Use Black for code formatting
- **Flake8**: Use Flake8 for linting
- **Type Hints**: Use type hints for better code clarity

### JavaScript Style
- **ESLint**: Use ESLint for JavaScript linting
- **Prettier**: Use Prettier for code formatting
- **Consistent Naming**: Use consistent naming conventions

### Git Workflow
- **Feature Branches**: Create feature branches for new features
- **Commit Messages**: Use clear, descriptive commit messages
- **Pull Requests**: Use pull requests for code review
- **Testing**: Ensure all tests pass before merging

## 🔍 Debugging

### Development Tools
- **Flask Debug Mode**: Enable debug mode for development
- **Logging**: Use proper logging for debugging
- **Error Handling**: Implement comprehensive error handling
- **Browser DevTools**: Use browser developer tools

### Common Issues
- **Database Issues**: Check database connectivity and migrations
- **Permission Issues**: Verify file and directory permissions
- **DataLad Issues**: Check DataLad installation and configuration
- **Frontend Issues**: Check JavaScript console for errors

## 📚 Additional Resources

### Documentation
- **Flask Documentation**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **SQLAlchemy Documentation**: [docs.sqlalchemy.org](https://docs.sqlalchemy.org/)
- **DataLad Documentation**: [datalad.org](https://www.datalad.org/)
- **Bootstrap Documentation**: [getbootstrap.com](https://getbootstrap.com/)

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Join community discussions
- **Contributing**: See contributing guidelines
- **Code of Conduct**: Follow community guidelines

---

**Ready to contribute?** Check out the [Contributing Guidelines](../contributing/README.md) to get started, or explore the [Architecture Overview](architecture.md) to understand the system design.
