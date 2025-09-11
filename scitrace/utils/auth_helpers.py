"""
Authentication and authorization helpers for SciTrace

Provides decorators and utilities for access control and user permission checks.
"""

from functools import wraps
from flask import jsonify, request, abort
from flask_login import current_user, login_required
from ..models import Project, Task, Dataflow


def require_login(f):
    """Decorator to require user login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            abort(401)
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """Decorator to require admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            abort(401)
        
        if current_user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_project_access(f):
    """Decorator to require access to a specific project."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            abort(401)
        
        # Get project_id from route parameters
        project_id = kwargs.get('project_id')
        if project_id:
            project = Project.query.get_or_404(project_id)
            if project.admin_id != current_user.id:
                if request.is_json:
                    return jsonify({'error': 'Access denied to this project'}), 403
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_task_access(f):
    """Decorator to require access to a specific task."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            abort(401)
        
        # Get task_id from route parameters
        task_id = kwargs.get('task_id')
        if task_id:
            task = Task.query.get_or_404(task_id)
            if task.user_id != current_user.id:
                if request.is_json:
                    return jsonify({'error': 'Access denied to this task'}), 403
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_dataflow_access(f):
    """Decorator to require access to a specific dataflow."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            abort(401)
        
        # Get dataflow_id from route parameters
        dataflow_id = kwargs.get('dataflow_id')
        if dataflow_id:
            dataflow = Dataflow.query.get_or_404(dataflow_id)
            if dataflow.project.admin_id != current_user.id:
                if request.is_json:
                    return jsonify({'error': 'Access denied to this dataflow'}), 403
                abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_ownership_or_admin(resource_type):
    """
    Decorator factory to require ownership of a resource or admin role.
    
    Args:
        resource_type: The type of resource ('project', 'task', 'dataflow')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                abort(401)
            
            # Admin users have access to everything
            if current_user.role == 'admin':
                return f(*args, **kwargs)
            
            # Check ownership based on resource type
            if resource_type == 'project':
                project_id = kwargs.get('project_id')
                if project_id:
                    project = Project.query.get_or_404(project_id)
                    if project.admin_id != current_user.id:
                        if request.is_json:
                            return jsonify({'error': 'Access denied to this project'}), 403
                        abort(403)
            
            elif resource_type == 'task':
                task_id = kwargs.get('task_id')
                if task_id:
                    task = Task.query.get_or_404(task_id)
                    if task.user_id != current_user.id:
                        if request.is_json:
                            return jsonify({'error': 'Access denied to this task'}), 403
                        abort(403)
            
            elif resource_type == 'dataflow':
                dataflow_id = kwargs.get('dataflow_id')
                if dataflow_id:
                    dataflow = Dataflow.query.get_or_404(dataflow_id)
                    if dataflow.project.admin_id != current_user.id:
                        if request.is_json:
                            return jsonify({'error': 'Access denied to this dataflow'}), 403
                        abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_project_permission(project_id, permission='read'):
    """
    Check if the current user has permission for a project.
    
    Args:
        project_id: The project ID to check
        permission: The permission to check ('read', 'write', 'admin')
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not current_user.is_authenticated:
        return False
    
    # Admin users have all permissions
    if current_user.role == 'admin':
        return True
    
    project = Project.query.get(project_id)
    if not project:
        return False
    
    # Project admin has all permissions
    if project.admin_id == current_user.id:
        return True
    
    # For now, only project admin has permissions
    # In the future, this could be extended to support collaborators
    return False


def check_task_permission(task_id, permission='read'):
    """
    Check if the current user has permission for a task.
    
    Args:
        task_id: The task ID to check
        permission: The permission to check ('read', 'write', 'admin')
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not current_user.is_authenticated:
        return False
    
    # Admin users have all permissions
    if current_user.role == 'admin':
        return True
    
    task = Task.query.get(task_id)
    if not task:
        return False
    
    # Task owner has all permissions
    if task.user_id == current_user.id:
        return True
    
    # Project admin has permissions to all tasks in their project
    if task.project and task.project.admin_id == current_user.id:
        return True
    
    return False


def check_dataflow_permission(dataflow_id, permission='read'):
    """
    Check if the current user has permission for a dataflow.
    
    Args:
        dataflow_id: The dataflow ID to check
        permission: The permission to check ('read', 'write', 'admin')
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if not current_user.is_authenticated:
        return False
    
    # Admin users have all permissions
    if current_user.role == 'admin':
        return True
    
    dataflow = Dataflow.query.get(dataflow_id)
    if not dataflow:
        return False
    
    # Project admin has all permissions to dataflows in their project
    if dataflow.project and dataflow.project.admin_id == current_user.id:
        return True
    
    return False


def get_user_accessible_projects(user_id=None):
    """
    Get all projects accessible to a user.
    
    Args:
        user_id: The user ID (defaults to current user)
    
    Returns:
        Query: SQLAlchemy query for accessible projects
    """
    if user_id is None:
        user_id = current_user.id if current_user.is_authenticated else None
    
    if not user_id:
        return Project.query.filter(False)  # Empty query
    
    # Admin users can see all projects
    if current_user.is_authenticated and current_user.role == 'admin':
        return Project.query
    
    # Regular users can only see their own projects
    return Project.query.filter_by(admin_id=user_id)


def get_user_accessible_tasks(user_id=None):
    """
    Get all tasks accessible to a user.
    
    Args:
        user_id: The user ID (defaults to current user)
    
    Returns:
        Query: SQLAlchemy query for accessible tasks
    """
    if user_id is None:
        user_id = current_user.id if current_user.is_authenticated else None
    
    if not user_id:
        return Task.query.filter(False)  # Empty query
    
    # Admin users can see all tasks
    if current_user.is_authenticated and current_user.role == 'admin':
        return Task.query
    
    # Regular users can see their own tasks and tasks in their projects
    from sqlalchemy import or_
    return Task.query.filter(
        or_(
            Task.user_id == user_id,
            Task.project.has(admin_id=user_id)
        )
    )


def get_user_accessible_dataflows(user_id=None):
    """
    Get all dataflows accessible to a user.
    
    Args:
        user_id: The user ID (defaults to current user)
    
    Returns:
        Query: SQLAlchemy query for accessible dataflows
    """
    if user_id is None:
        user_id = current_user.id if current_user.is_authenticated else None
    
    if not user_id:
        return Dataflow.query.filter(False)  # Empty query
    
    # Admin users can see all dataflows
    if current_user.is_authenticated and current_user.role == 'admin':
        return Dataflow.query
    
    # Regular users can see dataflows in their projects
    return Dataflow.query.filter(Dataflow.project.has(admin_id=user_id))
