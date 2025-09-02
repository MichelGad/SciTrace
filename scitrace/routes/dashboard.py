"""
Dashboard routes for SciTrace

Handles the main dashboard view with project and task overview.
"""

from flask import Blueprint, render_template, jsonify, flash
from flask_login import login_required, current_user
import os
import shutil

from ..services import ProjectService

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """Show the main dashboard."""
    project_service = ProjectService()
    
    try:
        dashboard_data = project_service.get_project_dashboard_data(current_user.id)
        
        # Get recent tasks and projects for display
        recent_tasks = dashboard_data['tasks'][:5]  # Show last 5 tasks
        recent_projects = dashboard_data['projects'][:3]  # Show last 3 projects
        recent_dataflows = dashboard_data['dataflows'][:3]  # Show last 3 dataflows
        
        return render_template('dashboard/index.html',
                             stats=dashboard_data['stats'],
                             tasks=recent_tasks,
                             projects=recent_projects,
                             dataflows=recent_dataflows,
                             user=current_user)
    except Exception as e:
        # Handle errors gracefully
        return render_template('dashboard/index.html',
                             stats={'total_projects': 0, 'ongoing_projects': 0, 
                                   'total_tasks': 0, 'pending_tasks': 0, 'urgent_tasks': 0, 'total_dataflows': 0},
                             tasks=[],
                             projects=[],
                             dataflows=[],
                             user=current_user,
                             error=str(e))

@bp.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """API endpoint to get dashboard data."""
    project_service = ProjectService()
    
    try:
        data = project_service.get_project_dashboard_data(current_user.id)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset', methods=['POST'])
@login_required
def reset_data():
    """Reset all projects and dataflows for the current user."""
    try:
        from ..models import Project, Task, Dataflow, db
        
        # Get all projects for the current user
        user_projects = Project.query.filter_by(admin_id=current_user.id).all()
        
        # Delete physical DataLad datasets first
        for project in user_projects:
            if project.dataset_path and os.path.exists(project.dataset_path):
                try:
                    # Remove the entire dataset directory
                    shutil.rmtree(project.dataset_path)
                    print(f"Deleted dataset directory: {project.dataset_path}")
                except Exception as e:
                    print(f"Warning: Could not delete dataset directory {project.dataset_path}: {e}")
        
        # Delete all tasks for these projects
        for project in user_projects:
            Task.query.filter_by(project_id=project.id).delete()
        
        # Delete all dataflows for these projects
        for project in user_projects:
            Dataflow.query.filter_by(project_id=project.id).delete()
        
        # Delete all projects for the current user
        Project.query.filter_by(admin_id=current_user.id).delete()
        
        # Commit the changes
        db.session.commit()
        
        flash('All projects, dataflows, and datasets have been reset successfully!', 'success')
        return jsonify({'success': True, 'message': 'Data reset successfully'})
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting data: {str(e)}', 'error')
        return jsonify({'error': str(e)}), 500
