"""
Tasks routes for SciTrace

Handles task management and viewing across all projects.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from ..models import Task, Project, db

bp = Blueprint('tasks', __name__, url_prefix='/tasks')

@bp.route('/')
@login_required
def index():
    """Show all tasks for the current user."""
    # Get all tasks for the current user
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    
    # Get projects for context
    projects = Project.query.filter_by(admin_id=current_user.id).all()
    
    return render_template('tasks/index.html',
                         tasks=tasks,
                         projects=projects,
                         user=current_user,
                         now=datetime.utcnow())

@bp.route('/<int:task_id>')
@login_required
def view(task_id):
    """View a specific task."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('tasks.index'))
    
    return render_template('tasks/view.html',
                         task=task,
                         user=current_user,
                         now=datetime.utcnow())

@bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(task_id):
    """Edit a task."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('tasks.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        deadline_str = request.form.get('deadline', '')
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', 'pending')
        
        if not title:
            flash('Task title is required', 'error')
            return redirect(url_for('tasks.edit', task_id=task_id))
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            except ValueError:
                flash('Invalid deadline format', 'error')
                return redirect(url_for('tasks.edit', task_id=task_id))
        
        task.title = title
        task.description = description
        task.deadline = deadline
        task.priority = priority
        task.status = status
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.view', task_id=task_id))
    
    return render_template('tasks/edit.html',
                         task=task,
                         user=current_user)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new task."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        project_id = request.form.get('project_id')
        deadline_str = request.form.get('deadline', '')
        priority = request.form.get('priority', 'medium')
        
        if not title or not project_id:
            flash('Task title and project are required', 'error')
            return redirect(url_for('tasks.create'))
        
        # Check if user has access to the project
        project = Project.query.get_or_404(project_id)
        if project.admin_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('tasks.create'))
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
            except ValueError:
                flash('Invalid deadline format', 'error')
                return redirect(url_for('tasks.create'))
        
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
        return redirect(url_for('tasks.view', task_id=task.id))
    
    # Get user's projects for the form
    projects = Project.query.filter_by(admin_id=current_user.id).all()
    
    return render_template('tasks/create.html',
                         projects=projects,
                         user=current_user)

@bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete(task_id):
    """Delete a task."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('tasks.index'))
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.index'))
