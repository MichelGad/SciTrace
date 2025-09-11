"""
User repository for SciTrace

Provides data access methods for user-related operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from .base_repository import BaseRepository
from ..models import User
from ..exceptions import DatabaseError, ValidationError


class UserRepository(BaseRepository):
    """Repository for user data access operations."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username to search for
        
        Returns:
            User instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_first(username=username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: Email to search for
        
        Returns:
            User instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_first(email=email)
    
    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """
        Get user by username or email.
        
        Args:
            identifier: Username or email to search for
        
        Returns:
            User instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            # Try username first
            user = self.get_by_username(identifier)
            if user:
                return user
            
            # Try email
            return self.get_by_email(identifier)
        except Exception as e:
            raise DatabaseError(f"Failed to get user by identifier: {str(e)}")
    
    def get_admins(self) -> List[User]:
        """
        Get all admin users.
        
        Returns:
            List of admin users
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(role='admin')
    
    def get_regular_users(self) -> List[User]:
        """
        Get all regular users (non-admin).
        
        Returns:
            List of regular users
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(role='user')
    
    def get_active_users(self, days: int = 30) -> List[User]:
        """
        Get users who have logged in within the specified days.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of active users
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            return User.query.filter(User.last_login >= cutoff_date).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get active users: {str(e)}")
    
    def get_users_by_role(self, role: str) -> List[User]:
        """
        Get users by role.
        
        Args:
            role: User role to filter by
        
        Returns:
            List of users with the specified role
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.filter_by_all(role=role)
    
    def create_user(self, username: str, email: str, password_hash: str, name: str, role: str = 'user') -> User:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            password_hash: Hashed password
            name: Full name
            role: User role (default: 'user')
        
        Returns:
            Created user instance
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If validation fails
        """
        # Check if username already exists
        if self.get_by_username(username):
            raise ValidationError(f"Username '{username}' already exists")
        
        # Check if email already exists
        if self.get_by_email(email):
            raise ValidationError(f"Email '{email}' already exists")
        
        return self.create(
            username=username,
            email=email,
            password_hash=password_hash,
            name=name,
            role=role
        )
    
    def update_last_login(self, user_id: int) -> Optional[User]:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
        
        Returns:
            Updated user instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(user_id, last_login=datetime.now(timezone.utc))
    
    def update_password(self, user_id: int, password_hash: str) -> Optional[User]:
        """
        Update user's password.
        
        Args:
            user_id: User ID
            password_hash: New hashed password
        
        Returns:
            Updated user instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
        """
        return self.update(user_id, password_hash=password_hash)
    
    def update_profile(self, user_id: int, name: str = None, email: str = None) -> Optional[User]:
        """
        Update user's profile information.
        
        Args:
            user_id: User ID
            name: New name (optional)
            email: New email (optional)
        
        Returns:
            Updated user instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If email already exists
        """
        update_data = {}
        
        if name is not None:
            update_data['name'] = name
        
        if email is not None:
            # Check if email already exists for another user
            existing_user = self.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise ValidationError(f"Email '{email}' already exists")
            update_data['email'] = email
        
        if update_data:
            return self.update(user_id, **update_data)
        
        return self.get_by_id(user_id)
    
    def change_role(self, user_id: int, new_role: str) -> Optional[User]:
        """
        Change user's role.
        
        Args:
            user_id: User ID
            new_role: New role
        
        Returns:
            Updated user instance or None if not found
        
        Raises:
            DatabaseError: If database operation fails
            ValidationError: If role is invalid
        """
        valid_roles = ['user', 'admin']
        if new_role not in valid_roles:
            raise ValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")
        
        return self.update(user_id, role=new_role)
    
    def search_users(self, search_term: str) -> List[User]:
        """
        Search users by username, email, or name.
        
        Args:
            search_term: Search term
        
        Returns:
            List of matching users
        
        Raises:
            DatabaseError: If database operation fails
        """
        search_fields = ['username', 'email', 'name']
        return self.search(search_term, search_fields)
    
    def get_user_stats(self) -> Dict[str, int]:
        """
        Get user statistics.
        
        Returns:
            Dictionary with user statistics
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            total_users = self.count()
            admin_users = len(self.get_admins())
            regular_users = len(self.get_regular_users())
            active_users = len(self.get_active_users())
            
            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': regular_users,
                'active_users': active_users
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get user stats: {str(e)}")
    
    def get_recent_users(self, limit: int = 10) -> List[User]:
        """
        Get recently created users.
        
        Args:
            limit: Maximum number of users to return
        
        Returns:
            List of recent users
        
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            return User.query.order_by(User.created_at.desc()).limit(limit).all()
        except Exception as e:
            raise DatabaseError(f"Failed to get recent users: {str(e)}")
    
    def is_username_available(self, username: str) -> bool:
        """
        Check if username is available.
        
        Args:
            username: Username to check
        
        Returns:
            True if available, False if taken
        
        Raises:
            DatabaseError: If database operation fails
        """
        return not self.exists(username=username)
    
    def is_email_available(self, email: str) -> bool:
        """
        Check if email is available.
        
        Args:
            email: Email to check
        
        Returns:
            True if available, False if taken
        
        Raises:
            DatabaseError: If database operation fails
        """
        return not self.exists(email=email)
