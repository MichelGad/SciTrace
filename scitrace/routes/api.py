"""
API routes for SciTrace

Handles AJAX requests and API endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import os
import stat

from ..models import Project, Task, Dataflow, db
from ..services import DataLadService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/tasks/<int:task_id>/update-status', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Update task status."""
    task = Task.query.get_or_404(task_id)
    
    # Check if user has access to this task
    if task.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status in ['pending', 'ongoing', 'done']:
        task.status = new_status
        db.session.commit()
        return jsonify({'success': True, 'status': new_status})
    else:
        return jsonify({'error': 'Invalid status'}), 400

@bp.route('/projects/<int:project_id>/dataset-info')
@login_required
def get_dataset_info(project_id):
    """Get DataLad dataset information for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.dataset_path:
        return jsonify({'error': 'No dataset path found'}), 404
    
    try:
        datalad_service = DataLadService()
        dataset_info = datalad_service.get_dataset_info(project.dataset_path)
        return jsonify(dataset_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/projects/<int:project_id>/file-tree')
@login_required
def get_file_tree(project_id):
    """Get file tree structure for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if not project.dataset_path:
        return jsonify({'error': 'No dataset path found'}), 404
    
    try:
        datalad_service = DataLadService()
        file_tree = datalad_service.get_file_tree(project.dataset_path)
        return jsonify(file_tree)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/regenerate', methods=['POST'])
@login_required
def regenerate_dataflow(dataflow_id):
    """Regenerate dataflow from dataset structure."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get dataset path from project or try to find it
    dataset_path = dataflow.project.dataset_path
    if not dataset_path:
        # Try to find dataset path from metadata
        try:
            metadata = dataflow.get_metadata()
            dataset_path = metadata.get('dataset_path')
        except:
            pass
        
        # If still not found, try to find it in the expected location
        if not dataset_path:
            home_dir = os.path.expanduser("~")
            expected_path = os.path.join(home_dir, "scitrace_datasets", "DOM_ENV_MODEL")
            if os.path.exists(expected_path):
                dataset_path = expected_path
                # Update the project with the found path
                dataflow.project.dataset_path = dataset_path
                db.session.commit()
    
    if not dataset_path:
        return jsonify({'error': 'No dataset path found'}), 404
    
    try:
        datalad_service = DataLadService()
        dataflow_data = datalad_service.create_dataflow_from_dataset(dataset_path)
        
        dataflow.set_nodes(dataflow_data['nodes'])
        dataflow.set_edges(dataflow_data['edges'])
        dataflow.set_metadata(dataflow_data['metadata'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dataflow regenerated successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/stage/<stage_name>')
@login_required
def get_stage_files(dataflow_id, stage_name):
    """Get files and metadata for a specific stage in a dataflow."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get dataset path from project (dynamic) or fallback to metadata
    dataset_path = dataflow.project.dataset_path
    if not dataset_path:
        # Fallback to metadata if project path is not set
        try:
            metadata = dataflow.get_metadata()
            dataset_path = metadata.get('dataset_path')
        except:
            pass
    
    if not dataset_path:
        return jsonify({'error': 'No dataset path found'}), 404
    
    # Map node types to directory names
    stage_mapping = {
        'raw_data': 'raw_data',
        'preprocessing': 'preprocessed',
        'analysis': 'analysis',
        'modeling': 'models',
        'visualization': 'visualizations'
    }
    
    # Get the actual directory name
    directory_name = stage_mapping.get(stage_name, stage_name)
    
    print(f"DEBUG: get_stage_files called with dataflow_id={dataflow_id}, stage_name={stage_name}")
    print(f"DEBUG: Found dataflow: {dataflow.name}, project: {dataflow.project.name}")
    print(f"DEBUG: Dataset path: {dataset_path}")
    print(f"DEBUG: Mapped directory name: {directory_name}")
    
    try:
        datalad_service = DataLadService()
        stage_data = datalad_service.get_stage_files(dataset_path, directory_name)
        
        if stage_data is None:
            print(f"DEBUG: Dataset not found at {dataflow.project.dataset_path}")
            return jsonify({'error': 'Dataset not found'}), 404
        
        print(f"DEBUG: Successfully retrieved stage data for {directory_name}")
        return jsonify(stage_data)
    except Exception as e:
        print(f"DEBUG: Error in get_stage_files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/open-folder', methods=['POST'])
@login_required
def open_folder():
    """Open a folder in the system's file explorer."""
    data = request.get_json()
    folder_path = data.get('folder_path')
    
    if not folder_path:
        return jsonify({'error': 'No folder path provided'}), 400
    
    # Security: Ensure path is within allowed directories
    allowed_paths = [
        os.path.expanduser('~'),  # Home directory
        '/Users',
        '/home',
        '/tmp',
        '/var/tmp'
    ]
    
    # Check if the folder path is within allowed directories
    folder_path = os.path.abspath(folder_path)
    is_allowed = any(folder_path.startswith(allowed_path) for allowed_path in allowed_paths)
    
    if not is_allowed:
        return jsonify({'error': 'Access denied: Path not in allowed directories'}), 403
    
    if not os.path.exists(folder_path):
        return jsonify({'error': 'Folder does not exist'}), 404
    
    try:
        # Open folder in file explorer based on operating system
        import platform
        import subprocess
        
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(['open', folder_path], check=True)
        elif system == "Windows":
            subprocess.run(['explorer', folder_path], check=True)
        elif system == "Linux":
            # Try different file managers
            file_managers = ['xdg-open', 'nautilus', 'dolphin', 'thunar', 'pcmanfm']
            for fm in file_managers:
                try:
                    subprocess.run([fm, folder_path], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                return jsonify({'error': 'No file manager found on Linux'}), 500
        else:
            return jsonify({'error': f'Unsupported operating system: {system}'}), 500
        
        return jsonify({
            'success': True,
            'message': f'Folder opened successfully: {folder_path}'
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Failed to open folder: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@bp.route('/setup-demo', methods=['POST'])
@login_required
def setup_demo():
    """Set up demo project and dataflow."""
    # Check if user is admin
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied. Admin role required.'}), 403
    
    try:
        # Import the demo setup function
        import subprocess
        import sys
        
        # Run the demo setup script
        result = subprocess.run([sys.executable, 'setup_demo.py'], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Demo setup completed successfully'})
        else:
            return jsonify({'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/stats/dashboard')
@login_required
def dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Count user's projects
        total_projects = Project.query.filter_by(admin_id=current_user.id).count()
        ongoing_projects = Project.query.filter_by(admin_id=current_user.id, status='ongoing').count()
        
        # Count user's tasks
        total_tasks = Task.query.filter_by(user_id=current_user.id).count()
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').count()
        urgent_tasks = Task.query.filter_by(user_id=current_user.id, priority='urgent').count()
        
        return jsonify({
            'total_projects': total_projects,
            'ongoing_projects': ongoing_projects,
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'urgent_tasks': urgent_tasks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Reset all data for the current user using reset_data.py script."""
    try:
        import subprocess
        import sys
        
        # Run the reset_data.py script for the current user
        result = subprocess.run([
            sys.executable, 'reset_data.py', 'user', str(current_user.id)
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            return jsonify({
                'success': True, 
                'message': 'All data has been reset successfully!'
            })
        else:
            return jsonify({
                'error': f'Reset failed: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/browse-directories')
@login_required
def browse_directories():
    """Browse directories for file selection."""
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

@bp.route('/test-directory')
@login_required
def test_directory():
    """Test directory access without restrictions."""
    try:
        test_path = '/Users/michelgad'
        if os.path.exists(test_path) and os.path.isdir(test_path):
            items = os.listdir(test_path)
            directories = [item for item in items if os.path.isdir(os.path.join(test_path, item))]
            return jsonify({
                'success': True,
                'path': test_path,
                'exists': True,
                'is_dir': True,
                'total_items': len(items),
                'directories': directories[:5]  # First 5 directories
            })
        else:
            return jsonify({
                'success': False,
                'path': test_path,
                'exists': os.path.exists(test_path),
                'is_dir': os.path.isdir(test_path) if os.path.exists(test_path) else False
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-all-data', methods=['POST'])
@login_required
def reset_all_data():
    """Reset all data for the current user (projects, tasks, dataflows)."""
    try:
        # Delete all dataflows for user's projects
        user_projects = Project.query.filter_by(admin_id=current_user.id).all()
        for project in user_projects:
            dataflows = Dataflow.query.filter_by(project_id=project.id).all()
            for dataflow in dataflows:
                db.session.delete(dataflow)
        
        # Delete all tasks for the user
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        for task in tasks:
            db.session.delete(task)
        
        # Delete all projects for the user
        for project in user_projects:
            db.session.delete(project)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All data has been reset successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-projects', methods=['POST'])
@login_required
def reset_projects():
    """Reset only projects for the current user."""
    try:
        # Delete all dataflows for user's projects
        user_projects = Project.query.filter_by(admin_id=current_user.id).all()
        for project in user_projects:
            dataflows = Dataflow.query.filter_by(project_id=project.id).all()
            for dataflow in dataflows:
                db.session.delete(dataflow)
        
        # Delete all projects for the user
        for project in user_projects:
            db.session.delete(project)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All projects have been reset successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-tasks', methods=['POST'])
@login_required
def reset_tasks():
    """Reset only tasks for the current user."""
    try:
        # Delete all tasks for the user
        tasks = Task.query.filter_by(user_id=current_user.id).all()
        for task in tasks:
            db.session.delete(task)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All tasks have been reset successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-dataflows', methods=['POST'])
@login_required
def reset_dataflows():
    """Reset only dataflows for the current user."""
    try:
        # Delete all dataflows for user's projects
        user_projects = Project.query.filter_by(admin_id=current_user.id).all()
        for project in user_projects:
            dataflows = Dataflow.query.filter_by(project_id=project.id).all()
            for dataflow in dataflows:
                db.session.delete(dataflow)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All dataflows have been reset successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
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

@bp.route('/dataflows/<int:dataflow_id>/add-file-to-datalad', methods=['POST'])
@login_required
def add_file_to_datalad(dataflow_id):
    """Add a specific file to DataLad."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    file_path = data.get('file_path')
    commit_message = data.get('commit_message', 'Add file to DataLad')
    
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Construct full file path
        full_file_path = os.path.join(dataset_path, file_path)
        
        # Verify file exists
        if not os.path.exists(full_file_path):
            return jsonify({'error': f'File not found: {full_file_path}'}), 404
        
        # Add file directly with datalad save (adds and commits in one step)
        import subprocess
        
        # Use datalad save with file path to add and commit specific file
        result = subprocess.run(['datalad', 'save', '-m', commit_message, file_path], 
                              cwd=dataset_path, capture_output=True, text=True, check=True)
        
        return jsonify({
            'success': True,
            'message': f'File {os.path.basename(file_path)} has been added to DataLad'
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'DataLad operation failed: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/add-all-untracked-to-datalad', methods=['POST'])
@login_required
def add_all_untracked_to_datalad(dataflow_id):
    """Add all untracked files in a stage to DataLad."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    stage_name = data.get('stage_name')
    commit_message = data.get('commit_message', 'Add untracked files')
    
    if not stage_name:
        return jsonify({'error': 'No stage name provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Construct stage path
        stage_path = os.path.join(dataset_path, stage_name)
        
        # Verify stage exists
        if not os.path.exists(stage_path):
            return jsonify({'error': 'Stage directory not found'}), 404
        
        import subprocess
        
        # Add all files in the stage directory directly with datalad save
        result = subprocess.run(['datalad', 'save', '-m', commit_message, stage_name + '/'], 
                              cwd=dataset_path, capture_output=True, text=True, check=True)
        
        return jsonify({
            'success': True,
            'message': f'All untracked files in {stage_name} have been added to DataLad'
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'DataLad operation failed: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/run-script', methods=['POST'])
@login_required
def run_script_with_datalad(dataflow_id):
    """Run a script file using datalad run with input/output tracking."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    script_path = data.get('script_path')
    commit_message = data.get('commit_message', 'Run script')
    inputs = data.get('inputs', [])  # List of input file paths
    outputs = data.get('outputs', [])  # List of output file paths
    command = data.get('command', '')  # The actual command to run
    
    if not script_path:
        return jsonify({'error': 'No script path provided'}), 400
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Construct full script path
        full_script_path = os.path.join(dataset_path, script_path)
        
        # Verify script exists
        if not os.path.exists(full_script_path):
            return jsonify({'error': f'Script not found: {full_script_path}'}), 404
        
        import subprocess
        
        # Build datalad run command
        cmd = ['datalad', 'run', '-m', commit_message]
        
        # Add input files
        for input_file in inputs:
            if input_file.strip():
                cmd.extend(['-i', input_file])
        
        # Add output files
        for output_file in outputs:
            if output_file.strip():
                cmd.extend(['-o', output_file])
        
        # Add the actual command, converting python to python3 if needed
        if command.startswith('python '):
            command = command.replace('python ', 'python3 ', 1)
        cmd.append(command)
        
        # Execute datalad run
        result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
        
        return jsonify({
            'success': True,
            'message': f'Script {os.path.basename(script_path)} executed successfully with DataLad tracking',
            'output': result.stdout,
            'command': ' '.join(cmd)
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({
            'error': f'DataLad run failed: {e.stderr}',
            'command': ' '.join(cmd) if 'cmd' in locals() else 'Unknown'
        }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dataflows/<int:dataflow_id>/restore-file', methods=['POST'])
@login_required
def restore_deleted_file(dataflow_id):
    """Restore a deleted file from a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    file_path = data.get('file_path')
    file_name = data.get('file_name')
    commit_hash = data.get('commit_hash')
    commit_message = data.get('commit_message')
    
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    if not commit_hash:
        return jsonify({'error': 'No commit hash provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use the Project service to restore the file
        from ..services import ProjectService
        project_service = ProjectService()
        
        result = project_service.restore_file_to_commit(
            dataset_path, file_path, commit_hash, commit_message
        )
        
        return jsonify({
            'success': True,
            'message': f'File {file_name} has been restored from commit {commit_hash}'
        })
        
    except Exception as e:
        # Get more detailed error information
        error_details = {
            'error': f'File restoration failed: {str(e)}',
            'file_path': file_path,
            'commit_hash': commit_hash,
            'dataset_path': dataset_path
        }
        
        # If it's a subprocess error, add more details
        if hasattr(e, 'returncode'):
            error_details['return_code'] = e.returncode
        if hasattr(e, 'stderr'):
            error_details['stderr'] = e.stderr
        if hasattr(e, 'stdout'):
            error_details['stdout'] = e.stdout
            
        return jsonify(error_details), 500

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
        
        # Use the Project service to get commit history
        from ..services import ProjectService
        project_service = ProjectService()
        
        commits = project_service.get_file_commit_history(dataset_path, file_path, limit=10)
        
        return jsonify({
            'success': True,
            'commits': commits
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get commit history: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/save-stage', methods=['POST'])
@login_required
def save_stage(dataflow_id):
    """Save a stage to DataLad, committing any changes including deletions."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    stage_name = data.get('stage_name')
    commit_message = data.get('commit_message', 'Save stage changes')
    
    if not stage_name:
        return jsonify({'error': 'No stage name provided'}), 400
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Construct stage path
        stage_path = os.path.join(dataset_path, stage_name)
        
        # Verify stage exists
        if not os.path.exists(stage_path):
            return jsonify({'error': 'Stage directory not found'}), 404
        
        import subprocess
        
        # Save the stage using datalad save (this will commit all changes including deletions)
        result = subprocess.run(['datalad', 'save', '-m', commit_message, stage_name + '/'], 
                              cwd=dataset_path, capture_output=True, text=True, check=True)
        
        return jsonify({
            'success': True,
            'message': f'Stage {stage_name} has been saved to DataLad',
            'commit_message': commit_message
        })
        
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'DataLad save failed: {e.stderr}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/debug/git-test', methods=['POST'])
@login_required
def debug_git_test():
    """Debug endpoint to test git commands directly."""
    data = request.get_json()
    dataset_path = data.get('dataset_path')
    file_path = data.get('file_path')
    
    if not dataset_path or not file_path:
        return jsonify({'error': 'Missing dataset_path or file_path'}), 400
    
    try:
        import subprocess
        
        # Test basic git log command
        cmd = ['git', 'log', '--oneline', '--follow', '-n', '5', '--', file_path]
        result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=False)
        
        # Test without --follow
        cmd_no_follow = ['git', 'log', '--oneline', '-n', '5', '--', file_path]
        result_no_follow = subprocess.run(cmd_no_follow, cwd=dataset_path, capture_output=True, text=True, check=False)
        
        # Test general git log
        cmd_general = ['git', 'log', '--oneline', '-n', '5']
        result_general = subprocess.run(cmd_general, cwd=dataset_path, capture_output=True, text=True, check=False)
        
        return jsonify({
            'success': True,
            'tests': {
                'with_follow': {
                    'command': ' '.join(cmd),
                    'return_code': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                },
                'without_follow': {
                    'command': ' '.join(cmd_no_follow),
                    'return_code': result_no_follow.returncode,
                    'stdout': result_no_follow.stdout,
                    'stderr': result_no_follow.stderr
                },
                'general_log': {
                    'command': ' '.join(cmd_general),
                    'return_code': result_general.returncode,
                    'stdout': result_general.stdout,
                    'stderr': result_general.stderr
                }
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Debug test failed: {str(e)}'}), 500

@bp.route('/debug/file-restore-debug', methods=['POST'])
@login_required
def debug_file_restore():
    """Debug endpoint to troubleshoot file restoration issues."""
    data = request.get_json()
    dataset_path = data.get('dataset_path')
    file_path = data.get('file_path')
    commit_hash = data.get('commit_hash')
    
    if not dataset_path or not file_path or not commit_hash:
        return jsonify({'error': 'Missing dataset_path, file_path, or commit_hash'}), 400
    
    try:
        # Use the Project service to debug the restore
        from ..services import ProjectService
        project_service = ProjectService()
        
        debug_info = project_service.debug_file_restore(dataset_path, file_path, commit_hash)
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Debug failed: {str(e)}'}), 500

@bp.route('/debug/git-config', methods=['POST'])
@login_required
def debug_git_config():
    """Debug endpoint to check git configuration."""
    data = request.get_json()
    dataset_path = data.get('dataset_path')
    
    if not dataset_path:
        return jsonify({'error': 'Missing dataset_path'}), 400
    
    try:
        # Use the Project service to check git config
        from ..services import ProjectService
        project_service = ProjectService()
        
        config_info = project_service.check_git_config(dataset_path)
        
        return jsonify({
            'success': True,
            'config_info': config_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Git config check failed: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-log', methods=['GET'])
@login_required
def get_git_log(dataflow_id):
    """Get detailed git log for a dataflow's dataset."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Get limit parameter
        limit = request.args.get('limit', 50, type=int)
        if limit > 100:  # Cap at 100 commits
            limit = 100
        
        # Use the Project service to get detailed git log
        from ..services import ProjectService
        project_service = ProjectService()
        
        commits = project_service.get_detailed_git_log(dataset_path, limit=limit)
        
        return jsonify({
            'success': True,
            'commits': commits,
            'total_commits': len(commits)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get git log: {str(e)}'}), 500

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
        
        # Use the Project service to get commit files
        from ..services import ProjectService
        project_service = ProjectService()
        
        files = project_service.get_commit_files(dataset_path, commit_hash)
        
        return jsonify({
            'success': True,
            'commit_hash': commit_hash,
            'files': files,
            'total_files': len(files)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get commit files: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/commit-file-content/<commit_hash>', methods=['GET'])
@login_required
def get_commit_file_content(dataflow_id, commit_hash):
    """Get file content at a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Get file path from query parameter
        file_path = request.args.get('file_path')
        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400
        
        # Use the Project service to get file content
        from ..services import ProjectService
        project_service = ProjectService()
        
        content = project_service.get_file_content_at_commit(dataset_path, commit_hash, file_path)
        
        return jsonify({
            'success': True,
            'commit_hash': commit_hash,
            'file_path': file_path,
            'content': content
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get file content: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/revert', methods=['POST'])
@login_required
def revert_commit(dataflow_id):
    """Revert a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        commit_hash = data.get('commit_hash')
        commit_message = data.get('commit_message')
        
        if not commit_hash:
            return jsonify({'error': 'No commit hash provided'}), 400
        
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use the Project service to revert commit
        from ..services import ProjectService
        project_service = ProjectService()
        
        result = project_service.revert_commit(dataset_path, commit_hash, commit_message)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to revert commit: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/new-branch', methods=['POST'])
@login_required
def create_branch(dataflow_id):
    """Create a new branch from a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        commit_hash = data.get('commit_hash')
        branch_name = data.get('branch_name')
        
        if not commit_hash or not branch_name:
            return jsonify({'error': 'Commit hash and branch name are required'}), 400
        
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use the Project service to create branch
        from ..services import ProjectService
        project_service = ProjectService()
        
        result = project_service.create_branch_from_commit(dataset_path, commit_hash, branch_name)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to create branch: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/checkout', methods=['POST'])
@login_required
def checkout_commit(dataflow_id):
    """Checkout a specific commit."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        commit_hash = data.get('commit_hash')
        
        if not commit_hash:
            return jsonify({'error': 'No commit hash provided'}), 400
        
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use the Project service to checkout commit
        from ..services import ProjectService
        project_service = ProjectService()
        
        result = project_service.checkout_commit(dataset_path, commit_hash)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to checkout commit: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-operations/compare', methods=['GET'])
@login_required
def compare_commit(dataflow_id):
    """Compare a commit to the current local state."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        commit_hash = request.args.get('commit_hash')
        
        if not commit_hash:
            return jsonify({'error': 'No commit hash provided'}), 400
        
        # Get dataset path
        dataset_path = dataflow.project.dataset_path
        if not dataset_path:
            return jsonify({'error': 'No dataset path found'}), 404
        
        # Use the Project service to compare commit
        from ..services import ProjectService
        project_service = ProjectService()
        
        result = project_service.compare_commit_to_local(dataset_path, commit_hash)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Failed to compare commit: {str(e)}'}), 500

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
        
        # Use the Project service to get current branch
        from ..services import ProjectService
        project_service = ProjectService()
        
        branch_name = project_service.get_current_branch(dataset_path)
        
        return jsonify({
            'success': True,
            'current_branch': branch_name
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get current branch: {str(e)}'}), 500

@bp.route('/dataflows/<int:dataflow_id>/git-tree', methods=['GET'])
@login_required
def get_git_tree(dataflow_id):
    """Get git log with tree structure and branch information."""
    try:
        # Get the dataflow
        dataflow = Dataflow.query.get_or_404(dataflow_id)
        
        # Check if user has access to this dataflow
        if not current_user.has_access_to_dataflow(dataflow):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        # Get the dataset path
        dataset_path = dataflow.dataset_path
        if not dataset_path or not os.path.exists(dataset_path):
            return jsonify({'success': False, 'error': 'Dataset path not found'}), 404
        
        # Get limit parameter
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Cap at 100 commits
        
        # Get git tree structure
        project_service = ProjectService()
        result = project_service.get_git_tree_structure(dataset_path, limit)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
