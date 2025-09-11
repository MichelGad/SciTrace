"""
Git API routes for SciTrace

Handles git operations and version control functionality for datasets.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from ...models import Dataflow
from ...services import GitOperationsService

bp = Blueprint('git_api', __name__, url_prefix='/api')

@bp.route('/dataflows/<int:dataflow_id>/git-log', methods=['GET'])
@login_required
def get_git_log(dataflow_id):
    """Get git log for a dataflow's dataset."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Get limit from query parameters
        limit = request.args.get('limit', 20, type=int)
        
        # Use GitOperationsService to get git log
        git_service = GitOperationsService()
        git_log = git_service.get_detailed_git_log(dataset_path, limit)
        
        return jsonify({
            'success': True,
            'git_log': git_log
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/commit-files/<commit_hash>', methods=['GET'])
@login_required
def get_commit_files(dataflow_id, commit_hash):
    """Get files changed in a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to get commit files
        git_service = GitOperationsService()
        commit_files = git_service.get_commit_files(dataset_path, commit_hash)
        
        return jsonify({
            'success': True,
            'commit_files': commit_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/commit-file-content/<commit_hash>', methods=['GET'])
@login_required
def get_commit_file_content(dataflow_id, commit_hash):
    """Get content of a specific file at a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    file_path = request.args.get('file_path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to get file content
        git_service = GitOperationsService()
        file_content = git_service.get_file_content_at_commit(dataset_path, commit_hash, file_path)
        
        return jsonify({
            'success': True,
            'file_content': file_content,
            'file_path': file_path,
            'commit_hash': commit_hash
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/revert', methods=['POST'])
@login_required
def revert_commit(dataflow_id):
    """Revert a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    commit_hash = data.get('commit_hash')
    commit_message = data.get('commit_message', f'Revert commit {commit_hash}')
    
    if not commit_hash:
        return jsonify({'error': 'No commit hash provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to revert commit
        git_service = GitOperationsService()
        result = git_service.revert_commit(dataset_path, commit_hash, commit_message)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Commit {commit_hash} has been reverted',
                'output': result.get('output', '')
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to revert commit')}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/checkout', methods=['POST'])
@login_required
def checkout_commit(dataflow_id):
    """Checkout a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    commit_hash = data.get('commit_hash')
    
    if not commit_hash:
        return jsonify({'error': 'No commit hash provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to checkout commit
        git_service = GitOperationsService()
        result = git_service.checkout_commit(dataset_path, commit_hash)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Checked out commit {commit_hash}',
                'output': result.get('output', '')
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to checkout commit')}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/commit-files', methods=['GET'])
@login_required
def get_commit_files_git_ops(dataflow_id):
    """Get files changed in a specific commit (git operations endpoint)."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    commit_hash = request.args.get('commit_hash')
    if not commit_hash:
        return jsonify({'error': 'No commit hash provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to get commit files
        git_service = GitOperationsService()
        commit_files = git_service.get_commit_files(dataset_path, commit_hash)
        
        return jsonify({
            'success': True,
            'commit_files': commit_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/file-diff', methods=['GET'])
@login_required
def get_file_diff_git_ops(dataflow_id):
    """Get diff for a specific file at a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    commit_hash = request.args.get('commit_hash')
    file_path = request.args.get('file_path')
    
    if not commit_hash or not file_path:
        return jsonify({'error': 'Both commit_hash and file_path are required'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to get file diff
        git_service = GitOperationsService()
        file_diff = git_service.get_file_diff(dataset_path, commit_hash, file_path)
        
        return jsonify({
            'success': True,
            'file_diff': file_diff,
            'file_path': file_path,
            'commit_hash': commit_hash
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/branch', methods=['POST'])
@login_required
def create_branch_git_ops(dataflow_id):
    """Create a new branch from a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    commit_hash = data.get('commit_hash')
    branch_name = data.get('branch_name')
    
    if not commit_hash or not branch_name:
        return jsonify({'error': 'Both commit_hash and branch_name are required'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to create branch
        git_service = GitOperationsService()
        result = git_service.create_branch_from_commit(dataset_path, commit_hash, branch_name)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Branch {branch_name} created from commit {commit_hash}',
                'output': result.get('output', '')
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to create branch')}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/compare', methods=['GET'])
@login_required
def compare_commit_git_ops(dataflow_id):
    """Compare a commit with the current working directory."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    commit_hash = request.args.get('commit_hash')
    if not commit_hash:
        return jsonify({'error': 'No commit hash provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to compare commit
        git_service = GitOperationsService()
        comparison = git_service.compare_commit_to_local(dataset_path, commit_hash)
        
        return jsonify({
            'success': True,
            'comparison': comparison,
            'commit_hash': commit_hash
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/current-branch', methods=['GET'])
@login_required
def get_current_branch(dataflow_id):
    """Get the current branch name."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to get current branch
        git_service = GitOperationsService()
        current_branch = git_service.get_current_branch(dataset_path)
        
        return jsonify({
            'success': True,
            'current_branch': current_branch
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-tree', methods=['GET'])
@login_required
def get_git_tree(dataflow_id):
    """Get git tree structure for a dataflow's dataset."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Get limit from query parameters
        limit = request.args.get('limit', 20, type=int)
        
        # Use GitOperationsService to get git tree
        git_service = GitOperationsService()
        git_tree = git_service.get_detailed_git_log(dataset_path, limit)
        
        return jsonify({
            'success': True,
            'commits': git_tree
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
