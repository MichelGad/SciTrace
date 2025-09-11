"""
Flash message utilities for SciTrace

Provides standardized flash message handling and user feedback patterns.
"""

from typing import Dict, List, Any, Optional, Union
from flask import flash, session, request
from datetime import datetime
import json
import logging

from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


class FlashMessage:
    """Represents a flash message with metadata."""
    
    def __init__(self, message: str, category: str = 'info', title: str = None, 
                 dismissible: bool = True, auto_hide: bool = False, 
                 auto_hide_delay: int = 5000, data: Dict[str, Any] = None):
        """
        Initialize a flash message.
        
        Args:
            message: The message content
            category: Message category (success, error, warning, info)
            title: Optional message title
            dismissible: Whether the message can be dismissed
            auto_hide: Whether the message should auto-hide
            auto_hide_delay: Auto-hide delay in milliseconds
            data: Additional data for the message
        """
        self.message = message
        self.category = category
        self.title = title
        self.dismissible = dismissible
        self.auto_hide = auto_hide
        self.auto_hide_delay = auto_hide_delay
        self.data = data or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"flash_{hash(message + category + str(datetime.now()))}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert flash message to dictionary."""
        return {
            'id': self.id,
            'message': self.message,
            'category': self.category,
            'title': self.title,
            'dismissible': self.dismissible,
            'auto_hide': self.auto_hide,
            'auto_hide_delay': self.auto_hide_delay,
            'data': self.data,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlashMessage':
        """Create flash message from dictionary."""
        return cls(
            message=data['message'],
            category=data.get('category', 'info'),
            title=data.get('title'),
            dismissible=data.get('dismissible', True),
            auto_hide=data.get('auto_hide', False),
            auto_hide_delay=data.get('auto_hide_delay', 5000),
            data=data.get('data', {})
        )


class FlashManager:
    """Manages flash messages with enhanced functionality."""
    
    # Standard message categories
    CATEGORIES = {
        'success': {'icon': 'check-circle', 'color': 'green', 'auto_hide': True},
        'error': {'icon': 'exclamation-circle', 'color': 'red', 'auto_hide': False},
        'warning': {'icon': 'exclamation-triangle', 'color': 'yellow', 'auto_hide': True},
        'info': {'icon': 'info-circle', 'color': 'blue', 'auto_hide': True},
        'primary': {'icon': 'star', 'color': 'blue', 'auto_hide': True},
        'secondary': {'icon': 'circle', 'color': 'gray', 'auto_hide': True}
    }
    
    def __init__(self):
        self.session_key = '_flash_messages'
    
    def add_message(self, message: str, category: str = 'info', **kwargs) -> str:
        """
        Add a flash message.
        
        Args:
            message: The message content
            category: Message category
            **kwargs: Additional message options
        
        Returns:
            Message ID
        """
        # Validate category
        if category not in self.CATEGORIES:
            logger.warning(f"Unknown flash message category: {category}")
            category = 'info'
        
        # Get category defaults
        category_config = self.CATEGORIES[category]
        
        # Create flash message
        flash_msg = FlashMessage(
            message=message,
            category=category,
            auto_hide=kwargs.get('auto_hide', category_config['auto_hide']),
            **kwargs
        )
        
        # Store in session
        messages = self.get_messages()
        messages.append(flash_msg.to_dict())
        session[self.session_key] = messages
        
        # Also use Flask's built-in flash for backward compatibility
        flash(message, category)
        
        logger.debug(f"Added flash message: {category} - {message}")
        return flash_msg.id
    
    def get_messages(self, category: str = None, consume: bool = True) -> List[Dict[str, Any]]:
        """
        Get flash messages.
        
        Args:
            category: Optional category filter
            consume: Whether to remove messages after getting them
        
        Returns:
            List of flash message dictionaries
        """
        messages = session.get(self.session_key, [])
        
        # Filter by category if specified
        if category:
            messages = [msg for msg in messages if msg.get('category') == category]
        
        # Remove messages if consuming
        if consume:
            session.pop(self.session_key, None)
        
        return messages
    
    def get_messages_by_category(self, consume: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get flash messages grouped by category.
        
        Args:
            consume: Whether to remove messages after getting them
        
        Returns:
            Dictionary with categories as keys and message lists as values
        """
        messages = self.get_messages(consume=consume)
        
        grouped = {}
        for msg in messages:
            category = msg.get('category', 'info')
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(msg)
        
        return grouped
    
    def clear_messages(self):
        """Clear all flash messages."""
        session.pop(self.session_key, None)
        logger.debug("Cleared all flash messages")
    
    def has_messages(self, category: str = None) -> bool:
        """
        Check if there are any flash messages.
        
        Args:
            category: Optional category filter
        
        Returns:
            True if messages exist, False otherwise
        """
        messages = self.get_messages(consume=False)
        
        if category:
            return any(msg.get('category') == category for msg in messages)
        
        return len(messages) > 0
    
    def success(self, message: str, **kwargs) -> str:
        """Add a success message."""
        return self.add_message(message, 'success', **kwargs)
    
    def error(self, message: str, **kwargs) -> str:
        """Add an error message."""
        return self.add_message(message, 'error', **kwargs)
    
    def warning(self, message: str, **kwargs) -> str:
        """Add a warning message."""
        return self.add_message(message, 'warning', **kwargs)
    
    def info(self, message: str, **kwargs) -> str:
        """Add an info message."""
        return self.add_message(message, 'info', **kwargs)
    
    def primary(self, message: str, **kwargs) -> str:
        """Add a primary message."""
        return self.add_message(message, 'primary', **kwargs)
    
    def secondary(self, message: str, **kwargs) -> str:
        """Add a secondary message."""
        return self.add_message(message, 'secondary', **kwargs)


# Global flash manager instance
flash_manager = FlashManager()


# Convenience functions
def flash_success(message: str, **kwargs) -> str:
    """Flash a success message."""
    return flash_manager.success(message, **kwargs)


def flash_error(message: str, **kwargs) -> str:
    """Flash an error message."""
    return flash_manager.error(message, **kwargs)


def flash_warning(message: str, **kwargs) -> str:
    """Flash a warning message."""
    return flash_manager.warning(message, **kwargs)


def flash_info(message: str, **kwargs) -> str:
    """Flash an info message."""
    return flash_manager.info(message, **kwargs)


def flash_primary(message: str, **kwargs) -> str:
    """Flash a primary message."""
    return flash_manager.primary(message, **kwargs)


def flash_secondary(message: str, **kwargs) -> str:
    """Flash a secondary message."""
    return flash_manager.secondary(message, **kwargs)


def flash_validation_errors(errors: Dict[str, List[str]], title: str = "Validation Errors"):
    """
    Flash validation errors.
    
    Args:
        errors: Dictionary of field errors
        title: Error title
    """
    if not errors:
        return
    
    # Create error message
    error_parts = []
    for field, field_errors in errors.items():
        for error in field_errors:
            error_parts.append(f"{field}: {error}")
    
    error_message = "\\n".join(error_parts)
    
    flash_manager.error(
        error_message,
        title=title,
        data={'validation_errors': errors}
    )


def flash_form_errors(form):
    """
    Flash form validation errors.
    
    Args:
        form: WTForms form instance
    """
    if form.errors:
        flash_validation_errors(form.errors)


def flash_exception(exception: Exception, title: str = "An Error Occurred"):
    """
    Flash an exception message.
    
    Args:
        exception: Exception instance
        title: Error title
    """
    # Get user-friendly error message
    if hasattr(exception, 'message'):
        message = exception.message
    elif hasattr(exception, 'args') and exception.args:
        message = str(exception.args[0])
    else:
        message = str(exception)
    
    # Add additional context for specific exception types
    data = {}
    if hasattr(exception, 'error_code'):
        data['error_code'] = exception.error_code
    if hasattr(exception, 'details'):
        data['details'] = exception.details
    
    flash_manager.error(
        message,
        title=title,
        data=data
    )


def flash_api_response(response_data: Dict[str, Any], success_message: str = None):
    """
    Flash messages based on API response.
    
    Args:
        response_data: API response data
        success_message: Custom success message
    """
    if response_data.get('success'):
        message = success_message or response_data.get('message', 'Operation completed successfully')
        flash_manager.success(message, data=response_data)
    else:
        error_message = response_data.get('error', {}).get('message', 'An error occurred')
        flash_manager.error(error_message, data=response_data)


def flash_operation_result(operation: str, success: bool, details: str = None, 
                          resource_name: str = None):
    """
    Flash operation result message.
    
    Args:
        operation: Operation name (e.g., 'created', 'updated', 'deleted')
        success: Whether operation was successful
        details: Additional details
        resource_name: Name of the resource
    """
    if success:
        if resource_name:
            message = f"{resource_name} {operation} successfully"
        else:
            message = f"Operation {operation} completed successfully"
        
        if details:
            message += f": {details}"
        
        flash_manager.success(message)
    else:
        if resource_name:
            message = f"Failed to {operation} {resource_name}"
        else:
            message = f"Operation {operation} failed"
        
        if details:
            message += f": {details}"
        
        flash_manager.error(message)


def flash_file_operation(operation: str, file_path: str, success: bool, 
                        details: str = None):
    """
    Flash file operation result.
    
    Args:
        operation: File operation (uploaded, downloaded, deleted, etc.)
        file_path: File path
        success: Whether operation was successful
        details: Additional details
    """
    filename = file_path.split('/')[-1] if '/' in file_path else file_path
    
    if success:
        message = f"File '{filename}' {operation} successfully"
        if details:
            message += f": {details}"
        flash_manager.success(message, data={'file_path': file_path})
    else:
        message = f"Failed to {operation} file '{filename}'"
        if details:
            message += f": {details}"
        flash_manager.error(message, data={'file_path': file_path})


def flash_datalad_operation(operation: str, dataset_name: str, success: bool, 
                           details: str = None):
    """
    Flash DataLad operation result.
    
    Args:
        operation: DataLad operation
        dataset_name: Dataset name
        success: Whether operation was successful
        details: Additional details
    """
    if success:
        message = f"DataLad {operation} completed for dataset '{dataset_name}'"
        if details:
            message += f": {details}"
        flash_manager.success(message, data={'dataset_name': dataset_name, 'operation': operation})
    else:
        message = f"DataLad {operation} failed for dataset '{dataset_name}'"
        if details:
            message += f": {details}"
        flash_manager.error(message, data={'dataset_name': dataset_name, 'operation': operation})


def flash_user_action(action: str, resource_type: str, success: bool, 
                     resource_name: str = None, details: str = None):
    """
    Flash user action result.
    
    Args:
        action: User action (created, updated, deleted, etc.)
        resource_type: Type of resource
        success: Whether action was successful
        resource_name: Name of the resource
        details: Additional details
    """
    if success:
        if resource_name:
            message = f"{resource_type.title()} '{resource_name}' {action} successfully"
        else:
            message = f"{resource_type.title()} {action} successfully"
        
        if details:
            message += f": {details}"
        
        flash_manager.success(message, data={
            'action': action,
            'resource_type': resource_type,
            'resource_name': resource_name
        })
    else:
        if resource_name:
            message = f"Failed to {action} {resource_type} '{resource_name}'"
        else:
            message = f"Failed to {action} {resource_type}"
        
        if details:
            message += f": {details}"
        
        flash_manager.error(message, data={
            'action': action,
            'resource_type': resource_type,
            'resource_name': resource_name
        })


def get_flash_messages(category: str = None, consume: bool = True) -> List[Dict[str, Any]]:
    """
    Get flash messages.
    
    Args:
        category: Optional category filter
        consume: Whether to remove messages after getting them
    
    Returns:
        List of flash message dictionaries
    """
    return flash_manager.get_messages(category=category, consume=consume)


def get_flash_messages_by_category(consume: bool = True) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get flash messages grouped by category.
    
    Args:
        consume: Whether to remove messages after getting them
    
    Returns:
        Dictionary with categories as keys and message lists as values
    """
    return flash_manager.get_messages_by_category(consume=consume)


def clear_flash_messages():
    """Clear all flash messages."""
    flash_manager.clear_messages()


def has_flash_messages(category: str = None) -> bool:
    """
    Check if there are any flash messages.
    
    Args:
        category: Optional category filter
    
    Returns:
        True if messages exist, False otherwise
    """
    return flash_manager.has_messages(category=category)


# Template context processor
def flash_messages_context():
    """
    Template context processor for flash messages.
    
    Returns:
        Dictionary with flash message data for templates
    """
    return {
        'flash_messages': get_flash_messages(consume=False),
        'flash_messages_by_category': get_flash_messages_by_category(consume=False),
        'has_flash_messages': has_flash_messages(),
        'flash_categories': FlashManager.CATEGORIES
    }
