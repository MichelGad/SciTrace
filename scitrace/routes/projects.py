"""
Project routes for SciTrace

Handles project creation, management, and viewing.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import json

from ..models import Project, Task, db
from ..services import ProjectService

bp = Blueprint('projects', __name__, url_prefix='/projects')

@bp.route('/')
@login_required
def index():
    """Show all projects for the current user."""
    projects = Project.query.filter_by(admin_id=current_user.id).all()
    
    return render_template('projects/index.html',
                         projects=projects,
                         user=current_user)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new project."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        collaborators = request.form.get('collaborators', '')
        
        if not name:
            flash('Project name is required', 'error')
            return redirect(url_for('projects.create'))
        
        project_service = ProjectService()
        
        try:
            # Parse collaborators
            collaborator_list = []
            if collaborators:
                collaborator_list = [c.strip() for c in collaborators.split(',') if c.strip()]
            
            project_data = project_service.create_project(
                name=name,
                description=description,
                admin_id=current_user.id,
                collaborators=collaborator_list
            )
            
            # Create project in database
            project = Project(
                project_id=project_data['id'],
                name=project_data['name'],
                description=project_data['description'],
                admin_id=project_data['admin_id'],
                collaborators=json.dumps(project_data['collaborators']),
                dataset_path=project_data['dataset_path'],
                status=project_data['status']
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view', project_id=project.id))
            
        except Exception as e:
            flash(f'Error creating project: {str(e)}', 'error')
            return redirect(url_for('projects.create'))
    
    return render_template('projects/create.html', user=current_user)

@bp.route('/<int:project_id>')
@login_required
def view(project_id):
    """View a specific project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('projects.index'))
    
    # Get project tasks
    tasks = Task.query.filter_by(project_id=project_id).all()
    
    return render_template('projects/view.html',
                         project=project,
                         tasks=tasks,
                         user=current_user)

@bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(project_id):
    """Edit a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('projects.index'))
    
    if request.method == 'POST':
        project.name = request.form.get('name', project.name)
        project.description = request.form.get('description', project.description)
        project.status = request.form.get('status', project.status)
        
        collaborators = request.form.get('collaborators', '')
        if collaborators:
            collaborator_list = [c.strip() for c in collaborators.split(',') if c.strip()]
            project.collaborators = json.dumps(collaborator_list)
        
        db.session.commit()
        
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view', project_id=project.id))
    
    return render_template('projects/edit.html',
                         project=project,
                         user=current_user)

@bp.route('/<int:project_id>/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    """Create a new task for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('projects.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        deadline_str = request.form.get('deadline', '')
        priority = request.form.get('priority', 'medium')
        
        if not title:
            flash('Task title is required', 'error')
            return redirect(url_for('projects.create_task', project_id=project_id))
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            except ValueError:
                flash('Invalid deadline format', 'error')
                return redirect(url_for('projects.create_task', project_id=project_id))
        
        task = Task(
            title=title,
            description=description,
            user_id=current_user.id,
            project_id=project_id,
            deadline=deadline,
            priority=priority,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('projects.view', project_id=project_id))
    
    return render_template('projects/create_task.html',
                         project=project,
                         user=current_user)
