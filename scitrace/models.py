"""
Database models for SciTrace

Defines the data models for users, projects, tasks, and dataflows.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='admin', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    """Project model for research projects."""
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., I293DSA39
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    collaborators = db.Column(db.String(500))  # JSON string of collaborators
    status = db.Column(db.String(20), default='ongoing')  # ongoing, completed, paused
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # DataLad specific fields
    dataset_path = db.Column(db.String(500))  # Path to the DataLad dataset
    git_remote = db.Column(db.String(500))  # Git remote URL
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True)
    dataflows = db.relationship('Dataflow', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def get_collaborators_list(self):
        """Get collaborators as a list."""
        if self.collaborators:
            return json.loads(self.collaborators)
        return []

class Task(db.Model):
    """Task model for project tasks."""
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    deadline = db.Column(db.DateTime)
    priority = db.Column(db.String(20), default='medium')  # low, medium, urgent
    status = db.Column(db.String(20), default='pending')  # pending, ongoing, done
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Task {self.title}>'

class Dataflow(db.Model):
    """Dataflow model for visualizing research data workflows."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Dataflow structure stored as JSON
    nodes = db.Column(db.Text)  # JSON string of nodes
    edges = db.Column(db.Text)  # JSON string of edges
    flow_metadata = db.Column(db.Text)  # Additional metadata as JSON (renamed from metadata)
    
    def get_nodes(self):
        """Get nodes as a list."""
        if self.nodes:
            return json.loads(self.nodes)
        return []
    
    def get_edges(self):
        """Get edges as a list."""
        if self.edges:
            return json.loads(self.edges)
        return []
    
    def get_metadata(self):
        """Get metadata as a dict."""
        if self.flow_metadata:
            return json.loads(self.flow_metadata)
        return {}
    
    def set_nodes(self, nodes_list):
        """Set nodes from a list."""
        self.nodes = json.dumps(nodes_list)
    
    def set_edges(self, edges_list):
        """Set edges from a list."""
        self.edges = json.dumps(edges_list)
    
    def set_metadata(self, metadata_dict):
        """Set metadata from a dict."""
        self.flow_metadata = json.dumps(metadata_dict)
    
    def __repr__(self):
        return f'<Dataflow {self.name}>'
