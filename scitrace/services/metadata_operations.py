"""
Metadata operations services for SciTrace

Handles metadata operations and dataset information retrieval.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from ..utils.datalad_utils import DataLadUtils, DataLadCommandError
from ..exceptions import DatasetError, ValidationError
from .base_service import BaseService


class MetadataOperationsService(BaseService):
    """Service for metadata operations and dataset information."""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.datalad_utils = DataLadUtils()
    
    def get_dataset_info(self, dataset_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing dataset information
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get dataset status
            status_result = self.datalad_utils.get_status(dataset_path)
            
            # Get dataset metadata
            metadata_result = self.datalad_utils.get_metadata(dataset_path)
            
            # Get basic dataset information
            dataset_info = {
                'path': dataset_path,
                'name': os.path.basename(dataset_path),
                'status': status_result.get('status_output', ''),
                'metadata': metadata_result.get('metadata_output', ''),
                'has_metadata': metadata_result.get('has_metadata', False),
                'exists': True,
                'is_datalad': os.path.exists(os.path.join(dataset_path, '.datalad')),
                'is_git': os.path.exists(os.path.join(dataset_path, '.git')),
                'created_at': self._get_creation_time(dataset_path),
                'last_modified': self._get_last_modified_time(dataset_path)
            }
            
            return dataset_info
            
        except DataLadCommandError as e:
            raise DatasetError(f"Failed to get dataset info: {e.message}", dataset_path=dataset_path)
        except Exception as e:
            raise DatasetError(f"Unexpected error getting dataset info: {str(e)}", dataset_path=dataset_path)
    
    def get_dataset_summary(self, dataset_path: str) -> Dict[str, Any]:
        """
        Get a summary of dataset contents and structure.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing dataset summary
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get file tree structure
            from .file_operations import FileOperationsService
            file_ops = FileOperationsService()
            file_tree = file_ops.get_file_tree(dataset_path)
            
            # Analyze structure
            total_files = 0
            total_dirs = 0
            file_types = {}
            total_size = 0
            
            def analyze_tree(items):
                nonlocal total_files, total_dirs, total_size
                for item in items:
                    if item['type'] == 'directory':
                        total_dirs += 1
                        if 'children' in item:
                            analyze_tree(item['children'])
                    else:
                        total_files += 1
                        if 'size' in item:
                            total_size += item['size']
                        
                        # Count file types
                        ext = os.path.splitext(item['name'])[1].lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
            
            analyze_tree(file_tree)
            
            # Get commit count
            commit_count = 0
            try:
                from .git_operations import GitOperationsService
                git_ops = GitOperationsService()
                commits = git_ops.get_commit_history(dataset_path, limit=1000)
                commit_count = len(commits)
            except Exception:
                pass  # Git operations might fail, that's okay
            
            return {
                'dataset_path': dataset_path,
                'dataset_name': os.path.basename(dataset_path),
                'structure': {
                    'total_files': total_files,
                    'total_directories': total_dirs,
                    'file_types': file_types,
                    'total_size_bytes': total_size,
                    'total_size_human': self._format_file_size(total_size)
                },
                'version_control': {
                    'is_git': os.path.exists(os.path.join(dataset_path, '.git')),
                    'is_datalad': os.path.exists(os.path.join(dataset_path, '.datalad')),
                    'commit_count': commit_count
                },
                'file_tree': file_tree
            }
            
        except Exception as e:
            raise DatasetError(f"Failed to get dataset summary: {str(e)}", dataset_path=dataset_path)
    
    def create_dataflow_from_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Create a dataflow visualization from dataset structure as a spider web.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing dataflow nodes, edges, and metadata
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get actual dataset structure
            from .file_operations import FileOperationsService
            file_ops = FileOperationsService()
            file_tree = file_ops.get_file_tree(dataset_path)
            
            # Analyze dataset content and create spider web workflow
            nodes = []
            edges = []
            node_id = 1
            
            # Define directory types and their colors
            directory_types = {
                'raw_data': {'color': '#87CEEB', 'type': 'raw_data', 'description': 'Raw data files'},
                'preprocessed': {'color': '#90EE90', 'type': 'preprocessed', 'description': 'Preprocessed data files'},
                'scripts': {'color': '#4CAF50', 'type': 'scripts', 'description': 'Analysis and processing scripts'},
                'results': {'color': '#FFA07A', 'type': 'results', 'description': 'Final results and outputs'},
                'plots': {'color': '#DDA0DD', 'type': 'plots', 'description': 'Generated visualizations'}
            }
            
            # Create central "Dataset Root" node
            central_node = {
                'id': node_id,
                'label': 'Dataset Root',
                'type': 'dataset_root',
                'path': dataset_path,
                'color': '#4CAF50',
                'description': 'Root of the research dataset',
                'file_count': 0,
                'is_central': True
            }
            nodes.append(central_node)
            central_node_id = node_id
            node_id += 1
            
            # Create nodes for each directory that exists
            directory_nodes = {}
            for item in file_tree:
                if item['type'] == 'directory' and item['name'] in directory_types:
                    dir_type = directory_types[item['name']]
                    
                    # Count files in this directory
                    file_count = len([f for f in item.get('children', []) if f['type'] == 'file'])
                    
                    # Get tracking status for this directory
                    stage_data = file_ops.get_stage_files(dataset_path, item['name'])
                    tracked_count = stage_data['metadata']['tracked_files'] if stage_data else 0
                    untracked_count = stage_data['metadata']['untracked_files'] if stage_data else 0
                    deleted_count = stage_data['metadata']['deleted_files'] if stage_data else 0
                    
                    # Determine node color based on status
                    base_color = dir_type['color']
                    if deleted_count > 0:
                        node_color = '#FF6B6B'  # Red for deleted files
                    elif untracked_count > 0:
                        node_color = '#FFA500'  # Orange for untracked files
                    else:
                        node_color = base_color
                    
                    # Create label with status information
                    status_parts = []
                    if file_count > 0:
                        status_parts.append(f"{file_count} files")
                    if untracked_count > 0:
                        status_parts.append(f"{untracked_count} untracked")
                    if deleted_count > 0:
                        status_parts.append(f"{deleted_count} deleted")
                    
                    if status_parts:
                        label = f"{item['name']}\n({', '.join(status_parts)})"
                    else:
                        label = f"{item['name']}\n(0 files)"
                    
                    node = {
                        'id': node_id,
                        'label': label,
                        'type': dir_type['type'],
                        'path': item['path'],
                        'color': node_color,
                        'description': dir_type['description'],
                        'file_count': file_count,
                        'tracked_files': tracked_count,
                        'untracked_files': untracked_count,
                        'deleted_files': deleted_count,
                        'has_untracked': untracked_count > 0,
                        'has_deleted': deleted_count > 0,
                        'is_central': False
                    }
                    nodes.append(node)
                    directory_nodes[item['name']] = node_id
                    node_id += 1
            
            # Add missing workflow stages (even if directories don't exist yet)
            missing_stages = {
                'scripts': {'color': '#4CAF50', 'type': 'scripts', 'description': 'Analysis and processing scripts'},
                'results': {'color': '#FFA07A', 'type': 'results', 'description': 'Final results and outputs'},
                'plots': {'color': '#DDA0DD', 'type': 'plots', 'description': 'Generated visualizations'}
            }
            
            for stage_name, stage_info in missing_stages.items():
                if stage_name not in directory_nodes:
                    node = {
                        'id': node_id,
                        'label': f"{stage_name}\n(0 files)",
                        'type': stage_info['type'],
                        'path': f"{stage_name}/",
                        'color': stage_info['color'],
                        'description': stage_info['description'],
                        'file_count': 0,
                        'is_central': False
                    }
                    nodes.append(node)
                    directory_nodes[stage_name] = node_id
                    node_id += 1
            
            # Create spider web connections - all directories connect to Dataset Root
            for dir_name, dir_node_id in directory_nodes.items():
                edge = {
                    'from': central_node_id,
                    'to': dir_node_id,
                    'arrows': 'to',
                    'label': 'contains',
                    'color': '#666'
                }
                edges.append(edge)
            
            # If no directories found, create a basic spider web
            if len(nodes) == 1:  # Only central node exists
                basic_dirs = ['raw_data', 'preprocessed', 'scripts', 'results', 'plots']
                for dir_name in basic_dirs:
                    dir_info = directory_types.get(dir_name, {'color': '#87CEEB', 'type': 'raw_data', 'description': f'{dir_name} directory'})
                    node = {
                        'id': node_id,
                        'label': f"{dir_name}\n(0 files)",
                        'type': dir_info['type'],
                        'path': f"{dir_name}/",
                        'color': dir_info['color'],
                        'description': dir_info['description'],
                        'file_count': 0,
                        'is_central': False
                    }
                    nodes.append(node)
                    
                    # Connect to central node
                    edge = {
                        'from': central_node_id,
                        'to': node_id,
                        'arrows': 'to',
                        'label': 'contains',
                        'color': '#666'
                    }
                    edges.append(edge)
                    node_id += 1
            
            # Create metadata
            metadata = {
                'dataset_path': dataset_path,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'workflow_type': 'spider_web_directory',
                'total_stages': len(nodes),
                'total_connections': len(edges),
                'description': 'Directory structure visualization as spider web with Dataset Root as central node',
                'visualization_type': 'spider_web'
            }
            
            return {
                'nodes': nodes,
                'edges': edges,
                'metadata': metadata
            }
            
        except Exception as e:
            raise DatasetError(f"Failed to create dataflow from dataset: {str(e)}", dataset_path=dataset_path)
    
    def get_dataset_metadata(self, dataset_path: str) -> Dict[str, Any]:
        """
        Get metadata information for a dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing metadata information
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            raise DatasetError(f"Dataset path does not exist: {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Get DataLad metadata
            metadata_result = self.datalad_utils.get_metadata(dataset_path)
            
            # Get basic file system metadata
            stat_info = os.stat(dataset_path)
            
            # Get git metadata if available
            git_metadata = {}
            if os.path.exists(os.path.join(dataset_path, '.git')):
                try:
                    from .git_operations import GitOperationsService
                    git_ops = GitOperationsService()
                    git_metadata = {
                        'current_branch': git_ops.get_current_branch(dataset_path),
                        'commit_count': len(git_ops.get_commit_history(dataset_path, limit=1000))
                    }
                except Exception:
                    pass  # Git operations might fail
            
            return {
                'dataset_path': dataset_path,
                'dataset_name': os.path.basename(dataset_path),
                'datalad_metadata': metadata_result.get('metadata_output', ''),
                'has_datalad_metadata': metadata_result.get('has_metadata', False),
                'filesystem_metadata': {
                    'created_at': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                    'accessed_at': datetime.fromtimestamp(stat_info.st_atime).isoformat(),
                    'permissions': oct(stat_info.st_mode)[-3:]
                },
                'git_metadata': git_metadata,
                'is_datalad': os.path.exists(os.path.join(dataset_path, '.datalad')),
                'is_git': os.path.exists(os.path.join(dataset_path, '.git'))
            }
            
        except Exception as e:
            raise DatasetError(f"Failed to get dataset metadata: {str(e)}", dataset_path=dataset_path)
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Validate a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing validation results
        
        Raises:
            DatasetError: If dataset is invalid
        """
        if not os.path.exists(dataset_path):
            return {
                'valid': False,
                'errors': [f"Dataset path does not exist: {dataset_path}"]
            }
        
        errors = []
        warnings = []
        
        # Check for .git directory
        if not os.path.exists(os.path.join(dataset_path, '.git')):
            errors.append("Missing .git directory - not a valid git repository")
        
        # Check for .datalad directory
        if not os.path.exists(os.path.join(dataset_path, '.datalad')):
            warnings.append("Missing .datalad directory - may not be a DataLad dataset")
        
        # Try to get status
        try:
            status_result = self.datalad_utils.get_status(dataset_path)
        except DataLadCommandError as e:
            errors.append(f"Failed to get dataset status: {e.message}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'dataset_path': dataset_path
        }
    
    def _get_creation_time(self, dataset_path: str) -> Optional[str]:
        """Get dataset creation time."""
        try:
            stat_info = os.stat(dataset_path)
            return datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        except Exception:
            return None
    
    def _get_last_modified_time(self, dataset_path: str) -> Optional[str]:
        """Get dataset last modified time."""
        try:
            stat_info = os.stat(dataset_path)
            return datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        except Exception:
            return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
