"""
File operations services for SciTrace

Handles file operations within DataLad datasets.
"""

import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..utils.datalad_utils import DataLadUtils, DataLadCommandError
from ..utils.file_utils import FileUtils
from ..exceptions import FileOperationError, DatasetError, ValidationError
from .base_service import BaseService


class FileOperationsService(BaseService):
    """Service for file operations within DataLad datasets."""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.datalad_utils = DataLadUtils()
        self.file_utils = FileUtils()
    
    def add_file_to_dataset(self, dataset_path: str, file_path: str, commit_message: str = None) -> dict:
        """
        Add a file to a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file to add (relative to dataset)
            commit_message: Optional commit message
        
        Returns:
            Dict containing operation result information
        
        Raises:
            FileOperationError: If file operation fails
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        # Handle relative paths - construct absolute path within dataset
        if not os.path.isabs(file_path):
            full_file_path = os.path.join(dataset_path, file_path)
        else:
            full_file_path = file_path
        
        if not os.path.exists(full_file_path):
            raise FileOperationError(f"File does not exist: {file_path}", file_path=file_path)
        
        try:
            # If file is already in dataset (relative path), use it directly
            if not os.path.isabs(file_path):
                # File is already in dataset, add it to DataLad
                result = self.datalad_utils.add_file(dataset_path, file_path, commit_message)
                
                return {
                    'file_path': full_file_path,
                    'status': 'added',
                    'message': f'File {file_path} added to dataset',
                    'datalad_result': result
                }
            else:
                # File is outside dataset, copy it first
                filename = os.path.basename(file_path)
                dest_path = os.path.join(dataset_path, filename)
                
                self.file_utils.copy_file(file_path, dest_path, overwrite=True)
                
                # Add to DataLad
                result = self.datalad_utils.add_file(dataset_path, filename, commit_message)
                
                return {
                    'file_path': dest_path,
                    'status': 'added',
                    'message': f'File {filename} added to dataset',
                    'datalad_result': result
                }
            
        except DataLadCommandError as e:
            raise FileOperationError(f"DataLad operation failed: {e.message}", file_path=file_path)
        except Exception as e:
            raise FileOperationError(f"Failed to add file to dataset: {str(e)}", file_path=file_path)
    
    def create_directory_in_dataset(self, dataset_path: str, dir_name: str, commit_message: str = None) -> dict:
        """
        Create a directory in a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
            dir_name: Name of the directory to create
            commit_message: Optional commit message
        
        Returns:
            Dict containing operation result information
        
        Raises:
            FileOperationError: If directory creation fails
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            dir_path = os.path.join(dataset_path, dir_name)
            self.file_utils.create_directory(dir_path)
            
            # Add to DataLad
            commit_msg = commit_message or f'Add directory: {dir_name}'
            result = self.datalad_utils.save_changes(dataset_path, commit_msg, [dir_name])
            
            return {
                'dir_path': dir_path,
                'status': 'created',
                'message': f'Directory {dir_name} created in dataset',
                'datalad_result': result
            }
            
        except Exception as e:
            raise FileOperationError(f"Failed to create directory in dataset: {str(e)}", file_path=dir_name)
    
    def get_stage_files(self, dataset_path: str, stage_name: str) -> Optional[Dict[str, Any]]:
        """
        Get actual files and metadata for a specific stage in the dataset.
        
        Args:
            dataset_path: Path to the dataset
            stage_name: Name of the stage/directory
        
        Returns:
            Dict containing stage file information or None if not found
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            return None
        
        # Handle dataset root case
        if stage_name == '.':
            stage_path = dataset_path
            display_name = 'Dataset Root'
        else:
            stage_path = os.path.join(dataset_path, stage_name)
            display_name = stage_name.replace('_', ' ').title()
        
        if not os.path.exists(stage_path):
            return {
                'stage_name': display_name,
                'stage_dir': stage_name,  # Add actual directory name for file path construction
                'path': stage_path,
                'files': [],
                'metadata': {
                    'file_count': 0,
                    'total_size': '0 B',
                    'last_modified': None,
                    'stage_type': display_name,
                    'datalad_status': 'unknown'
                }
            }
        
        try:
            files = []
            deleted_files = []
            total_size = 0
            tracked_files = 0
            untracked_files = 0
            
            # Get DataLad status for the stage directory
            datalad_status = self._get_datalad_status(dataset_path, stage_name)
            
            # Get deleted files from DataLad status
            deleted_files = self._get_deleted_files(dataset_path, stage_name)
            
            # Get all files in the stage directory
            if stage_name == '.':
                # Only get files directly in the root directory
                for filename in os.listdir(stage_path):
                    file_path = os.path.join(stage_path, filename)
                    if os.path.isfile(file_path) and filename != '.DS_Store':
                        file_info = self._get_file_info(file_path, filename, dataset_path, stage_name)
                        files.append(file_info)
                        total_size += file_info['size_bytes']
                        if file_info['tracked']:
                            tracked_files += 1
                        else:
                            untracked_files += 1
            else:
                # For other stages, walk through all subdirectories
                for root, dirs, filenames in os.walk(stage_path):
                    for filename in filenames:
                        if filename == '.DS_Store':
                            continue
                            
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, stage_path)
                        
                        file_info = self._get_file_info(file_path, rel_path, dataset_path, stage_name)
                        files.append(file_info)
                        total_size += file_info['size_bytes']
                        if file_info['tracked']:
                            tracked_files += 1
                        else:
                            untracked_files += 1
            
            # Sort files by size (largest first)
            files.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Get stage metadata
            stage_stat = os.stat(stage_path)
            metadata = {
                'file_count': len(files),
                'tracked_files': tracked_files,
                'untracked_files': untracked_files,
                'deleted_files': len(deleted_files),
                'total_size': self.file_utils.format_file_size(total_size),
                'last_modified': datetime.fromtimestamp(stage_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                'stage_type': display_name,
                'path': stage_path,
                'datalad_status': 'mixed' if untracked_files > 0 else 'clean' if tracked_files > 0 else 'empty'
            }
            
            return {
                'stage_name': display_name,
                'stage_dir': stage_name,  # Add actual directory name for file path construction
                'path': stage_path,
                'files': files,
                'deleted_files': deleted_files,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'stage_name': display_name,
                'stage_dir': stage_name,  # Add actual directory name for file path construction
                'path': stage_path,
                'error': str(e),
                'files': [],
                'metadata': {}
            }
    
    def _get_file_info(self, file_path: str, rel_path: str, dataset_path: str, stage_name: str) -> Dict[str, Any]:
        """Get information about a single file."""
        stat = os.stat(file_path)
        file_size = stat.st_size
        
        # Determine file type
        file_ext = os.path.splitext(os.path.basename(file_path))[1].lower()
        file_type = self.file_utils.get_file_type(file_path)
        
        # Check if file is tracked by DataLad
        git_path = rel_path if stage_name == '.' else os.path.join(stage_name, rel_path)
        is_tracked = self._check_file_in_git(dataset_path, git_path)
        
        return {
            'name': os.path.basename(file_path),
            'path': rel_path,
            'size': self.file_utils.format_file_size(file_size),
            'type': file_type,
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'size_bytes': file_size,
            'tracked': is_tracked,
            'status': 'Tracked' if is_tracked else 'Not tracked by DataLad'
        }
    
    def _get_datalad_status(self, dataset_path: str, stage_name: str) -> str:
        """Get DataLad status for a specific stage directory."""
        try:
            result = self.datalad_utils.get_status(dataset_path)
            return result.get('status_output', '')
        except Exception as e:
            print(f"Warning: Could not get DataLad status: {e}")
            return ""
    
    def _check_file_in_git(self, dataset_path: str, file_path: str) -> bool:
        """Check if a file is tracked in git."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', file_path],
                cwd=dataset_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_deleted_files(self, dataset_path: str, stage_name: str) -> List[Dict[str, Any]]:
        """Get list of deleted files in a stage from DataLad status."""
        try:
            import subprocess
            result = subprocess.run(
                ['datalad', 'status', stage_name],
                cwd=dataset_path,
                capture_output=True, 
                text=True,
                check=False
            )
            
            deleted_files = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('deleted:'):
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            file_info = parts[1].strip()
                            if '(' in file_info:
                                file_info = file_info.split('(')[0].strip()
                            filename = os.path.basename(file_info)
                            deleted_files.append({
                                'name': filename,
                                'path': file_info,
                                'status': 'Deleted',
                                'type': 'deleted'
                            })
            
            return deleted_files
        except Exception as e:
            print(f"Error getting deleted files: {e}")
            return []
    
    def get_file_tree(self, dataset_path: str) -> List[Dict[str, Any]]:
        """
        Get file tree structure of a dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            List containing file tree structure
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        def build_tree(path: str, relative_path: str = "") -> List[Dict[str, Any]]:
            tree = []
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    relative_item_path = os.path.join(relative_path, item) if relative_path else item
                    
                    if os.path.isdir(item_path):
                        # Skip .git and .datalad directories
                        if item in ['.git', '.datalad']:
                            continue
                        
                        children = build_tree(item_path, relative_item_path)
                        tree.append({
                            'name': item,
                            'path': relative_item_path,
                            'type': 'directory',
                            'children': children
                        })
                    else:
                        # Skip .DS_Store files
                        if item == '.DS_Store':
                            continue
                            
                        tree.append({
                            'name': item,
                            'path': relative_item_path,
                            'type': 'file',
                            'size': os.path.getsize(item_path)
                        })
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(dataset_path)
    
    def run_command_in_dataset(self, dataset_path: str, command: str, commit_message: str = None) -> dict:
        """
        Run a command in a DataLad dataset and track changes.
        
        Args:
            dataset_path: Path to the dataset
            command: Command to run
            commit_message: Optional commit message
        
        Returns:
            Dict containing command execution result
        
        Raises:
            DatasetError: If dataset is invalid
            FileOperationError: If command execution fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Handle existing output files that might be symbolic links
            # Extract output files from the command (simple parsing)
            import re
            output_files = []
            
            # Try to extract output files from command (basic parsing)
            # Look for patterns like "output.csv" or "results/file.csv"
            output_patterns = re.findall(r'\b(?:results|outputs?|plots?)/[^\s]+\.(?:csv|txt|json|png|jpg|pdf)\b', command)
            output_files = output_patterns
            
            # Remove existing output files if they are symbolic links
            for output_file in output_files:
                full_output_path = os.path.join(dataset_path, output_file)
                if os.path.exists(full_output_path) and os.path.islink(full_output_path):
                    try:
                        os.unlink(full_output_path)
                        print(f"Removed existing symbolic link: {output_file}")
                    except Exception as e:
                        print(f"Warning: Could not remove {output_file}: {e}")
            
            result = self.datalad_utils.run_command(
                dataset_path, 
                command, 
                message=commit_message
            )
            
            return {
                'command': command,
                'status': 'completed',
                'message': f'Command executed successfully',
                'datalad_result': result
            }
            
        except DataLadCommandError as e:
            raise FileOperationError(f"Command execution failed: {e.message}", operation="run_command")
        except Exception as e:
            raise FileOperationError(f"Failed to run command in dataset: {str(e)}", operation="run_command")
    
    def save_stage_changes(self, dataset_path: str, stage_name: str, commit_message: str = None) -> dict:
        """
        Save changes in a stage to DataLad.
        
        Args:
            dataset_path: Path to the dataset
            stage_name: Name of the stage
            commit_message: Optional commit message
        
        Returns:
            Dict containing save result
        
        Raises:
            DatasetError: If dataset is invalid
            FileOperationError: If save operation fails
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        stage_path = os.path.join(dataset_path, stage_name)
        if not os.path.exists(stage_path):
            raise FileOperationError(f"Stage directory not found: {stage_path}", file_path=stage_path)
        
        try:
            commit_msg = commit_message or f'Save stage changes: {stage_name}'
            result = self.datalad_utils.save_changes(dataset_path, commit_msg, [stage_name])
            
            return {
                'stage_name': stage_name,
                'status': 'saved',
                'message': f'Stage {stage_name} changes saved to DataLad',
                'datalad_result': result
            }
            
        except DataLadCommandError as e:
            raise FileOperationError(f"DataLad save failed: {e.message}", file_path=stage_path)
        except Exception as e:
            raise FileOperationError(f"Failed to save stage changes: {str(e)}", file_path=stage_path)
