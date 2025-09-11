"""
Admin API routes for SciTrace

Handles demo setup, system operations, and administrative functionality.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import subprocess
import os

from ...models import db, Project, Dataflow, Task, User

bp = Blueprint('admin_api', __name__, url_prefix='/api')

@bp.route('/setup-demo', methods=['POST'])
@login_required
def setup_demo():
    """Set up demo environment with sample projects."""
    print(f"🚀 Starting demo setup for user: {current_user.username}")
    
    try:
        # Reset database to prepare for demo setup
        print("🧹 Resetting database to prepare for demo setup...")
        
        # Delete all existing dataflows, tasks, and projects
        try:
            # Delete in order to respect foreign key constraints
            Dataflow.query.delete()
            Task.query.delete()
            Project.query.delete()
            
            # Commit the deletions
            db.session.commit()
            print("✅ Database reset completed successfully")
        except Exception as e:
            print(f"⚠️ Database reset failed: {e}")
            # Try to rollback and continue
            db.session.rollback()
            # Force delete all tables and recreate
            db.drop_all()
            db.create_all()
            print("✅ Database recreated successfully")
        
        # Run the demo setup script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'setup_demo_datalad.py')
        script_path = os.path.abspath(script_path)
        
        print(f"📝 Running demo setup script: {script_path}")
        
        # Run the script with the virtual environment's Python and proper environment
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'venv')
        python_path = os.path.join(venv_path, 'bin', 'python')
        
        if not os.path.exists(python_path):
            # Fallback to system python3
            python_path = 'python3'
            env = None
        else:
            # Set up environment with virtual environment's PATH
            env = os.environ.copy()
            venv_bin = os.path.join(venv_path, 'bin')
            if 'PATH' in env:
                env['PATH'] = f"{venv_bin}:{env['PATH']}"
            else:
                env['PATH'] = venv_bin
        
        result = subprocess.run([python_path, script_path], capture_output=True, text=True, env=env)
        
        print(f"📊 Demo setup completed with return code: {result.returncode}")
        print(f"📝 STDOUT: {result.stdout}")
        
        if result.stderr:
            print(f"⚠️ STDERR: {result.stderr}")
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Demo environment setup completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'error': f'Demo setup failed with return code {result.returncode}',
                'stderr': result.stderr,
                'stdout': result.stdout
            }), 500
            
    except Exception as e:
        print(f"❌ Demo setup failed: {str(e)}")
        return jsonify({
            'error': f'Demo setup failed: {str(e)}'
        }), 500

@bp.route('/check-prerequisites', methods=['POST'])
@login_required
def check_prerequisites():
    """Check system prerequisites for SciTrace."""
    print(f"🔍 Checking prerequisites for user: {current_user.username}")
    
    try:
        # Check DataLad availability with proper environment
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'venv')
        venv_bin = os.path.join(venv_path, 'bin')
        
        # Set up environment with virtual environment's PATH
        env = os.environ.copy()
        if 'PATH' in env:
            env['PATH'] = f"{venv_bin}:{env['PATH']}"
        else:
            env['PATH'] = venv_bin
        
        # Use full path to datalad
        datalad_path = '/opt/homebrew/bin/datalad'
        if not os.path.exists(datalad_path):
            datalad_path = 'datalad'  # fallback
        
        datalad_result = subprocess.run([datalad_path, '--version'], capture_output=True, text=True, env=env)
        datalad_available = datalad_result.returncode == 0
        datalad_version = datalad_result.stdout.strip() if datalad_available else "Not available"
        
        # Check write permissions for demo datasets directory
        demo_dir = os.path.expanduser("~/scitrace_demo_datasets")
        write_permissions = True
        try:
            os.makedirs(demo_dir, exist_ok=True)
            test_file = os.path.join(demo_dir, "test_write_permissions.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception:
            write_permissions = False
        
        # Check database connectivity
        db_connectivity = True
        try:
            user_count = User.query.count()
        except Exception:
            db_connectivity = False
            user_count = 0
        
        # Compile results
        results = {
            'datalad_available': datalad_available,
            'datalad_version': datalad_version,
            'write_permissions': write_permissions,
            'demo_directory': demo_dir,
            'db_connectivity': db_connectivity,
            'user_count': user_count
        }
        
        # Determine overall status
        all_good = datalad_available and write_permissions and db_connectivity
        
        if all_good:
            print("✅ All prerequisites check passed")
            return jsonify({
                'success': True,
                'message': 'All prerequisites are satisfied',
                'results': results
            })
        else:
            print("❌ Some prerequisites are not satisfied")
            return jsonify({
                'success': False,
                'message': 'Some prerequisites are not satisfied',
                'results': results
            }), 400
            
    except Exception as e:
        print(f"❌ Prerequisites check failed: {str(e)}")
        return jsonify({
            'error': f'Prerequisites check failed: {str(e)}'
        }), 500

@bp.route('/stats/dashboard')
@login_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        # Get counts
        project_count = Project.query.count()
        dataflow_count = Dataflow.query.count()
        task_count = Task.query.count()
        user_count = User.query.count()
        
        return jsonify({
            'success': True,
            'stats': {
                'projects': project_count,
                'dataflows': dataflow_count,
                'tasks': task_count,
                'users': user_count
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Reset all data in the system including datasets."""
    try:
        # Delete all dataflows, tasks, and projects
        Dataflow.query.delete()
        Task.query.delete()
        Project.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        # Get the DataLad base path from configuration
        from ...config.config import Config
        datalad_base_path = Config.DATALAD_BASE_PATH
        
        # Also check the default path in case it's different
        default_demo_dir = os.path.expanduser("~/scitrace_demo_datasets")
        
        # Remove all dataset directories
        removed_dirs = []
        failed_dirs = []
        
        for dataset_dir in [datalad_base_path, default_demo_dir]:
            if os.path.exists(dataset_dir):
                try:
                    # First, try to remove individual datasets with DataLad
                    if os.path.isdir(dataset_dir):
                        for item in os.listdir(dataset_dir):
                            item_path = os.path.join(dataset_dir, item)
                            if os.path.isdir(item_path):
                                try:
                                    # Try DataLad remove for individual datasets
                                    result = subprocess.run(
                                        ['datalad', 'remove', '--recursive', item_path], 
                                        capture_output=True, text=True, timeout=30
                                    )
                                    if result.returncode == 0:
                                        print(f"✅ Removed dataset: {item_path}")
                                        removed_dirs.append(item_path)
                                    else:
                                        print(f"⚠️ DataLad remove failed for {item_path}: {result.stderr}")
                                        # Try direct removal
                                        subprocess.run(['rm', '-rf', item_path], timeout=30)
                                        removed_dirs.append(item_path)
                                except Exception as e:
                                    print(f"⚠️ Failed to remove dataset {item_path}: {e}")
                                    # Try direct removal as fallback
                                    try:
                                        subprocess.run(['rm', '-rf', item_path], timeout=30)
                                        removed_dirs.append(item_path)
                                    except Exception as e2:
                                        print(f"❌ Failed to remove {item_path}: {e2}")
                                        failed_dirs.append(item_path)
                    
                    # Remove the base directory if it's empty
                    try:
                        if os.path.exists(dataset_dir) and not os.listdir(dataset_dir):
                            os.rmdir(dataset_dir)
                            print(f"✅ Removed empty base directory: {dataset_dir}")
                        elif os.path.exists(dataset_dir):
                            # Directory not empty, try to remove it anyway
                            subprocess.run(['rm', '-rf', dataset_dir], timeout=30)
                            print(f"✅ Removed base directory: {dataset_dir}")
                        removed_dirs.append(dataset_dir)
                    except Exception as e:
                        print(f"⚠️ Failed to remove base directory {dataset_dir}: {e}")
                        failed_dirs.append(dataset_dir)
                        
                except Exception as e:
                    print(f"❌ Failed to process directory {dataset_dir}: {e}")
                    failed_dirs.append(dataset_dir)
        
        # Prepare response message
        message = 'All data has been reset'
        if removed_dirs:
            message += f'. Removed {len(removed_dirs)} dataset directories'
        if failed_dirs:
            message += f'. Warning: {len(failed_dirs)} directories could not be removed'
        
        return jsonify({
            'success': True,
            'message': message,
            'removed_dirs': removed_dirs,
            'failed_dirs': failed_dirs
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-all-data', methods=['POST'])
@login_required
def reset_all_data():
    """Reset all data including demo datasets."""
    try:
        # Delete all dataflows, tasks, and projects
        Dataflow.query.delete()
        Task.query.delete()
        Project.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        # Get the DataLad base path from configuration
        from ...config.config import Config
        datalad_base_path = Config.DATALAD_BASE_PATH
        
        # Also check the default path in case it's different
        default_demo_dir = os.path.expanduser("~/scitrace_demo_datasets")
        
        # Remove all dataset directories
        removed_dirs = []
        failed_dirs = []
        
        for dataset_dir in [datalad_base_path, default_demo_dir]:
            if os.path.exists(dataset_dir):
                try:
                    # First, try to remove individual datasets with DataLad
                    if os.path.isdir(dataset_dir):
                        for item in os.listdir(dataset_dir):
                            item_path = os.path.join(dataset_dir, item)
                            if os.path.isdir(item_path):
                                try:
                                    # Try DataLad remove for individual datasets
                                    result = subprocess.run(
                                        ['datalad', 'remove', '--recursive', item_path], 
                                        capture_output=True, text=True, timeout=30
                                    )
                                    if result.returncode == 0:
                                        print(f"✅ Removed dataset: {item_path}")
                                        removed_dirs.append(item_path)
                                    else:
                                        print(f"⚠️ DataLad remove failed for {item_path}: {result.stderr}")
                                        # Try direct removal
                                        subprocess.run(['rm', '-rf', item_path], timeout=30)
                                        removed_dirs.append(item_path)
                                except Exception as e:
                                    print(f"⚠️ Failed to remove dataset {item_path}: {e}")
                                    # Try direct removal as fallback
                                    try:
                                        subprocess.run(['rm', '-rf', item_path], timeout=30)
                                        removed_dirs.append(item_path)
                                    except Exception as e2:
                                        print(f"❌ Failed to remove {item_path}: {e2}")
                                        failed_dirs.append(item_path)
                    
                    # Remove the base directory if it's empty
                    try:
                        if os.path.exists(dataset_dir) and not os.listdir(dataset_dir):
                            os.rmdir(dataset_dir)
                            print(f"✅ Removed empty base directory: {dataset_dir}")
                        elif os.path.exists(dataset_dir):
                            # Directory not empty, try to remove it anyway
                            subprocess.run(['rm', '-rf', dataset_dir], timeout=30)
                            print(f"✅ Removed base directory: {dataset_dir}")
                        removed_dirs.append(dataset_dir)
                    except Exception as e:
                        print(f"⚠️ Failed to remove base directory {dataset_dir}: {e}")
                        failed_dirs.append(dataset_dir)
                        
                except Exception as e:
                    print(f"❌ Failed to process directory {dataset_dir}: {e}")
                    failed_dirs.append(dataset_dir)
        
        # Prepare response message
        message = 'All data has been reset'
        if removed_dirs:
            message += f'. Removed {len(removed_dirs)} dataset directories'
        if failed_dirs:
            message += f'. Warning: {len(failed_dirs)} directories could not be removed'
        
        return jsonify({
            'success': True,
            'message': message,
            'removed_dirs': removed_dirs,
            'failed_dirs': failed_dirs
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-projects', methods=['POST'])
@login_required
def reset_projects():
    """Reset all projects."""
    try:
        # Delete all projects (this will cascade to dataflows and tasks)
        Project.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All projects have been reset'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-tasks', methods=['POST'])
@login_required
def reset_tasks():
    """Reset all tasks."""
    try:
        # Delete all tasks
        Task.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All tasks have been reset'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reset-dataflows', methods=['POST'])
@login_required
def reset_dataflows():
    """Reset all dataflows."""
    try:
        # Delete all dataflows
        Dataflow.query.delete()
        
        # Commit the deletions
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All dataflows have been reset'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/debug/git-test', methods=['POST'])
@login_required
def debug_git_test():
    """Debug endpoint to test git operations."""
    data = request.get_json()
    test_path = data.get('test_path', os.path.expanduser('~'))
    
    try:
        # Test git status
        result = subprocess.run(['git', 'status'], cwd=test_path, capture_output=True, text=True)
        
        return jsonify({
            'success': True,
            'test_path': test_path,
            'git_status': {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/debug/file-restore-debug', methods=['POST'])
@login_required
def debug_file_restore():
    """Debug endpoint for file restore operations."""
    data = request.get_json()
    dataset_path = data.get('dataset_path')
    file_path = data.get('file_path')
    commit_hash = data.get('commit_hash')
    
    try:
        # Test file restore
        result = subprocess.run(['git', 'show', f'{commit_hash}:{file_path}'], 
                              cwd=dataset_path, capture_output=True, text=True)
        
        return jsonify({
            'success': True,
            'dataset_path': dataset_path,
            'file_path': file_path,
            'commit_hash': commit_hash,
            'file_content': result.stdout,
            'error': result.stderr
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/debug/git-config', methods=['POST'])
@login_required
def debug_git_config():
    """Debug endpoint to check git configuration."""
    data = request.get_json()
    dataset_path = data.get('dataset_path', os.path.expanduser('~'))
    
    try:
        # Check git config
        result = subprocess.run(['git', 'config', '--list'], 
                              cwd=dataset_path, capture_output=True, text=True)
        
        return jsonify({
            'success': True,
            'dataset_path': dataset_path,
            'git_config': result.stdout,
            'error': result.stderr
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
