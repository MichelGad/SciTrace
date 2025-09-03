"""
Project Services for SciTrace

Handles project management operations and DataLad integration.
"""

import os
import subprocess
import uuid
from datetime import datetime, timezone
from .datalad_services import DataLadService


class ProjectService:
    """Service for project management operations."""
    
    def __init__(self):
        self.datalad_service = DataLadService()
    
    def create_project(self, name, description, admin_id, collaborators=None):
        """Create a new project in the database (without DataLad dataset)."""
        if collaborators is None:
            collaborators = []
        
        # Generate unique project ID
        project_id = self._generate_project_id()
        
        return {
            'project_id': project_id,
            'name': name,
            'description': description,
            'admin_id': admin_id,
            'collaborators': collaborators,
            'dataset_path': None,  # No dataset created yet
            'status': 'ongoing'
        }
    
    def _generate_project_id(self):
        """Generate a unique project ID."""
        return str(uuid.uuid4())[:8].upper()
    
    def get_project_info(self, project_id):
        """Get detailed information about a project."""
        # This would typically query the database
        # For now, return basic structure
        return {
            'project_id': project_id,
            'status': 'ongoing'
        }
    
    def get_project_dashboard_data(self, user_id):
        """Get dashboard data for a user's projects."""
        from .models import Project, Task, Dataflow
        
        # Get user's projects
        projects = Project.query.filter_by(admin_id=user_id).all()
        
        # Get tasks for these projects
        project_ids = [p.id for p in projects]
        tasks = Task.query.filter(Task.project_id.in_(project_ids)).all() if project_ids else []
        
        # Get dataflows for these projects
        dataflows = Dataflow.query.filter(Dataflow.project_id.in_(project_ids)).all() if project_ids else []
        
        # Calculate statistics
        total_projects = len(projects)
        ongoing_projects = len([p for p in projects if p.status == 'ongoing'])
        completed_projects = len([p for p in projects if p.status == 'completed'])
        
        total_tasks = len(tasks)
        pending_tasks = len([t for t in tasks if t.status == 'pending'])
        ongoing_tasks = len([t for t in tasks if t.status == 'ongoing'])
        completed_tasks = len([t for t in tasks if t.status == 'done'])
        urgent_tasks = len([t for t in tasks if t.priority == 'urgent'])
        
        total_dataflows = len(dataflows)
        
        return {
            'projects': projects,
            'tasks': tasks,
            'dataflows': dataflows,
            'stats': {
                'total_projects': total_projects,
                'ongoing_projects': ongoing_projects,
                'completed_projects': completed_projects,
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'ongoing_tasks': ongoing_tasks,
                'completed_tasks': completed_tasks,
                'urgent_tasks': urgent_tasks,
                'total_dataflows': total_dataflows
            }
        }

    def get_commit_history(self, dataset_path, file_path=None, limit=10):
        """Get git commit history for a dataset or specific file."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            if file_path:
                # Get commit history for a specific file
                cmd = ['git', 'log', '--oneline', '--follow', '--', file_path]
            else:
                # Get general commit history
                cmd = ['git', 'log', '--oneline', '-n', str(limit)]
            
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        commit_hash = parts[0]
                        message = parts[1]
                        commits.append({
                            'hash': commit_hash,
                            'message': message,
                            'full_hash': self._get_full_hash(dataset_path, commit_hash)
                        })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get commit history: {e.stderr}")
    
    def _get_full_hash(self, dataset_path, short_hash):
        """Get full commit hash from short hash."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', short_hash], 
                cwd=dataset_path, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return short_hash
    
    def restore_file_to_commit(self, dataset_path, file_path, commit_hash, commit_message=None):
        """Restore a file to a specific commit using git checkout and DataLad save."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # First check if the file exists in the specified commit
            if not self.check_file_exists_in_commit(dataset_path, file_path, commit_hash):
                raise Exception(f"File {file_path} does not exist in commit {commit_hash}")
            
            # Use git checkout to restore the file from the specific commit
            # This handles DataLad annex files properly
            print(f"Attempting to restore {file_path} from commit {commit_hash}")
            result = subprocess.run(
                ['git', 'checkout', commit_hash, '--', file_path], 
                cwd=dataset_path, capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout if result.stdout else "Unknown error"
                raise Exception(f"Failed to restore file {file_path} from commit {commit_hash}: {error_msg}")
            
            # Verify the file was actually restored
            restored_file_path = os.path.join(dataset_path, file_path)
            if not os.path.exists(restored_file_path):
                raise Exception(f"File {file_path} was not restored to {restored_file_path}")
            
            # Check if the file was actually modified by the checkout
            # Get the file content from the commit to compare
            try:
                commit_content = subprocess.run(
                    ['git', 'show', f'{commit_hash}:{file_path}'], 
                    cwd=dataset_path, capture_output=True, text=True, check=True
                ).stdout
                
                # Read the current file content
                with open(restored_file_path, 'r') as f:
                    current_content = f.read()
                
                if commit_content == current_content:
                    print(f"File {file_path} is already identical to commit {commit_hash}")
                else:
                    print(f"File {file_path} was modified by checkout")
                    
            except Exception as e:
                print(f"Warning: Could not compare file content: {e}")
                # Continue anyway
            
            # Add the restored file to git
            print(f"Adding {file_path} to git")
            add_result = subprocess.run(['git', 'add', file_path], cwd=dataset_path, capture_output=True, text=True, check=False)
            if add_result.returncode != 0:
                print(f"Warning: git add failed: {add_result.stderr}")
                # Continue anyway as the file might already be staged
            
            # Check git status before commit
            status_result = subprocess.run(['git', 'status', '--porcelain'], cwd=dataset_path, capture_output=True, text=True, check=False)
            print(f"Git status before commit: {status_result.stdout}")
            
            # Commit the restoration
            commit_msg = commit_message or f"Restore {file_path} from commit {commit_hash}"
            print(f"Committing restoration with message: {commit_msg}")
            
            # Check if there are any staged changes
            if not status_result.stdout.strip():
                print("No staged changes to commit, skipping commit step")
            else:
                commit_result = subprocess.run(['git', 'commit', '-m', commit_msg], cwd=dataset_path, capture_output=True, text=True, check=False)
                if commit_result.returncode != 0:
                    print(f"Warning: git commit failed: {commit_result.stderr}")
                    print(f"Git commit stdout: {commit_result.stdout}")
                    # Continue anyway as the file is restored
            
            # If this is a DataLad dataset, also save to DataLad
            if os.path.exists(os.path.join(dataset_path, '.datalad')):
                print(f"Saving to DataLad with message: {commit_msg}")
                try:
                    datalad_result = subprocess.run(['datalad', 'save', '-m', commit_msg], cwd=dataset_path, capture_output=True, text=True, check=False)
                    if datalad_result.returncode != 0:
                        print(f"Warning: datalad save failed: {datalad_result.stderr}")
                        print(f"DataLad save stdout: {datalad_result.stdout}")
                except Exception as e:
                    print(f"Warning: datalad save failed with exception: {e}")
            
            return {
                'success': True,
                'message': f'File {file_path} restored from commit {commit_hash}',
                'commit_hash': commit_hash,
                'file_path': file_path
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
            raise Exception(f"Failed to restore file: {error_msg}")
    
    def get_file_commit_history(self, dataset_path, file_path, limit=10):
        """Get commit history specifically for a file."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get commit history for the specific file
            cmd = ['git', 'log', '--oneline', '--follow', '-n', str(limit), '--', file_path]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=False)
            
            commits = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split(' ', 1)
                        if len(parts) == 2:
                            commit_hash = parts[0]
                            message = parts[1]
                            commits.append({
                                'hash': commit_hash,
                                'message': message,
                                'full_hash': self._get_full_hash(dataset_path, commit_hash)
                            })
            
            # If no commits found, try without --follow flag
            if not commits:
                cmd_no_follow = ['git', 'log', '--oneline', '-n', str(limit), '--', file_path]
                result_no_follow = subprocess.run(cmd_no_follow, cwd=dataset_path, capture_output=True, text=True, check=False)
                
                if result_no_follow.returncode == 0 and result_no_follow.stdout.strip():
                    for line in result_no_follow.stdout.strip().split('\n'):
                        if line.strip():
                            parts = line.split(' ', 1)
                            if len(parts) == 2:
                                commit_hash = parts[0]
                                message = parts[1]
                                commits.append({
                                    'hash': commit_hash,
                                    'message': message,
                                    'full_hash': self._get_full_hash(dataset_path, commit_hash)
                                })
            
            # If still no commits found, try getting general commit history
            if not commits:
                try:
                    general_commits = self.get_commit_history(dataset_path, limit=limit)
                    # Filter commits that might contain this file
                    for commit in general_commits:
                        if self.check_file_exists_in_commit(dataset_path, file_path, commit['hash']):
                            commits.append(commit)
                except Exception as e:
                    pass  # Silently ignore if general history fails
            
            return commits
            
        except Exception as e:
            # If file doesn't exist in git history, return empty list
            if "does not exist" in str(e) or "fatal: bad revision" in str(e):
                return []
            raise Exception(f"Failed to get file commit history: {str(e)}")
    
    def check_file_exists_in_commit(self, dataset_path, file_path, commit_hash):
        """Check if a file exists in a specific commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'], 
                cwd=dataset_path, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_file_restore_info(self, dataset_path, file_path):
        """Get information needed to restore a file, including commit history."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Check if this is a DataLad dataset
            is_datalad = os.path.exists(os.path.join(dataset_path, '.datalad'))
            
            # Get commit history for the file
            commit_history = self.get_file_commit_history(dataset_path, file_path, limit=20)
            
            if not commit_history:
                return {
                    'file_path': file_path,
                    'can_restore': False,
                    'error': 'No commit history found for this file. It may not have been committed to version control.',
                    'is_datalad': is_datalad,
                    'suggestions': [
                        'Check if the file was ever committed to the repository',
                        'Verify the file path is correct',
                        'Try using the full path from the dataset root'
                    ]
                }
            
            # Get current file status
            current_status = 'exists'
            if not os.path.exists(os.path.join(dataset_path, file_path)):
                current_status = 'deleted'
            
            return {
                'file_path': file_path,
                'can_restore': True,
                'current_status': current_status,
                'is_datalad': is_datalad,
                'commit_history': commit_history,
                'latest_commit': commit_history[0] if commit_history else None,
                'total_commits': len(commit_history)
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'can_restore': False,
                'error': str(e),
                'is_datalad': False
            }
    
    def restore_file_from_latest_commit(self, dataset_path, file_path, commit_message=None):
        """Restore a file from its most recent commit."""
        file_info = self.get_file_restore_info(dataset_path, file_path)
        
        if not file_info['can_restore']:
            raise Exception(file_info['error'])
        
        if not file_info['commit_history']:
            raise Exception("No commit history available for restoration")
        
        # Use the latest commit
        latest_commit = file_info['commit_history'][0]
        return self.restore_file_to_commit(dataset_path, file_path, latest_commit['hash'], commit_message)
    
    def get_dataset_restore_summary(self, dataset_path):
        """Get a summary of all files that can be restored in a dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get all tracked files from git
            result = subprocess.run(
                ['git', 'ls-files'], 
                cwd=dataset_path, capture_output=True, text=True, check=True
            )
            
            tracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get deleted files from git status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'], 
                cwd=dataset_path, capture_output=True, text=True, check=True
            )
            
            deleted_files = []
            for line in status_result.stdout.strip().split('\n'):
                if line.strip().startswith('D '):
                    file_path = line[3:].strip()
                    deleted_files.append(file_path)
            
            restore_summary = {
                'dataset_path': dataset_path,
                'total_tracked_files': len(tracked_files),
                'deleted_files': deleted_files,
                'can_restore_count': len(deleted_files),
                'is_datalad': os.path.exists(os.path.join(dataset_path, '.datalad'))
            }
            
            return restore_summary
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get dataset restore summary: {e.stderr}")
    
    def debug_file_restore(self, dataset_path, file_path, commit_hash):
        """Debug method to get detailed information about file restoration."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            debug_info = {
                'dataset_path': dataset_path,
                'file_path': file_path,
                'commit_hash': commit_hash,
                'file_exists_in_commit': self.check_file_exists_in_commit(dataset_path, file_path, commit_hash),
                'current_file_exists': os.path.exists(os.path.join(dataset_path, file_path)),
                'is_datalad': os.path.exists(os.path.join(dataset_path, '.datalad'))
            }
            
            # Get git status
            try:
                git_status = subprocess.run(
                    ['git', 'status', '--porcelain'], 
                    cwd=dataset_path, capture_output=True, text=True, check=False
                )
                debug_info['git_status'] = git_status.stdout if git_status.stdout else "No output"
                debug_info['git_status_returncode'] = git_status.returncode
            except Exception as e:
                debug_info['git_status_error'] = str(e)
            
            # Get DataLad status if applicable
            if debug_info['is_datalad']:
                try:
                    datalad_status = subprocess.run(
                        ['datalad', 'status'], 
                        cwd=dataset_path, capture_output=True, text=True, check=False
                    )
                    debug_info['datalad_status'] = datalad_status.stdout if datalad_status.stdout else "No output"
                    debug_info['datalad_status_returncode'] = datalad_status.returncode
                except Exception as e:
                    debug_info['datalad_status_error'] = str(e)
            
            return debug_info
            
        except Exception as e:
            return {
                'error': str(e),
                'dataset_path': dataset_path,
                'file_path': file_path,
                'commit_hash': commit_hash
            }
    
    def check_git_config(self, dataset_path):
        """Check git configuration for potential issues."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            config_info = {}
            
            # Check user name and email
            try:
                user_name = subprocess.run(
                    ['git', 'config', 'user.name'], 
                    cwd=dataset_path, capture_output=True, text=True, check=False
                )
                config_info['user_name'] = user_name.stdout.strip() if user_name.stdout else None
                config_info['user_name_error'] = user_name.stderr if user_name.stderr else None
            except Exception as e:
                config_info['user_name_error'] = str(e)
            
            try:
                user_email = subprocess.run(
                    ['git', 'config', 'user.email'], 
                    cwd=dataset_path, capture_output=True, text=True, check=False
                )
                config_info['user_email'] = user_email.stdout.strip() if user_email.stdout else None
                config_info['user_email_error'] = user_email.stderr if user_email.stderr else None
            except Exception as e:
                config_info['user_email_error'] = str(e)
            
            # Check if this is a git repository
            try:
                git_dir = subprocess.run(
                    ['git', 'rev-parse', '--git-dir'], 
                    cwd=dataset_path, capture_output=True, text=True, check=False
                )
                config_info['git_dir'] = git_dir.stdout.strip() if git_dir.stdout else None
                config_info['is_git_repo'] = git_dir.returncode == 0
            except Exception as e:
                config_info['git_dir_error'] = str(e)
                config_info['is_git_repo'] = False
            
            return config_info
            
        except Exception as e:
            return {
                'error': str(e),
                'dataset_path': dataset_path
            }

    def get_detailed_git_log(self, dataset_path, limit=50):
        """Get detailed git log information for comprehensive visualization."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get detailed git log with author, date, and commit info
            cmd = [
                'git', 'log', 
                '--pretty=format:%H|%h|%an|%ae|%ad|%s|%b',
                '--date=iso',
                '-n', str(limit)
            ]
            
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Split by | delimiter
                    parts = line.split('|')
                    if len(parts) >= 6:
                        full_hash = parts[0]
                        short_hash = parts[1]
                        author_name = parts[2]
                        author_email = parts[3]
                        date = parts[4]
                        message = parts[5]
                        body = parts[6] if len(parts) > 6 else ""
                        
                        # Parse date
                        try:
                            from datetime import datetime
                            parsed_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                            formatted_date = parsed_date.strftime('%d. %b %Y at %H:%M')
                            relative_date = self._get_relative_date(parsed_date)
                        except:
                            formatted_date = date
                            relative_date = "Unknown"
                        
                        commits.append({
                            'full_hash': full_hash,
                            'short_hash': short_hash,
                            'author_name': author_name,
                            'author_email': author_email,
                            'date': date,
                            'formatted_date': formatted_date,
                            'relative_date': relative_date,
                            'message': message,
                            'body': body
                        })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get detailed git log: {e.stderr}")
    
    def _get_relative_date(self, date):
        """Get relative date string (e.g., '2 hours ago', 'yesterday')."""
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        diff = now - date.replace(tzinfo=timezone.utc)
        
        if diff.days == 0:
            if diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        elif diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = diff.days // 365
            return f"{years} year{'s' if years != 1 else ''} ago"

    def get_file_diff(self, dataset_path, commit_hash, file_path):
        """Get the diff for a specific file in a commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get the diff for the file
            cmd = ['git', 'show', commit_hash, '--', file_path]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get file diff: {e.stderr}")
    
    def get_commit_files(self, dataset_path, commit_hash):
        """Get files changed in a specific commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get files changed in the commit
            cmd = ['git', 'show', '--name-status', '--pretty=format:', commit_hash]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) == 2:
                        status = parts[0]
                        file_path = parts[1]
                        
                        # Determine change type
                        if status == 'A':
                            change_type = 'Added'
                        elif status == 'M':
                            change_type = 'Modified'
                        elif status == 'D':
                            change_type = 'Deleted'
                        elif status == 'R':
                            change_type = 'Renamed'
                        else:
                            change_type = status
                        
                        # Get file size if file exists
                        file_size = None
                        if status != 'D':  # Not deleted
                            full_path = os.path.join(dataset_path, file_path)
                            if os.path.exists(full_path):
                                file_size = os.path.getsize(full_path)
                        
                        files.append({
                            'path': file_path,
                            'status': status,
                            'change_type': change_type,
                            'size': file_size
                        })
            
            return files
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get commit files: {e.stderr}")
    
    def get_file_content_at_commit(self, dataset_path, commit_hash, file_path):
        """Get file content at a specific commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get file content at the specific commit
            cmd = ['git', 'show', f'{commit_hash}:{file_path}']
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get file content: {e.stderr}")
    
    def revert_commit(self, dataset_path, commit_hash, commit_message=None):
        """Revert a specific commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Create revert commit
            cmd = ['git', 'revert', '--no-edit', commit_hash]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            # If custom message provided, amend the revert commit
            if commit_message:
                subprocess.run(['git', 'commit', '--amend', '-m', commit_message], 
                             cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'message': f'Successfully reverted commit {commit_hash}',
                'output': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to revert commit: {e.stderr}")
    
    def create_branch_from_commit(self, dataset_path, commit_hash, branch_name):
        """Create a new branch from a specific commit."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Create and checkout new branch
            cmd = ['git', 'checkout', '-b', branch_name, commit_hash]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'message': f'Successfully created branch {branch_name} from commit {commit_hash}',
                'output': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create branch: {e.stderr}")
    
    def checkout_commit(self, dataset_path, commit_hash):
        """Checkout a specific commit (detached HEAD state)."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Checkout the commit
            cmd = ['git', 'checkout', commit_hash]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'message': f'Successfully checked out commit {commit_hash}',
                'output': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to checkout commit: {e.stderr}")
    
    def compare_commit_to_local(self, dataset_path, commit_hash):
        """Compare a commit to the current local state."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get diff between commit and current state
            cmd = ['git', 'diff', commit_hash, 'HEAD']
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return {
                'success': True,
                'diff': result.stdout,
                'has_changes': bool(result.stdout.strip())
            }
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to compare commit: {e.stderr}")
    
    def get_current_branch(self, dataset_path):
        """Get the current branch name."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            cmd = ['git', 'branch', '--show-current']
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # If no branch (detached HEAD), return the commit hash
            try:
                cmd = ['git', 'rev-parse', 'HEAD']
                result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
                return f"HEAD ({result.stdout.strip()[:8]})"
            except subprocess.CalledProcessError:
                return "Unknown"
