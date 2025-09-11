"""
Project repository for SciTrace

Provides data access methods for project-related operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json

from .base_repository import BaseRepository
from ..models import Project
from ..exceptions import DatabaseError, ValidationError


class ProjectRepository(BaseRepository):
    """Repository for project data access operations."""
    
    def __init__(self):
        super().__init__(Project)
    
    def get_by_project_id(self, project_id: str) -> Optional[Project]:
        """
        Get project by project ID.
        
        Args:
            project_id: Project ID to search for
        
        Returns:
            Project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_first(project_id=project_id)
    
    def get_by_admin(self, admin_id: int) -> List[Project]:
        """
        Get projects by admin user ID.
        
        Args:
            admin_id: Admin user ID
        
        Returns:
            List of projects administered by the user
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(admin_id=admin_id)
    
    def get_by_status(self, status: str) -> List[Project]:
        """
        Get projects by status.
        
        Args:
            status: Project status
        
        Returns:
            List of projects with the specified status
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(status=status)
    
    def get_ongoing_projects(self) -> List[Project]:
        """
        Get all ongoing projects.
        
        Returns:
            List of ongoing projects
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_status('ongoing')
    
    def get_completed_projects(self) -> List[Project]:
        """
        Get all completed projects.
        
        Returns:
            List of completed projects
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_status('completed')
    
    def get_projects_with_datasets(self) -> List[Project]:
        """
        Get projects that have dataset paths.
        
        Returns:
            List of projects with datasets
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Project.query.filter(Project.dataset_path.isnot(None)).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get projects with datasets: {str(e)}")
    
    def get_projects_without_datasets(self) -> List[Project]:
        """
        Get projects that don't have dataset paths.
        
        Returns:
            List of projects without datasets
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Project.query.filter(Project.dataset_path.is_(None)).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get projects without datasets: {str(e)}")
    
    def create_project(self, project_id: str, name: str, description: str, admin_id: int, 
                      collaborators: List[int] = None, status: str = 'ongoing') -> Project:
        """
        Create a new project.
        
        Args:
            project_id: Unique project ID
            name: Project name
            description: Project description
            admin_id: Admin user ID
            collaborators: List of collaborator user IDs
            status: Project status (default: 'ongoing')
        
        Returns:
            Created project instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        # Check if project ID already exists
        if self.get_by_project_id(project_id):
            raise ValidationError(f"Project ID '{project_id}' already exists")
        
        # Validate status
        valid_statuses = ['ongoing', 'completed', 'paused', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Convert collaborators to JSON string
        collaborators_json = json.dumps(collaborators) if collaborators else None
        
        return self.create(
            project_id=project_id,
            name=name,
            description=description,
            admin_id=admin_id,
            collaborators=collaborators_json,
            status=status
        )
    
    def update_status(self, project_id: int, status: str) -> Optional[Project]:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New status
        
        Returns:
            Updated project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If status is invalid
        """
        valid_statuses = ['ongoing', 'completed', 'paused', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.update(project_id, status=status, updated_at=datetime.now(timezone.utc))
    
    def update_dataset_path(self, project_id: int, dataset_path: str) -> Optional[Project]:
        """
        Update project's dataset path.
        
        Args:
            project_id: Project ID
            dataset_path: Dataset path
        
        Returns:
            Updated project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(project_id, dataset_path=dataset_path, updated_at=datetime.now(timezone.utc))
    
    def update_git_remote(self, project_id: int, git_remote: str) -> Optional[Project]:
        """
        Update project's git remote URL.
        
        Args:
            project_id: Project ID
            git_remote: Git remote URL
        
        Returns:
            Updated project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(project_id, git_remote=git_remote, updated_at=datetime.now(timezone.utc))
    
    def add_collaborator(self, project_id: int, user_id: int) -> Optional[Project]:
        """
        Add a collaborator to a project.
        
        Args:
            project_id: Project ID
            user_id: User ID to add as collaborator
        
        Returns:
            Updated project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        collaborators = project.get_collaborators_list()
        if user_id not in collaborators:
            collaborators.append(user_id)
            collaborators_json = json.dumps(collaborators)
            return self.update(project_id, collaborators=collaborators_json, updated_at=datetime.now(timezone.utc))
        
        return project
    
    def remove_collaborator(self, project_id: int, user_id: int) -> Optional[Project]:
        """
        Remove a collaborator from a project.
        
        Args:
            project_id: Project ID
            user_id: User ID to remove as collaborator
        
        Returns:
            Updated project instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        project = self.get_by_id(project_id)
        if not project:
            return None
        
        collaborators = project.get_collaborators_list()
        if user_id in collaborators:
            collaborators.remove(user_id)
            collaborators_json = json.dumps(collaborators)
            return self.update(project_id, collaborators=collaborators_json, updated_at=datetime.now(timezone.utc))
        
        return project
    
    def get_collaborators(self, project_id: int) -> List[int]:
        """
        Get list of collaborator IDs for a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of collaborator user IDs
        
        Raises:
            DatabaseError: If database operation fails
        """
        project = self.get_by_id(project_id)
        if not project:
            return []
        
        return project.get_collaborators_list()
    
    def is_collaborator(self, project_id: int, user_id: int) -> bool:
        """
        Check if a user is a collaborator on a project.
        
        Args:
            project_id: Project ID
            user_id: User ID to check
        
        Returns:
            True if user is a collaborator, False otherwise
        
        Raises:
            DatabaseError: If database operation fails
        """
        collaborators = self.get_collaborators(project_id)
        return user_id in collaborators
    
    def has_access(self, project_id: int, user_id: int) -> bool:
        """
        Check if a user has access to a project (admin or collaborator).
        
        Args:
            project_id: Project ID
            user_id: User ID to check
        
        Returns:
            True if user has access, False otherwise
        
        Raises:
            DatabaseError: If database operation fails
        """
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        # Check if user is admin
        if project.admin_id == user_id:
            return True
        
        # Check if user is collaborator
        return self.is_collaborator(project_id, user_id)
    
    def search_projects(self, search_term: str) -> List[Project]:
        """
        Search projects by name or description.
        
        Args:
            search_term: Search term
        
        Returns:
            List of matching projects
        
        Raises:
            DatabaseError: If database operation fails
        """
        search_fields = ['name', 'description']
        return self.search(search_term, search_fields)
    
    def get_recent_projects(self, limit: int = 10) -> List[Project]:
        """
        Get recently created projects.
        
        Args:
            limit: Maximum number of projects to return
        
        Returns:
            List of recent projects
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Project.query.order_by(Project.created_at.desc()).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get recent projects: {str(e)}")
    
    def get_project_stats(self) -> Dict[str, int]:
        """
        Get project statistics.
        
        Returns:
            Dictionary with project statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            total_projects = self.count()
            ongoing_projects = len(self.get_ongoing_projects())
            completed_projects = len(self.get_completed_projects())
            projects_with_datasets = len(self.get_projects_with_datasets())
            
            return {
                'total_projects': total_projects,
                'ongoing_projects': ongoing_projects,
                'completed_projects': completed_projects,
                'projects_with_datasets': projects_with_datasets
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get project stats: {str(e)}")
    
    def get_user_project_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get project statistics for a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with user's project statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            user_projects = self.get_by_admin(user_id)
            ongoing = len([p for p in user_projects if p.status == 'ongoing'])
            completed = len([p for p in user_projects if p.status == 'completed'])
            with_datasets = len([p for p in user_projects if p.dataset_path])
            
            return {
                'total_projects': len(user_projects),
                'ongoing_projects': ongoing,
                'completed_projects': completed,
                'projects_with_datasets': with_datasets
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get user project stats: {str(e)}")
    
    def is_project_id_available(self, project_id: str) -> bool:
        """
        Check if project ID is available.
        
        Args:
            project_id: Project ID to check
        
        Returns:
            True if available, False if taken
        
        Raises:
            DatabaseError: If database operation fails
        """
        return not self.exists(project_id=project_id)
