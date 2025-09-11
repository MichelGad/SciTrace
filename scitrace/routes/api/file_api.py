"""
File API routes for SciTrace

Handles file operations, directory management, and file restoration functionality.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import os

from ...models import Dataflow
from ...services import FileOperationsService

bp = Blueprint('file_api', __name__, url_prefix='/api')

@bp.route('/open-folder', methods=['POST'])
@login_required
def open_folder():
    """Open a folder in the system file explorer."""
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path:
        return jsonify({'error': 'No folder path provided'}), 400
    
    try:
        import subprocess
        import platform
        
        # Open folder based on operating system
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', folder_path])
        elif platform.system() == 'Windows':
            subprocess.run(['explorer', folder_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])
        
        return jsonify({
            'success': True,
            'message': f'Opened folder: {folder_path}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/browse-directories', methods=['GET'])
@login_required
def browse_directories():
    """Browse directories for file selection."""
    import stat
    print(f"DEBUG: browse_directories called with path: {request.args.get('path', '/')}")
    path = request.args.get('path', '/')
    
    # Security: Ensure path is absolute and within allowed directories
    if not os.path.isabs(path):
        return jsonify({'error': 'Invalid path'}), 400
    
    # For security, restrict to user's home directory and common directories
    allowed_paths = [
        os.path.expanduser('~'),  # User's home directory
        '/Users',  # macOS users directory
        '/home',   # Linux users directory
        '/tmp',    # Temporary directory
        '/var/tmp' # Alternative temp directory
    ]
    
    # Check if path is within allowed directories
    path_allowed = False
    for allowed_path in allowed_paths:
        if os.path.exists(allowed_path) and path.startswith(allowed_path):
            path_allowed = True
            break
    
    print(f"DEBUG: Path {path} allowed: {path_allowed}")
    print(f"DEBUG: Allowed paths: {allowed_paths}")
    
    if not path_allowed:
        return jsonify({'error': 'Access denied to this directory'}), 403
    
    try:
        if not os.path.exists(path):
            return jsonify({'error': 'Directory does not exist'}), 404
        
        if not os.path.isdir(path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        directories = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            # Only include directories
            if os.path.isdir(item_path):
                try:
                    # Get directory permissions
                    st = os.stat(item_path)
                    permissions = stat.filemode(st.st_mode)
                    
                    directories.append({
                        'name': item,
                        'path': item_path,
                        'permissions': permissions,
                        'readable': os.access(item_path, os.R_OK),
                        'writable': os.access(item_path, os.W_OK)
                    })
                except (OSError, PermissionError):
                    # Skip directories we can't access
                    continue
        
        # Sort directories alphabetically
        directories.sort(key=lambda x: x['name'].lower())
        
        return jsonify({
            'success': True,
            'directories': directories,
            'current_path': path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/test-directory', methods=['GET'])
@login_required
def test_directory():
    """Test if a directory exists and is accessible."""
    directory_path = request.args.get('path')
    
    if not directory_path:
        return jsonify({'error': 'No directory path provided'}), 400
    
    try:
        # Use FileOperationsService to test directory
        file_service = FileOperationsService()
        result = file_service.test_directory_access(directory_path)
        
        return jsonify({
            'success': True,
            'exists': result.get('exists', False),
            'accessible': result.get('accessible', False),
            'path': directory_path,
            'message': result.get('message', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/create-directory', methods=['POST'])
@login_required
def create_directory():
    """Create a new directory."""
    data = request.get_json()
    parent_path = data.get('parent_path')
    dir_name = data.get('dir_name')
    
    if not parent_path or not dir_name:
        return jsonify({'error': 'Missing parent_path or dir_name'}), 400
    
    # Security: Ensure parent_path is absolute and within allowed directories
    if not os.path.isabs(parent_path):
        return jsonify({'error': 'Invalid parent path'}), 400
    
    # For security, restrict to user's home directory and common directories
    allowed_paths = [
        os.path.expanduser('~'),  # User's home directory
        '/Users',  # macOS users directory
        '/home',   # Linux users directory
        '/tmp',    # Temporary directory
        '/var/tmp' # Alternative temp directory
    ]
    
    # Check if parent_path is within allowed directories
    parent_allowed = False
    for allowed_path in allowed_paths:
        if os.path.exists(allowed_path) and parent_path.startswith(allowed_path):
            parent_allowed = True
            break
    
    if not parent_allowed:
        return jsonify({'error': 'Access denied to this directory'}), 403
    
    try:
        # Validate directory name
        if not dir_name or '/' in dir_name or '\\' in dir_name:
            return jsonify({'error': 'Invalid directory name'}), 400
        
        new_dir_path = os.path.join(parent_path, dir_name)
        
        # Check if directory already exists
        if os.path.exists(new_dir_path):
            return jsonify({'error': 'Directory already exists'}), 409
        
        # Create the directory
        os.makedirs(new_dir_path, mode=0o755)
        
        return jsonify({
            'success': True,
            'message': f'Directory "{dir_name}" created successfully',
            'path': new_dir_path
        })
        
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/restore-file', methods=['POST'])
@login_required
def restore_file(dataflow_id):
    """Restore a file from a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    file_path = data.get('file_path')
    commit_hash = data.get('commit_hash')
    
    if not file_path or not commit_hash:
        return jsonify({'error': 'Both file_path and commit_hash are required'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use GitOperationsService to restore file
        from ...services.git_operations import GitOperationsService
        git_service = GitOperationsService()
        result = git_service.restore_file_to_commit(dataset_path, file_path, commit_hash)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': f'File {file_path} restored from commit {commit_hash}',
                'output': result.get('output', '')
            })
        else:
            return jsonify({'error': result.get('error', 'Failed to restore file')}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/file-commit-history', methods=['GET'])
@login_required
def get_file_commit_history(dataflow_id):
    """Get commit history for a specific file."""
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
        
        # Use GitOperationsService to get file commit history
        from ...services.git_operations import GitOperationsService
        git_service = GitOperationsService()
        commit_history = git_service.get_file_commit_history(dataset_path, file_path)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'commit_history': commit_history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
