"""
Git operations services for SciTrace

Handles Git operations within DataLad datasets.
"""

import os
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from ..exceptions import GitOperationError, DatasetError, ValidationError
from .base_service import BaseService


class GitOperationsService(BaseService):
    """Service for Git operations within DataLad datasets."""
    
    def __init__(self, db=None):
        super().__init__(db)
    
    def get_commit_history(self, dataset_path: str, file_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get git commit history for a dataset or specific file.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Optional specific file path
            limit: Maximum number of commits to return
        
        Returns:
            List of commit information dictionaries
        
        Raises:
            GitOperationError: If git operation fails
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to get commit history: {e.stderr}", command=cmd)
    
    def get_detailed_git_log(self, dataset_path: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get detailed git log information for comprehensive visualization.
        
        Args:
            dataset_path: Path to the dataset
            limit: Maximum number of commits to return
        
        Returns:
            List of detailed commit information
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to get detailed git log: {e.stderr}", command=cmd)
    
    def get_file_commit_history(self, dataset_path: str, file_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get commit history specifically for a file.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file
            limit: Maximum number of commits to return
        
        Returns:
            List of commit information for the file
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            
            return commits
            
        except Exception as e:
            # If file doesn't exist in git history, return empty list
            if "does not exist" in str(e) or "fatal: bad revision" in str(e):
                return []
            raise GitOperationError(f"Failed to get file commit history: {str(e)}", command=cmd)
    
    def restore_file_to_commit(self, dataset_path: str, file_path: str, commit_hash: str, commit_message: str = None) -> dict:
        """
        Restore a file to a specific commit using git checkout and DataLad save.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file to restore
            commit_hash: Commit hash to restore from
            commit_message: Optional commit message
        
        Returns:
            Dict containing restoration result
        
        Raises:
            GitOperationError: If git operation fails
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # First check if the file exists in the specified commit
            if not self.check_file_exists_in_commit(dataset_path, file_path, commit_hash):
                raise GitOperationError(f"File {file_path} does not exist in commit {commit_hash}")
            
            # Use git checkout to restore the file from the specific commit
            print(f"Attempting to restore {file_path} from commit {commit_hash}")
            result = subprocess.run(
                ['git', 'checkout', commit_hash, '--', file_path], 
                cwd=dataset_path, capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout if result.stdout else "Unknown error"
                raise GitOperationError(f"Failed to restore file {file_path} from commit {commit_hash}: {error_msg}")
            
            # Verify the file was actually restored
            restored_file_path = os.path.join(dataset_path, file_path)
            if not os.path.exists(restored_file_path):
                raise GitOperationError(f"File {file_path} was not restored to {restored_file_path}")
            
            # Add the restored file to git
            print(f"Adding {file_path} to git")
            add_result = subprocess.run(['git', 'add', file_path], cwd=dataset_path, capture_output=True, text=True, check=False)
            if add_result.returncode != 0:
                print(f"Warning: git add failed: {add_result.stderr}")
            
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
            
            # If this is a DataLad dataset, also save to DataLad
            if os.path.exists(os.path.join(dataset_path, '.datalad')):
                print(f"Saving to DataLad with message: {commit_msg}")
                try:
                    datalad_result = subprocess.run(['datalad', 'save', '-m', commit_msg], cwd=dataset_path, capture_output=True, text=True, check=False)
                    if datalad_result.returncode != 0:
                        print(f"Warning: datalad save failed: {datalad_result.stderr}")
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
            raise GitOperationError(f"Failed to restore file: {error_msg}")
    
    def check_file_exists_in_commit(self, dataset_path: str, file_path: str, commit_hash: str) -> bool:
        """
        Check if a file exists in a specific commit.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file
            commit_hash: Commit hash to check
        
        Returns:
            True if file exists in commit, False otherwise
        """
        if not os.path.exists(dataset_path):
            return False
        
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'], 
                cwd=dataset_path, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_file_diff(self, dataset_path: str, commit_hash: str, file_path: str) -> str:
        """
        Get the diff for a specific file in a commit.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash
            file_path: Path to the file
        
        Returns:
            Diff content as string
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get the diff for the file
            cmd = ['git', 'show', commit_hash, '--', file_path]
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Failed to get file diff: {e.stderr}", command=cmd)
    
    def get_commit_files(self, dataset_path: str, commit_hash: str) -> List[Dict[str, Any]]:
        """
        Get files changed in a specific commit.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash
        
        Returns:
            List of file change information
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to get commit files: {e.stderr}", command=cmd)
    
    def get_file_content_at_commit(self, dataset_path: str, commit_hash: str, file_path: str) -> str:
        """
        Get file content at a specific commit.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash
            file_path: Path to the file
        
        Returns:
            File content as string
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get file content at the specific commit
            cmd = ['git', 'show', f'{commit_hash}:{file_path}']
            result = subprocess.run(cmd, cwd=dataset_path, capture_output=True, text=True, check=True)
            
            return result.stdout
            
        except subprocess.CalledProcessError as e:
            raise GitOperationError(f"Failed to get file content: {e.stderr}", command=cmd)
    
    def revert_commit(self, dataset_path: str, commit_hash: str, commit_message: str = None) -> dict:
        """
        Revert a specific commit.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash to revert
            commit_message: Optional commit message
        
        Returns:
            Dict containing revert result
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to revert commit: {e.stderr}", command=cmd)
    
    def create_branch_from_commit(self, dataset_path: str, commit_hash: str, branch_name: str) -> dict:
        """
        Create a new branch from a specific commit.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash to branch from
            branch_name: Name of the new branch
        
        Returns:
            Dict containing branch creation result
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to create branch: {e.stderr}", command=cmd)
    
    def checkout_commit(self, dataset_path: str, commit_hash: str) -> dict:
        """
        Checkout a specific commit (detached HEAD state).
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash to checkout
        
        Returns:
            Dict containing checkout result
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
            raise GitOperationError(f"Failed to checkout commit: {e.stderr}", command=cmd)
    
    def get_current_branch(self, dataset_path: str) -> str:
        """
        Get the current branch name.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Current branch name or commit hash if in detached HEAD
        
        Raises:
            GitOperationError: If git operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
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
    
    def _get_full_hash(self, dataset_path: str, short_hash: str) -> str:
        """Get full commit hash from short hash."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', short_hash], 
                cwd=dataset_path, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return short_hash
    
    def _get_relative_date(self, date_obj: datetime) -> str:
        """Get relative date string (e.g., '2 hours ago', 'yesterday')."""
        try:
            now = datetime.now(timezone.utc)
            # Make date_obj timezone-aware if it isn't already
            if date_obj.tzinfo is None:
                date_obj = date_obj.replace(tzinfo=timezone.utc)
            
            diff = now - date_obj
            
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
                
        except Exception as e:
            # If date parsing fails, return the original date string
            return str(date_obj)
    
    def debug_file_restore(self, dataset_path: str, file_path: str, commit_hash: str) -> Dict[str, Any]:
        """
        Debug method to troubleshoot file restoration issues.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file
            commit_hash: Commit hash to restore from
        
        Returns:
            Debug information dictionary
        """
        debug_info = {
            'dataset_path': dataset_path,
            'file_path': file_path,
            'commit_hash': commit_hash,
            'dataset_exists': os.path.exists(dataset_path),
            'file_exists_in_commit': False,
            'file_exists_currently': False,
            'commit_exists': False,
            'errors': []
        }
        
        try:
            # Check if dataset exists
            if not os.path.exists(dataset_path):
                debug_info['errors'].append(f"Dataset path does not exist: {dataset_path}")
                return debug_info
            
            # Check if commit exists
            try:
                subprocess.run(['git', 'cat-file', '-e', commit_hash], 
                             cwd=dataset_path, capture_output=True, check=True)
                debug_info['commit_exists'] = True
            except subprocess.CalledProcessError:
                debug_info['errors'].append(f"Commit {commit_hash} does not exist")
            
            # Check if file exists in commit
            try:
                subprocess.run(['git', 'cat-file', '-e', f"{commit_hash}:{file_path}"], 
                             cwd=dataset_path, capture_output=True, check=True)
                debug_info['file_exists_in_commit'] = True
            except subprocess.CalledProcessError:
                debug_info['errors'].append(f"File {file_path} does not exist in commit {commit_hash}")
            
            # Check if file exists currently
            current_file_path = os.path.join(dataset_path, file_path)
            debug_info['file_exists_currently'] = os.path.exists(current_file_path)
            
        except Exception as e:
            debug_info['errors'].append(f"Debug error: {str(e)}")
        
        return debug_info
    
    def check_git_config(self, dataset_path: str) -> Dict[str, Any]:
        """
        Check git configuration for a dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Git configuration information
        """
        config_info = {
            'dataset_path': dataset_path,
            'is_git_repo': False,
            'git_config': {},
            'errors': []
        }
        
        try:
            if not os.path.exists(dataset_path):
                config_info['errors'].append(f"Dataset path does not exist: {dataset_path}")
                return config_info
            
            # Check if it's a git repository
            git_dir = os.path.join(dataset_path, '.git')
            if os.path.exists(git_dir):
                config_info['is_git_repo'] = True
                
                # Get git config
                try:
                    result = subprocess.run(['git', 'config', '--list'], 
                                          cwd=dataset_path, capture_output=True, text=True, check=True)
                    config_lines = result.stdout.strip().split('\n')
                    for line in config_lines:
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config_info['git_config'][key] = value
                except subprocess.CalledProcessError as e:
                    config_info['errors'].append(f"Failed to get git config: {e.stderr}")
            else:
                config_info['errors'].append("Not a git repository")
                
        except Exception as e:
            config_info['errors'].append(f"Config check error: {str(e)}")
        
        return config_info
    
    def compare_commit_to_local(self, dataset_path: str, commit_hash: str) -> Dict[str, Any]:
        """
        Compare a commit to the current local state.
        
        Args:
            dataset_path: Path to the dataset
            commit_hash: Commit hash to compare
        
        Returns:
            Comparison information dictionary
        """
        comparison_info = {
            'commit_hash': commit_hash,
            'dataset_path': dataset_path,
            'is_same': False,
            'differences': [],
            'errors': []
        }
        
        try:
            if not os.path.exists(dataset_path):
                comparison_info['errors'].append(f"Dataset path does not exist: {dataset_path}")
                return comparison_info
            
            # Check if commit exists
            try:
                subprocess.run(['git', 'cat-file', '-e', commit_hash], 
                             cwd=dataset_path, capture_output=True, check=True)
            except subprocess.CalledProcessError:
                comparison_info['errors'].append(f"Commit {commit_hash} does not exist")
                return comparison_info
            
            # Get current HEAD commit
            try:
                result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                      cwd=dataset_path, capture_output=True, text=True, check=True)
                current_head = result.stdout.strip()
                comparison_info['current_head'] = current_head
                comparison_info['is_same'] = (current_head == commit_hash)
            except subprocess.CalledProcessError as e:
                comparison_info['errors'].append(f"Failed to get current HEAD: {e.stderr}")
                return comparison_info
            
            # If not the same, get differences
            if not comparison_info['is_same']:
                try:
                    # Get file differences
                    result = subprocess.run(['git', 'diff', '--name-status', commit_hash, 'HEAD'], 
                                          cwd=dataset_path, capture_output=True, text=True, check=True)
                    if result.stdout.strip():
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                parts = line.split('\t', 1)
                                if len(parts) == 2:
                                    status = parts[0]
                                    file_path = parts[1]
                                    comparison_info['differences'].append({
                                        'status': status,
                                        'file_path': file_path
                                    })
                except subprocess.CalledProcessError as e:
                    comparison_info['errors'].append(f"Failed to get differences: {e.stderr}")
            
        except Exception as e:
            comparison_info['errors'].append(f"Comparison error: {str(e)}")
        
        return comparison_info
