# Contributing to SciTrace

Thank you for your interest in contributing to SciTrace! This guide will help you get started with contributing to the project.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit code improvements
- **Documentation**: Improve or add documentation
- **Testing**: Help with testing and quality assurance
- **Community Support**: Help other users

### Getting Started

1. **Fork the Repository**: Fork the SciTrace repository on GitHub
2. **Clone Your Fork**: Clone your fork to your local machine
3. **Set Up Development Environment**: Follow the development setup guide
4. **Create a Branch**: Create a feature branch for your changes
5. **Make Changes**: Implement your changes
6. **Test Your Changes**: Ensure your changes work correctly
7. **Submit a Pull Request**: Create a pull request with your changes

## 🛠️ Development Setup

### Prerequisites

- **Python 3.8+**: Required for development
- **Git**: For version control
- **DataLad**: For data management features
- **Node.js** (optional): For frontend development tools

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SciTrace.git
cd SciTrace

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

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

## 📝 Code Style

### Python Style

We follow PEP 8 style guidelines:

```bash
# Format code with Black
black scitrace/

# Lint with Flake8
flake8 scitrace/

# Type checking with MyPy
mypy scitrace/
```

### JavaScript Style

```bash
# Lint JavaScript
eslint scitrace/static/js/

# Format with Prettier
prettier --write scitrace/static/js/
```

### Git Commit Messages

Use clear, descriptive commit messages:

```
feat: add new dataflow visualization feature
fix: resolve file upload timeout issue
docs: update installation guide
test: add unit tests for project service
refactor: improve error handling in API endpoints
```

## 🧪 Testing

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

Create tests for new features:

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

### Test Structure

```
tests/
├── test_models.py          # Database model tests
├── test_services.py        # Service layer tests
├── test_api.py            # API endpoint tests
├── test_auth.py           # Authentication tests
└── fixtures/              # Test fixtures
    ├── conftest.py
    └── test_data.py
```

## 🔧 Development Workflow

### Branch Naming

Use descriptive branch names:

```
feature/add-user-roles
bugfix/fix-file-upload
docs/update-api-docs
refactor/improve-error-handling
```

### Pull Request Process

1. **Create Feature Branch**: Create a branch from `main`
2. **Implement Changes**: Make your changes with tests
3. **Update Documentation**: Update relevant documentation
4. **Run Tests**: Ensure all tests pass
5. **Create Pull Request**: Submit PR with clear description
6. **Code Review**: Address review feedback
7. **Merge**: Maintainer merges after approval

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 📚 Documentation

### Documentation Standards

- **User Documentation**: Clear, step-by-step instructions
- **API Documentation**: Complete endpoint documentation
- **Code Documentation**: Inline comments and docstrings
- **README Updates**: Keep README current

### Documentation Structure

```
docs/
├── README.md              # Main documentation index
├── installation/          # Installation guides
├── user-guide/           # User documentation
├── developer/            # Developer documentation
├── api/                  # API documentation
├── deployment/           # Deployment guides
├── troubleshooting/      # Troubleshooting guides
└── contributing/         # Contributing guidelines
```

## 🐛 Bug Reports

### Before Reporting

1. **Check Existing Issues**: Search for similar issues
2. **Try Latest Version**: Ensure you're using the latest version
3. **Check Documentation**: Review relevant documentation
4. **Reproduce Issue**: Ensure you can reproduce the issue

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.0]
- SciTrace Version: [e.g., 0.1.0]
- DataLad Version: [e.g., 0.15.0]

## Additional Context
Any other relevant information
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other relevant information
```

## 🔍 Code Review

### Review Guidelines

- **Functionality**: Does the code work as intended?
- **Style**: Does it follow our style guidelines?
- **Tests**: Are there adequate tests?
- **Documentation**: Is documentation updated?
- **Performance**: Are there performance implications?
- **Security**: Are there security considerations?

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and pass
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance is acceptable
- [ ] Security considerations addressed

## 🚀 Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number updated
- [ ] Release notes prepared
- [ ] Tag created
- [ ] Release published

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be Respectful**: Treat everyone with respect
- **Be Inclusive**: Welcome newcomers and different perspectives
- **Be Collaborative**: Work together constructively
- **Be Professional**: Maintain professional communication

### Communication

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code contributions
- **Email**: For security issues (see security policy)

## 🔒 Security

### Security Issues

For security issues, please:
1. **Do NOT** create a public issue
2. **Email** security concerns to: security@scitrace.org
3. **Include** detailed information about the issue
4. **Wait** for response before public disclosure

### Security Best Practices

- **Input Validation**: Validate all user inputs
- **Authentication**: Implement proper authentication
- **Authorization**: Check permissions for all operations
- **Data Protection**: Protect sensitive data
- **Dependencies**: Keep dependencies updated

## 📞 Getting Help

### Resources

- **Documentation**: Check our comprehensive documentation
- **Issues**: Search existing issues or create new ones
- **Discussions**: Join community discussions
- **FAQ**: Check frequently asked questions

### Contact

- **GitHub Issues**: [Create an issue](https://github.com/MichelGad/SciTrace/issues)
- **GitHub Discussions**: [Join discussions](https://github.com/MichelGad/SciTrace/discussions)
- **Email**: info@scitrace.org

## 🙏 Recognition

Contributors will be recognized in:
- **README**: Contributor list
- **Changelog**: Release notes
- **Documentation**: Contributor acknowledgments
- **GitHub**: Contributor statistics

## 📄 License

By contributing to SciTrace, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to SciTrace!** Your contributions help make research data management better for everyone.

**Ready to contribute?** Check out the [Development Setup Guide](../developer/development-setup.md) to get started, or explore the [Architecture Overview](../developer/architecture.md) to understand the system design.
