"""
Project API routes for SciTrace

Handles project-related API endpoints including dataset info and file tree operations.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import os

from ...models import db, Project, Task
from ...services import DatasetCreationService, FileOperationsService

bp = Blueprint('project_api', __name__, url_prefix='/api')

@bp.route('/tasks/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Update the status of a task."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    try:
        task.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Task status updated to {new_status}',
            'task_id': task_id,
            'new_status': new_status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/dataset-info')
@login_required
def get_dataset_info(project_id):
    """Get dataset information for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Use DatasetCreationService to get dataset info
        dataset_service = DatasetCreationService()
        dataset_info = dataset_service.get_dataset_info(project.dataset_path)
        
        return jsonify({
            'success': True,
            'dataset_info': dataset_info,
            'project_id': project_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/file-tree')
@login_required
def get_project_file_tree(project_id):
    """Get file tree structure for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use FileOperationsService to get file tree
        file_service = FileOperationsService()
        file_tree = file_service.get_file_tree(dataset_path)
        
        return jsonify({
            'success': True,
            'file_tree': file_tree,
            'project_id': project_id,
            'dataset_path': dataset_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
