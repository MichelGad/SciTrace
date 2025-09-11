"""
Main project service for SciTrace

Provides a unified interface for all project-related operations.
"""

from typing import Dict, List, Any, Optional

from .project_management import ProjectManagementService
from .dataset_integration import DatasetIntegrationService
from ..exceptions import ProjectError, ValidationError


class ProjectService:
    """Main service for project operations."""
    
    def __init__(self, db=None):
        self.project_management = ProjectManagementService(db)
        self.dataset_integration = DatasetIntegrationService(db)
    
    # Project Management Operations
    def create_project(self, name: str, description: str, admin_id: int, collaborators: List[int] = None) -> Dict[str, Any]:
        """Create a new project."""
        return self.project_management.create_project(name, description, admin_id, collaborators)
    
    def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """Get detailed information about a project."""
        return self.project_management.get_project_info(project_id)
    
    def get_project_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """Get dashboard data for a user's projects."""
        return self.project_management.get_project_dashboard_data(user_id)
    
    def update_project_status(self, project_id: str, status: str) -> Dict[str, Any]:
        """Update project status."""
        return self.project_management.update_project_status(project_id, status)
    
    def add_collaborator(self, project_id: str, user_id: int) -> Dict[str, Any]:
        """Add a collaborator to a project."""
        return self.project_management.add_collaborator(project_id, user_id)
    
    def remove_collaborator(self, project_id: str, user_id: int) -> Dict[str, Any]:
        """Remove a collaborator from a project."""
        return self.project_management.remove_collaborator(project_id, user_id)
    
    def get_project_collaborators(self, project_id: str) -> List[Dict[str, Any]]:
        """Get list of project collaborators."""
        return self.project_management.get_project_collaborators(project_id)
    
    # Dataset Integration Operations
    def create_dataset_for_project(self, project_id: str, project_name: str, research_type: str = "general") -> Dict[str, Any]:
        """Create a DataLad dataset for a project."""
        return self.dataset_integration.create_dataset_for_project(project_id, project_name, research_type)
    
    def get_project_dataset_info(self, project_id: str) -> Dict[str, Any]:
        """Get dataset information for a project."""
        return self.dataset_integration.get_project_dataset_info(project_id)
    
    def get_project_dataflow(self, project_id: str) -> Dict[str, Any]:
        """Get dataflow visualization for a project's dataset."""
        return self.dataset_integration.get_project_dataflow(project_id)
    
    def get_project_commit_history(self, project_id: str, file_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get commit history for a project's dataset."""
        return self.dataset_integration.get_project_commit_history(project_id, file_path, limit)
    
    def restore_project_file(self, project_id: str, file_path: str, commit_hash: str, commit_message: str = None) -> Dict[str, Any]:
        """Restore a file in a project's dataset to a specific commit."""
        return self.dataset_integration.restore_project_file(project_id, file_path, commit_hash, commit_message)
    
    def get_project_file_tree(self, project_id: str) -> List[Dict[str, Any]]:
        """Get file tree structure for a project's dataset."""
        return self.dataset_integration.get_project_file_tree(project_id)
    
    def get_project_stage_files(self, project_id: str, stage_name: str) -> Optional[Dict[str, Any]]:
        """Get files for a specific stage in a project's dataset."""
        return self.dataset_integration.get_project_stage_files(project_id, stage_name)
    
    def save_project_stage_changes(self, project_id: str, stage_name: str, commit_message: str = None) -> Dict[str, Any]:
        """Save changes in a stage of a project's dataset."""
        return self.dataset_integration.save_project_stage_changes(project_id, stage_name, commit_message)
    
    # Legacy compatibility methods (for backward compatibility with existing code)
    def get_commit_history(self, dataset_path: str, file_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Legacy method for getting commit history."""
        # This method is kept for backward compatibility
        # It should be replaced with get_project_commit_history in new code
        from .git_operations import GitOperationsService
        git_ops = GitOperationsService()
        return git_ops.get_commit_history(dataset_path, file_path, limit)
    
    def restore_file_to_commit(self, dataset_path: str, file_path: str, commit_hash: str, commit_message: str = None) -> Dict[str, Any]:
        """Legacy method for restoring files."""
        # This method is kept for backward compatibility
        # It should be replaced with restore_project_file in new code
        from .git_operations import GitOperationsService
        git_ops = GitOperationsService()
        return git_ops.restore_file_to_commit(dataset_path, file_path, commit_hash, commit_message)
    
    def get_file_commit_history(self, dataset_path: str, file_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Legacy method for getting file commit history."""
        # This method is kept for backward compatibility
        # It should be replaced with get_project_commit_history in new code
        from .git_operations import GitOperationsService
        git_ops = GitOperationsService()
        return git_ops.get_file_commit_history(dataset_path, file_path, limit)
    
    def check_file_exists_in_commit(self, dataset_path: str, file_path: str, commit_hash: str) -> bool:
        """Legacy method for checking file existence in commit."""
        # This method is kept for backward compatibility
        from .git_operations import GitOperationsService
        git_ops = GitOperationsService()
        return git_ops.check_file_exists_in_commit(dataset_path, file_path, commit_hash)
