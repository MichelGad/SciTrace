"""
Task repository for SciTrace

Provides data access methods for task-related operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

from .base_repository import BaseRepository
from ..models import Task
from ..exceptions import DatabaseError, ValidationError


class TaskRepository(BaseRepository):
    """Repository for task data access operations."""
    
    def __init__(self):
        super().__init__(Task)
    
    def get_by_user(self, user_id: int) -> List[Task]:
        """
        Get tasks by user ID.
        
        Args:
            user_id: User ID
        
        Returns:
            List of tasks assigned to the user
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(user_id=user_id)
    
    def get_by_project(self, project_id: int) -> List[Task]:
        """
        Get tasks by project ID.
        
        Args:
            project_id: Project ID
        
        Returns:
            List of tasks in the project
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(project_id=project_id)
    
    def get_by_status(self, status: str) -> List[Task]:
        """
        Get tasks by status.
        
        Args:
            status: Task status
        
        Returns:
            List of tasks with the specified status
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(status=status)
    
    def get_by_priority(self, priority: str) -> List[Task]:
        """
        Get tasks by priority.
        
        Args:
            priority: Task priority
        
        Returns:
            List of tasks with the specified priority
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(priority=priority)
    
    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks.
        
        Returns:
            List of pending tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_status('pending')
    
    def get_ongoing_tasks(self) -> List[Task]:
        """
        Get all ongoing tasks.
        
        Returns:
            List of ongoing tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_status('ongoing')
    
    def get_completed_tasks(self) -> List[Task]:
        """
        Get all completed tasks.
        
        Returns:
            List of completed tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_status('done')
    
    def get_urgent_tasks(self) -> List[Task]:
        """
        Get all urgent tasks.
        
        Returns:
            List of urgent tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.get_by_priority('urgent')
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Get tasks that are overdue.
        
        Returns:
            List of overdue tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            now = datetime.now(timezone.utc)
            return Task.query.filter(
                Task.deadline < now,
                Task.status.in_(['pending', 'ongoing'])
            ).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get overdue tasks: {str(e)}")
    
    def get_tasks_due_soon(self, days: int = 7) -> List[Task]:
        """
        Get tasks due within the specified number of days.
        
        Args:
            days: Number of days to look ahead
        
        Returns:
            List of tasks due soon
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            now = datetime.now(timezone.utc)
            future_date = now + timedelta(days=days)
            
            return Task.query.filter(
                Task.deadline >= now,
                Task.deadline <= future_date,
                Task.status.in_(['pending', 'ongoing'])
            ).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks due soon: {str(e)}")
    
    def get_user_tasks_by_status(self, user_id: int, status: str) -> List[Task]:
        """
        Get user's tasks by status.
        
        Args:
            user_id: User ID
            status: Task status
        
        Returns:
            List of user's tasks with the specified status
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Task.query.filter_by(user_id=user_id, status=status).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get user tasks by status: {str(e)}")
    
    def get_project_tasks_by_status(self, project_id: int, status: str) -> List[Task]:
        """
        Get project's tasks by status.
        
        Args:
            project_id: Project ID
            status: Task status
        
        Returns:
            List of project's tasks with the specified status
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Task.query.filter_by(project_id=project_id, status=status).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get project tasks by status: {str(e)}")
    
    def create_task(self, title: str, description: str, user_id: int, project_id: int,
                   deadline: datetime = None, priority: str = 'medium', status: str = 'pending') -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            user_id: User ID
            project_id: Project ID
            deadline: Task deadline (optional)
            priority: Task priority (default: 'medium')
            status: Task status (default: 'pending')
        
        Returns:
            Created task instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        # Validate priority
        valid_priorities = ['low', 'medium', 'urgent']
        if priority not in valid_priorities:
            raise ValidationError(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
        
        # Validate status
        valid_statuses = ['pending', 'ongoing', 'done']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.create(
            title=title,
            description=description,
            user_id=user_id,
            project_id=project_id,
            deadline=deadline,
            priority=priority,
            status=status
        )
    
    def update_status(self, task_id: int, status: str) -> Optional[Task]:
        """
        Update task status.
        
        Args:
            task_id: Task ID
            status: New status
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If status is invalid
        """
        valid_statuses = ['pending', 'ongoing', 'done']
        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        return self.update(task_id, status=status, updated_at=datetime.now(timezone.utc))
    
    def update_priority(self, task_id: int, priority: str) -> Optional[Task]:
        """
        Update task priority.
        
        Args:
            task_id: Task ID
            priority: New priority
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If priority is invalid
        """
        valid_priorities = ['low', 'medium', 'urgent']
        if priority not in valid_priorities:
            raise ValidationError(f"Invalid priority. Must be one of: {', '.join(valid_priorities)}")
        
        return self.update(task_id, priority=priority, updated_at=datetime.now(timezone.utc))
    
    def update_deadline(self, task_id: int, deadline: datetime) -> Optional[Task]:
        """
        Update task deadline.
        
        Args:
            task_id: Task ID
            deadline: New deadline
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(task_id, deadline=deadline, updated_at=datetime.now(timezone.utc))
    
    def assign_task(self, task_id: int, user_id: int) -> Optional[Task]:
        """
        Assign a task to a user.
        
        Args:
            task_id: Task ID
            user_id: User ID to assign to
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(task_id, user_id=user_id, updated_at=datetime.now(timezone.utc))
    
    def complete_task(self, task_id: int) -> Optional[Task]:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update_status(task_id, 'done')
    
    def reopen_task(self, task_id: int) -> Optional[Task]:
        """
        Reopen a completed task.
        
        Args:
            task_id: Task ID
        
        Returns:
            Updated task instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update_status(task_id, 'pending')
    
    def search_tasks(self, search_term: str) -> List[Task]:
        """
        Search tasks by title or description.
        
        Args:
            search_term: Search term
        
        Returns:
            List of matching tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        search_fields = ['title', 'description']
        return self.search(search_term, search_fields)
    
    def get_recent_tasks(self, limit: int = 10) -> List[Task]:
        """
        Get recently created tasks.
        
        Args:
            limit: Maximum number of tasks to return
        
        Returns:
            List of recent tasks
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Task.query.order_by(Task.created_at.desc()).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get recent tasks: {str(e)}")
    
    def get_task_stats(self) -> Dict[str, int]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with task statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            total_tasks = self.count()
            pending_tasks = len(self.get_pending_tasks())
            ongoing_tasks = len(self.get_ongoing_tasks())
            completed_tasks = len(self.get_completed_tasks())
            urgent_tasks = len(self.get_urgent_tasks())
            overdue_tasks = len(self.get_overdue_tasks())
            
            return {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'ongoing_tasks': ongoing_tasks,
                'completed_tasks': completed_tasks,
                'urgent_tasks': urgent_tasks,
                'overdue_tasks': overdue_tasks
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get task stats: {str(e)}")
    
    def get_user_task_stats(self, user_id: int) -> Dict[str, int]:
        """
        Get task statistics for a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with user's task statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            user_tasks = self.get_by_user(user_id)
            pending = len([t for t in user_tasks if t.status == 'pending'])
            ongoing = len([t for t in user_tasks if t.status == 'ongoing'])
            completed = len([t for t in user_tasks if t.status == 'done'])
            urgent = len([t for t in user_tasks if t.priority == 'urgent'])
            
            # Get overdue tasks for this user
            now = datetime.now(timezone.utc)
            overdue = len([t for t in user_tasks 
                          if t.deadline and t.deadline < now and t.status in ['pending', 'ongoing']])
            
            return {
                'total_tasks': len(user_tasks),
                'pending_tasks': pending,
                'ongoing_tasks': ongoing,
                'completed_tasks': completed,
                'urgent_tasks': urgent,
                'overdue_tasks': overdue
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get user task stats: {str(e)}")
    
    def get_project_task_stats(self, project_id: int) -> Dict[str, int]:
        """
        Get task statistics for a specific project.
        
        Args:
            project_id: Project ID
        
        Returns:
            Dictionary with project's task statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            project_tasks = self.get_by_project(project_id)
            pending = len([t for t in project_tasks if t.status == 'pending'])
            ongoing = len([t for t in project_tasks if t.status == 'ongoing'])
            completed = len([t for t in project_tasks if t.status == 'done'])
            urgent = len([t for t in project_tasks if t.priority == 'urgent'])
            
            return {
                'total_tasks': len(project_tasks),
                'pending_tasks': pending,
                'ongoing_tasks': ongoing,
                'completed_tasks': completed,
                'urgent_tasks': urgent
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get project task stats: {str(e)}")
    
    def get_tasks_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        Get tasks created within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            List of tasks created in the date range
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Task.query.filter(
                Task.created_at >= start_date,
                Task.created_at <= end_date
            ).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks by date range: {str(e)}")
    
    def get_tasks_due_in_range(self, start_date: datetime, end_date: datetime) -> List[Task]:
        """
        Get tasks with deadlines within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            List of tasks with deadlines in the date range
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return Task.query.filter(
                Task.deadline >= start_date,
                Task.deadline <= end_date
            ).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get tasks due in range: {str(e)}")
