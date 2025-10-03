# Database Schema Documentation

This guide covers the database schema, data models, relationships, and database operations in SciTrace.

## 🗄️ Database Overview

SciTrace uses SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production). The database schema is designed for research data management with proper relationships and constraints.

## 📊 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Database Schema                         │
├─────────────────────────────────────────────────────────────┤
│  Users                                                      │
│  ├── id (Primary Key)                                       │
│  ├── username (Unique)                                      │
│  ├── email (Unique)                                         │
│  ├── password_hash                                          │
│  ├── role                                                   │
│  ├── is_active                                              │
│  └── created_at                                            │
├─────────────────────────────────────────────────────────────┤
│  Projects                                                   │
│  ├── id (Primary Key)                                       │
│  ├── name                                                   │
│  ├── description                                            │
│  ├── research_type                                          │
│  ├── user_id (Foreign Key → Users.id)                      │
│  ├── created_at                                            │
│  └── updated_at                                            │
├─────────────────────────────────────────────────────────────┤
│  Dataflows                                                  │
│  ├── id (Primary Key)                                       │
│  ├── name                                                   │
│  ├── path                                                   │
│  ├── project_id (Foreign Key → Projects.id)                │
│  ├── created_at                                            │
│  └── updated_at                                            │
├─────────────────────────────────────────────────────────────┤
│  Tasks                                                      │
│  ├── id (Primary Key)                                       │
│  ├── title                                                  │
│  ├── description                                            │
│  ├── status                                                 │
│  ├── priority                                               │
│  ├── deadline                                               │
│  ├── project_id (Foreign Key → Projects.id)                │
│  ├── assignee_id (Foreign Key → Users.id)                  │
│  ├── created_at                                            │
│  └── updated_at                                            │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ Data Models

### User Model
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    assigned_tasks = db.relationship('Task', backref='assignee', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'
```

### Project Model
```python
class Project(db.Model):
    """Project model for research projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    research_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dataflows = db.relationship('Dataflow', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    # Computed properties
    @property
    def dataflow_count(self):
        return self.dataflows.count()
    
    @property
    def task_count(self):
        return self.tasks.count()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'research_type': self.research_type,
            'user_id': self.user_id,
            'dataflow_count': self.dataflow_count,
            'task_count': self.task_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Project {self.name}>'
```

### Dataflow Model
```python
class Dataflow(db.Model):
    """Dataflow model for dataset management"""
    __tablename__ = 'dataflows'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    path = db.Column(db.String(500), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Dataflow {self.name}>'
```

### Task Model
```python
class Task(db.Model):
    """Task model for project task management"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    priority = db.Column(db.String(20), default='medium', nullable=False, index=True)
    deadline = db.Column(db.DateTime, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Task {self.title}>'
```

## 🔗 Database Relationships

### Relationship Mapping
```python
# One-to-Many Relationships
User → Projects (One user can have many projects)
User → Tasks (One user can be assigned many tasks)
Project → Dataflows (One project can have many dataflows)
Project → Tasks (One project can have many tasks)

# Many-to-One Relationships
Project → User (Many projects belong to one user)
Task → User (Many tasks can be assigned to one user)
Task → Project (Many tasks belong to one project)
Dataflow → Project (Many dataflows belong to one project)
```

### Relationship Queries
```python
# Get user's projects
user_projects = User.query.get(user_id).projects.all()

# Get project's dataflows
project_dataflows = Project.query.get(project_id).dataflows.all()

# Get project's tasks
project_tasks = Project.query.get(project_id).tasks.all()

# Get user's assigned tasks
user_tasks = User.query.get(user_id).assigned_tasks.all()

# Get tasks by status
pending_tasks = Task.query.filter_by(status='pending').all()

# Get projects by research type
env_projects = Project.query.filter_by(research_type='environmental').all()
```

## 📊 Database Indexes

### Index Configuration
```python
# Primary indexes (automatically created)
users.id
projects.id
dataflows.id
tasks.id

# Unique indexes
users.username
users.email

# Foreign key indexes (automatically created)
projects.user_id
dataflows.project_id
tasks.project_id
tasks.assignee_id

# Custom indexes for performance
projects.research_type
projects.created_at
tasks.status
tasks.priority
tasks.deadline
users.role
users.is_active
```

### Index Optimization
```python
# Add custom indexes for common queries
db.Index('idx_projects_user_created', Project.user_id, Project.created_at)
db.Index('idx_tasks_project_status', Task.project_id, Task.status)
db.Index('idx_tasks_assignee_status', Task.assignee_id, Task.status)
db.Index('idx_tasks_deadline_status', Task.deadline, Task.status)
```

## 🔧 Database Operations

### CRUD Operations
```python
class DatabaseOperations:
    """Database operation utilities"""
    
    @staticmethod
    def create_user(username, email, password, role='user'):
        """Create new user"""
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def create_project(name, description, research_type, user_id):
        """Create new project"""
        project = Project(
            name=name,
            description=description,
            research_type=research_type,
            user_id=user_id
        )
        db.session.add(project)
        db.session.commit()
        return project
    
    @staticmethod
    def get_user_projects(user_id, limit=None):
        """Get user's projects with optional limit"""
        query = Project.query.filter_by(user_id=user_id).order_by(Project.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def update_task_status(task_id, status):
        """Update task status"""
        task = Task.query.get(task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()
            db.session.commit()
            return task
        return None
    
    @staticmethod
    def delete_project(project_id):
        """Delete project and related data"""
        project = Project.query.get(project_id)
        if project:
            # Cascade delete will handle related dataflows and tasks
            db.session.delete(project)
            db.session.commit()
            return True
        return False
```

## 📈 Database Migrations

### Migration Setup
```python
# Using Flask-Migrate
from flask_migrate import Migrate

migrate = Migrate(app, db)

# Create migration
# flask db migrate -m "Initial migration"

# Apply migration
# flask db upgrade

# Rollback migration
# flask db downgrade
```

### Migration Examples
```python
# Example migration for adding new field
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

def downgrade():
    # Remove column
    op.drop_column('users', 'last_login')
```

## 🔍 Query Optimization

### Efficient Queries
```python
# Use eager loading for related objects
projects = Project.query.options(
    db.joinedload(Project.dataflows),
    db.joinedload(Project.tasks)
).filter_by(user_id=user_id).all()

# Use pagination for large datasets
page = request.args.get('page', 1, type=int)
projects = Project.query.filter_by(user_id=user_id).paginate(
    page=page, per_page=10, error_out=False
)

# Use database functions for aggregations
from sqlalchemy import func

project_stats = db.session.query(
    Project.research_type,
    func.count(Project.id).label('count')
).group_by(Project.research_type).all()
```

### Query Performance
```python
# Use indexes for filtering
projects = Project.query.filter_by(research_type='environmental').all()

# Use compound indexes for complex queries
tasks = Task.query.filter_by(
    project_id=project_id,
    status='pending'
).order_by(Task.priority.desc()).all()

# Use exists() for existence checks
has_tasks = db.session.query(
    db.session.query(Task).filter_by(project_id=project_id).exists()
).scalar()
```

## 🛡️ Database Security

### Data Validation
```python
from sqlalchemy.orm import validates

class User(db.Model):
    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError("Invalid email format")
        return email
    
    @validates('role')
    def validate_role(self, key, role):
        valid_roles = ['user', 'admin', 'super_admin']
        if role not in valid_roles:
            raise ValueError("Invalid role")
        return role
```

### Access Control
```python
def get_user_projects(user_id, admin_override=False):
    """Get projects with access control"""
    if admin_override:
        return Project.query.all()
    return Project.query.filter_by(user_id=user_id).all()

def can_access_project(user_id, project_id, user_role=None):
    """Check if user can access project"""
    project = Project.query.get(project_id)
    if not project:
        return False
    
    # Admin can access all projects
    if user_role == 'admin':
        return True
    
    # Users can only access their own projects
    return project.user_id == user_id
```

## 📋 Database Checklist

### Development Checklist
- [ ] Models defined with proper relationships
- [ ] Indexes created for performance
- [ ] Validation rules implemented
- [ ] CRUD operations tested
- [ ] Migration scripts created
- [ ] Query optimization applied
- [ ] Security measures implemented
- [ ] Documentation updated

### Production Checklist
- [ ] Database connection configured
- [ ] Connection pooling enabled
- [ ] Backup procedures implemented
- [ ] Monitoring configured
- [ ] Performance benchmarks established
- [ ] Security audit completed
- [ ] Migration procedures tested
- [ ] Recovery procedures documented

---

**Need help with database development?** Check out the [Developer Guide](README.md) for more technical details, or explore the [API Reference](../api/README.md) for database integration examples.
