"""
Project management services for SciTrace

Handles project creation, management, and dashboard operations.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from ..services.base_service import BaseService
from ..exceptions import ProjectError, ValidationError


class ProjectManagementService(BaseService):
    """Service for project management operations."""
    
    def __init__(self, db=None):
        super().__init__(db)
    
    def create_project(self, name: str, description: str, admin_id: int, collaborators: List[int] = None) -> Dict[str, Any]:
        """
        Create a new project in the database.
        
        Args:
            name: Project name
            description: Project description
            admin_id: ID of the project administrator
            collaborators: List of collaborator user IDs
        
        Returns:
            Dict containing project information
        
        Raises:
            ProjectError: If project creation fails
            ValidationError: If parameters are invalid
        """
        if not name or not name.strip():
            raise ValidationError("Project name is required")
        
        if not description or not description.strip():
            raise ValidationError("Project description is required")
        
        if not admin_id:
            raise ValidationError("Admin ID is required")
        
        if collaborators is None:
            collaborators = []
        
        try:
            # Generate unique project ID
            project_id = self._generate_project_id()
            
            # Create project data
            project_data = {
                'id': project_id,
                'name': name.strip(),
                'description': description.strip(),
                'admin_id': admin_id,
                'collaborators': collaborators,
                'dataset_path': None,  # No dataset created yet
                'status': 'ongoing',
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            
            return project_data
            
        except Exception as e:
            raise ProjectError(f"Failed to create project: {str(e)}")
    
    def get_project_info(self, project_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dict containing project information
        
        Raises:
            ProjectError: If project not found
        """
        try:
            # This would typically query the database
            # For now, return basic structure
            return {
                'project_id': project_id,
                'status': 'ongoing',
                'exists': True
            }
        except Exception as e:
            raise ProjectError(f"Failed to get project info: {str(e)}")
    
    def get_project_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get dashboard data for a user's projects.
        
        Args:
            user_id: User ID
        
        Returns:
            Dict containing dashboard data
        
        Raises:
            ProjectError: If dashboard data retrieval fails
        """
        try:
            from ..models import Project, Task, Dataflow
            
            # Get user's projects
            projects = Project.query.filter_by(admin_id=user_id).all()
            
            # Get tasks for these projects
            project_ids = [p.id for p in projects]
            tasks = Task.query.filter(Task.project_id.in_(project_ids)).all() if project_ids else []
            
            # Get dataflows for these projects
            dataflows = Dataflow.query.filter(Dataflow.project_id.in_(project_ids)).all() if project_ids else []
            
            # Calculate statistics
            stats = self._calculate_project_stats(projects, tasks, dataflows)
            
            return {
                'projects': projects,
                'tasks': tasks,
                'dataflows': dataflows,
                'stats': stats
            }
            
        except Exception as e:
            raise ProjectError(f"Failed to get dashboard data: {str(e)}")
    
    def update_project_status(self, project_id: str, status: str) -> Dict[str, Any]:
        """
        Update project status.
        
        Args:
            project_id: Project ID
            status: New status
        
        Returns:
            Dict containing update result
        
        Raises:
            ProjectError: If update fails
            ValidationError: If status is invalid
        """
        valid_statuses = ['ongoing', 'completed', 'paused', 'cancelled']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        try:
            # This would typically update the database
            return {
                'project_id': project_id,
                'status': status,
                'updated_at': datetime.now(timezone.utc),
                'success': True
            }
        except Exception as e:
            raise ProjectError(f"Failed to update project status: {str(e)}")
    
    def add_collaborator(self, project_id: str, user_id: int) -> Dict[str, Any]:
        """
        Add a collaborator to a project.
        
        Args:
            project_id: Project ID
            user_id: User ID to add as collaborator
        
        Returns:
            Dict containing operation result
        
        Raises:
            ProjectError: If operation fails
        """
        try:
            # This would typically update the database
            return {
                'project_id': project_id,
                'user_id': user_id,
                'action': 'added',
                'success': True
            }
        except Exception as e:
            raise ProjectError(f"Failed to add collaborator: {str(e)}")
    
    def remove_collaborator(self, project_id: str, user_id: int) -> Dict[str, Any]:
        """
        Remove a collaborator from a project.
        
        Args:
            project_id: Project ID
            user_id: User ID to remove as collaborator
        
        Returns:
            Dict containing operation result
        
        Raises:
            ProjectError: If operation fails
        """
        try:
            # This would typically update the database
            return {
                'project_id': project_id,
                'user_id': user_id,
                'action': 'removed',
                'success': True
            }
        except Exception as e:
            raise ProjectError(f"Failed to remove collaborator: {str(e)}")
    
    def get_project_collaborators(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Get list of project collaborators.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of collaborator information
        
        Raises:
            ProjectError: If retrieval fails
        """
        try:
            # This would typically query the database
            return []
        except Exception as e:
            raise ProjectError(f"Failed to get collaborators: {str(e)}")
    
    def _generate_project_id(self) -> str:
        """Generate a unique project ID."""
        return str(uuid.uuid4())[:8].upper()
    
    def _calculate_project_stats(self, projects: List, tasks: List, dataflows: List) -> Dict[str, int]:
        """Calculate project statistics."""
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
