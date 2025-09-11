"""
Dataset integration services for SciTrace

Handles integration between projects and DataLad datasets.
"""

import os
from typing import Dict, List, Any, Optional

from ..services.base_service import BaseService
from ..services.dataset_creation import DatasetCreationService
from ..services.file_operations import FileOperationsService
from ..services.git_operations import GitOperationsService
from ..services.metadata_operations import MetadataOperationsService
from ..exceptions import ProjectError, DatasetError, ValidationError


class DatasetIntegrationService(BaseService):
    """Service for integrating projects with DataLad datasets."""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.dataset_creation = DatasetCreationService(db)
        self.file_operations = FileOperationsService(db)
        self.git_operations = GitOperationsService(db)
        self.metadata_operations = MetadataOperationsService(db)
    
    def create_dataset_for_project(self, project_id: str, project_name: str, research_type: str = "general") -> Dict[str, Any]:
        """
        Create a DataLad dataset for a project.
        
        Args:
            project_id: Project ID
            project_name: Project name
            research_type: Type of research
        
        Returns:
            Dict containing dataset creation result
        
        Raises:
            ProjectError: If project operation fails
            DatasetError: If dataset creation fails
        """
        try:
            # Generate dataset path
            dataset_path = self._generate_dataset_path(project_id, project_name)
            
            # Create the dataset
            result = self.dataset_creation.create_dataset_with_content(
                dataset_path, 
                project_name, 
                research_type
            )
            
            # Update project with dataset path
            self._update_project_dataset_path(project_id, dataset_path)
            
            return {
                'project_id': project_id,
                'dataset_path': dataset_path,
                'dataset_name': project_name,
                'research_type': research_type,
                'creation_result': result,
                'success': True
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to create dataset for project: {str(e)}")
    
    def get_project_dataset_info(self, project_id: str) -> Dict[str, Any]:
        """
        Get dataset information for a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dict containing dataset information
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                return {
                    'project_id': project_id,
                    'has_dataset': False,
                    'dataset_path': None
                }
            
            # Get dataset information
            dataset_info = self.metadata_operations.get_dataset_info(dataset_path)
            dataset_summary = self.metadata_operations.get_dataset_summary(dataset_path)
            
            return {
                'project_id': project_id,
                'has_dataset': True,
                'dataset_path': dataset_path,
                'dataset_info': dataset_info,
                'dataset_summary': dataset_summary
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to get project dataset info: {str(e)}")
    
    def get_project_dataflow(self, project_id: str) -> Dict[str, Any]:
        """
        Get dataflow visualization for a project's dataset.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dict containing dataflow information
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                return {
                    'project_id': project_id,
                    'has_dataset': False,
                    'dataflow': None
                }
            
            # Create dataflow from dataset
            dataflow = self.metadata_operations.create_dataflow_from_dataset(dataset_path)
            
            return {
                'project_id': project_id,
                'has_dataset': True,
                'dataset_path': dataset_path,
                'dataflow': dataflow
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to get project dataflow: {str(e)}")
    
    def get_project_commit_history(self, project_id: str, file_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get commit history for a project's dataset.
        
        Args:
            project_id: Project ID
            file_path: Optional specific file path
            limit: Maximum number of commits to return
        
        Returns:
            List of commit information
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                return []
            
            # Get commit history
            if file_path:
                commits = self.git_operations.get_file_commit_history(dataset_path, file_path, limit)
            else:
                commits = self.git_operations.get_commit_history(dataset_path, limit=limit)
            
            return commits
            
        except Exception as e:
            raise ProjectError(f"Failed to get project commit history: {str(e)}")
    
    def restore_project_file(self, project_id: str, file_path: str, commit_hash: str, commit_message: str = None) -> Dict[str, Any]:
        """
        Restore a file in a project's dataset to a specific commit.
        
        Args:
            project_id: Project ID
            file_path: Path to the file to restore
            commit_hash: Commit hash to restore from
            commit_message: Optional commit message
        
        Returns:
            Dict containing restoration result
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                raise ProjectError(f"Project {project_id} does not have a dataset")
            
            # Restore the file
            result = self.git_operations.restore_file_to_commit(
                dataset_path, 
                file_path, 
                commit_hash, 
                commit_message
            )
            
            return {
                'project_id': project_id,
                'file_path': file_path,
                'commit_hash': commit_hash,
                'restoration_result': result,
                'success': True
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to restore project file: {str(e)}")
    
    def get_project_file_tree(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get file tree structure for a project's dataset.
        
        Args:
            project_id: Project ID
        
        Returns:
            List containing file tree structure
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                return []
            
            # Get file tree
            file_tree = self.file_operations.get_file_tree(dataset_path)
            
            return file_tree
            
        except Exception as e:
            raise ProjectError(f"Failed to get project file tree: {str(e)}")
    
    def get_project_stage_files(self, project_id: str, stage_name: str) -> Optional[Dict[str, Any]]:
        """
        Get files for a specific stage in a project's dataset.
        
        Args:
            project_id: Project ID
            stage_name: Name of the stage/directory
        
        Returns:
            Dict containing stage file information or None if not found
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                return None
            
            # Get stage files
            stage_files = self.file_operations.get_stage_files(dataset_path, stage_name)
            
            return stage_files
            
        except Exception as e:
            raise ProjectError(f"Failed to get project stage files: {str(e)}")
    
    def save_project_stage_changes(self, project_id: str, stage_name: str, commit_message: str = None) -> Dict[str, Any]:
        """
        Save changes in a stage of a project's dataset.
        
        Args:
            project_id: Project ID
            stage_name: Name of the stage
            commit_message: Optional commit message
        
        Returns:
            Dict containing save result
        
        Raises:
            ProjectError: If project not found
            DatasetError: If dataset not found
        """
        try:
            # Get project dataset path
            dataset_path = self._get_project_dataset_path(project_id)
            
            if not dataset_path or not os.path.exists(dataset_path):
                raise ProjectError(f"Project {project_id} does not have a dataset")
            
            # Save stage changes
            result = self.file_operations.save_stage_changes(
                dataset_path, 
                stage_name, 
                commit_message
            )
            
            return {
                'project_id': project_id,
                'stage_name': stage_name,
                'save_result': result,
                'success': True
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to save project stage changes: {str(e)}")
    
    def _generate_dataset_path(self, project_id: str, project_name: str) -> str:
        """Generate dataset path for a project."""
        # Get base path from environment or use default
        home_dir = os.path.expanduser("~")
        base_path = os.environ.get('DATALAD_BASE_PATH', os.path.join(home_dir, 'scitrace_demo_datasets'))
        
        # Create project-specific directory
        project_dir = f"{project_id}_{project_name.replace(' ', '_')}"
        dataset_path = os.path.join(base_path, project_dir)
        
        return dataset_path
    
    def _get_project_dataset_path(self, project_id: str) -> Optional[str]:
        """Get dataset path for a project."""
        # This would typically query the database
        # For now, return None as placeholder
        return None
    
    def _update_project_dataset_path(self, project_id: str, dataset_path: str) -> None:
        """Update project with dataset path."""
        # This would typically update the database
        # For now, do nothing as placeholder
        pass
