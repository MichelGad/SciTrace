"""
Validation utilities for SciTrace

Provides standardized form validation utilities to reduce duplicate validation code.
"""

import re
import os
from typing import Dict, List, Any, Optional, Callable, Union
from datetime import datetime, date
from urllib.parse import urlparse
import logging

from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: Dict[str, List[str]] = None):
        self.is_valid = is_valid
        self.errors = errors or {}
    
    def add_error(self, field: str, message: str):
        """Add an error for a specific field."""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
        self.is_valid = False
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return not self.is_valid
    
    def get_error_messages(self) -> List[str]:
        """Get all error messages as a flat list."""
        messages = []
        for field_errors in self.errors.values():
            messages.extend(field_errors)
        return messages
    
    def get_field_errors(self, field: str) -> List[str]:
        """Get errors for a specific field."""
        return self.errors.get(field, [])


class Validator:
    """Base validator class."""
    
    def __init__(self, field_name: str, required: bool = True):
        self.field_name = field_name
        self.required = required
    
    def validate(self, value: Any, data: Dict[str, Any] = None) -> List[str]:
        """
        Validate a value.
        
        Args:
            value: The value to validate
            data: Optional context data for validation
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check if required field is missing
        if self.required and (value is None or value == ''):
            errors.append(f"{self.field_name} is required")
            return errors
        
        # Skip validation if value is empty and not required
        if not self.required and (value is None or value == ''):
            return errors
        
        # Perform specific validation
        specific_errors = self._validate_value(value, data or {})
        errors.extend(specific_errors)
        
        return errors
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        """Override in subclasses to implement specific validation logic."""
        return []


class StringValidator(Validator):
    """Validator for string fields."""
    
    def __init__(self, field_name: str, min_length: int = None, max_length: int = None, 
                 pattern: str = None, required: bool = True):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{self.field_name} must be a string")
            return errors
        
        if self.min_length is not None and len(value) < self.min_length:
            errors.append(f"{self.field_name} must be at least {self.min_length} characters long")
        
        if self.max_length is not None and len(value) > self.max_length:
            errors.append(f"{self.field_name} must be no more than {self.max_length} characters long")
        
        if self.pattern and not re.match(self.pattern, value):
            errors.append(f"{self.field_name} format is invalid")
        
        return errors


class EmailValidator(Validator):
    """Validator for email fields."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{self.field_name} must be a string")
            return errors
        
        if not re.match(self.EMAIL_PATTERN, value):
            errors.append(f"{self.field_name} must be a valid email address")
        
        return errors


class PasswordValidator(Validator):
    """Validator for password fields."""
    
    def __init__(self, field_name: str, min_length: int = 8, require_uppercase: bool = True,
                 require_lowercase: bool = True, require_digits: bool = True, 
                 require_special: bool = True, required: bool = True):
        super().__init__(field_name, required)
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{self.field_name} must be a string")
            return errors
        
        if len(value) < self.min_length:
            errors.append(f"{self.field_name} must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            errors.append(f"{self.field_name} must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', value):
            errors.append(f"{self.field_name} must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', value):
            errors.append(f"{self.field_name} must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append(f"{self.field_name} must contain at least one special character")
        
        return errors


class NumberValidator(Validator):
    """Validator for numeric fields."""
    
    def __init__(self, field_name: str, min_value: float = None, max_value: float = None,
                 integer_only: bool = False, required: bool = True):
        super().__init__(field_name, required)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        # Try to convert to number
        try:
            if self.integer_only:
                num_value = int(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            errors.append(f"{self.field_name} must be a valid number")
            return errors
        
        if self.min_value is not None and num_value < self.min_value:
            errors.append(f"{self.field_name} must be at least {self.min_value}")
        
        if self.max_value is not None and num_value > self.max_value:
            errors.append(f"{self.field_name} must be no more than {self.max_value}")
        
        return errors


class DateValidator(Validator):
    """Validator for date fields."""
    
    def __init__(self, field_name: str, date_format: str = '%Y-%m-%d', 
                 min_date: date = None, max_date: date = None, required: bool = True):
        super().__init__(field_name, required)
        self.date_format = date_format
        self.min_date = min_date
        self.max_date = max_date
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if isinstance(value, str):
            try:
                date_value = datetime.strptime(value, self.date_format).date()
            except ValueError:
                errors.append(f"{self.field_name} must be a valid date in format {self.date_format}")
                return errors
        elif isinstance(value, date):
            date_value = value
        else:
            errors.append(f"{self.field_name} must be a valid date")
            return errors
        
        if self.min_date and date_value < self.min_date:
            errors.append(f"{self.field_name} must be on or after {self.min_date}")
        
        if self.max_date and date_value > self.max_date:
            errors.append(f"{self.field_name} must be on or before {self.max_date}")
        
        return errors


class URLValidator(Validator):
    """Validator for URL fields."""
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{self.field_name} must be a string")
            return errors
        
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                errors.append(f"{self.field_name} must be a valid URL")
        except Exception:
            errors.append(f"{self.field_name} must be a valid URL")
        
        return errors


class FilePathValidator(Validator):
    """Validator for file path fields."""
    
    def __init__(self, field_name: str, must_exist: bool = False, 
                 allowed_extensions: List[str] = None, required: bool = True):
        super().__init__(field_name, required)
        self.must_exist = must_exist
        self.allowed_extensions = allowed_extensions
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if not isinstance(value, str):
            errors.append(f"{self.field_name} must be a string")
            return errors
        
        if self.must_exist and not os.path.exists(value):
            errors.append(f"{self.field_name} must point to an existing file or directory")
        
        if self.allowed_extensions:
            ext = os.path.splitext(value)[1].lower()
            if ext not in self.allowed_extensions:
                errors.append(f"{self.field_name} must have one of these extensions: {', '.join(self.allowed_extensions)}")
        
        return errors


class ChoiceValidator(Validator):
    """Validator for choice fields."""
    
    def __init__(self, field_name: str, choices: List[Any], required: bool = True):
        super().__init__(field_name, required)
        self.choices = choices
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        errors = []
        
        if value not in self.choices:
            errors.append(f"{self.field_name} must be one of: {', '.join(map(str, self.choices))}")
        
        return errors


class CustomValidator(Validator):
    """Validator with custom validation function."""
    
    def __init__(self, field_name: str, validation_func: Callable[[Any, Dict[str, Any]], List[str]], 
                 required: bool = True):
        super().__init__(field_name, required)
        self.validation_func = validation_func
    
    def _validate_value(self, value: Any, data: Dict[str, Any]) -> List[str]:
        try:
            return self.validation_func(value, data)
        except Exception as e:
            logger.error(f"Custom validation error for {self.field_name}: {e}")
            return [f"Validation error for {self.field_name}"]


class FormValidator:
    """Main form validation class."""
    
    def __init__(self):
        self.validators: Dict[str, List[Validator]] = {}
    
    def add_validator(self, field_name: str, validator: Validator):
        """Add a validator for a field."""
        if field_name not in self.validators:
            self.validators[field_name] = []
        self.validators[field_name].append(validator)
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate form data.
        
        Args:
            data: Dictionary of form data to validate
        
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        for field_name, validators in self.validators.items():
            value = data.get(field_name)
            
            for validator in validators:
                errors = validator.validate(value, data)
                for error in errors:
                    result.add_error(field_name, error)
        
        return result
    
    def validate_field(self, field_name: str, value: Any, data: Dict[str, Any] = None) -> List[str]:
        """
        Validate a single field.
        
        Args:
            field_name: Name of the field to validate
            value: Value to validate
            data: Optional context data
        
        Returns:
            List of error messages
        """
        errors = []
        
        if field_name in self.validators:
            for validator in self.validators[field_name]:
                field_errors = validator.validate(value, data or {})
                errors.extend(field_errors)
        
        return errors


# Predefined validation schemas
class ValidationSchemas:
    """Predefined validation schemas for common forms."""
    
    @staticmethod
    def user_registration() -> FormValidator:
        """Validation schema for user registration."""
        validator = FormValidator()
        
        validator.add_validator('username', StringValidator('username', min_length=3, max_length=50))
        validator.add_validator('email', EmailValidator('email'))
        validator.add_validator('name', StringValidator('name', min_length=2, max_length=100))
        validator.add_validator('password', PasswordValidator('password'))
        validator.add_validator('confirm_password', StringValidator('confirm_password'))
        
        # Custom validator for password confirmation
        def validate_password_confirmation(value, data):
            if value != data.get('password'):
                return ['Passwords do not match']
            return []
        
        validator.add_validator('confirm_password', CustomValidator('confirm_password', validate_password_confirmation))
        
        return validator
    
    @staticmethod
    def project_creation() -> FormValidator:
        """Validation schema for project creation."""
        validator = FormValidator()
        
        validator.add_validator('name', StringValidator('name', min_length=3, max_length=100))
        validator.add_validator('description', StringValidator('description', max_length=500, required=False))
        validator.add_validator('research_type', ChoiceValidator('research_type', 
                                                               ['general', 'environmental', 'biomedical', 'computational']))
        
        return validator
    
    @staticmethod
    def task_creation() -> FormValidator:
        """Validation schema for task creation."""
        validator = FormValidator()
        
        validator.add_validator('title', StringValidator('title', min_length=3, max_length=200))
        validator.add_validator('description', StringValidator('description', max_length=1000, required=False))
        validator.add_validator('priority', ChoiceValidator('priority', ['low', 'medium', 'high', 'urgent']))
        validator.add_validator('status', ChoiceValidator('status', ['pending', 'ongoing', 'done']))
        
        return validator
    
    @staticmethod
    def dataflow_creation() -> FormValidator:
        """Validation schema for dataflow creation."""
        validator = FormValidator()
        
        validator.add_validator('name', StringValidator('name', min_length=3, max_length=100))
        validator.add_validator('description', StringValidator('description', max_length=500, required=False))
        validator.add_validator('workflow_type', ChoiceValidator('workflow_type', 
                                                               ['linear', 'parallel', 'spider_web', 'custom']))
        
        return validator


# Utility functions
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present.
    
    Args:
        data: Data to validate
        required_fields: List of required field names
    
    Returns:
        List of error messages
    """
    errors = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            errors.append(f"{field} is required")
    
    return errors


def validate_field_length(value: str, field_name: str, min_length: int = None, 
                         max_length: int = None) -> List[str]:
    """
    Validate field length.
    
    Args:
        value: Value to validate
        field_name: Name of the field
        min_length: Minimum length
        max_length: Maximum length
    
    Returns:
        List of error messages
    """
    errors = []
    
    if not isinstance(value, str):
        errors.append(f"{field_name} must be a string")
        return errors
    
    if min_length is not None and len(value) < min_length:
        errors.append(f"{field_name} must be at least {min_length} characters long")
    
    if max_length is not None and len(value) > max_length:
        errors.append(f"{field_name} must be no more than {max_length} characters long")
    
    return errors


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_input(value: str, max_length: int = None) -> str:
    """
    Sanitize user input.
    
    Args:
        value: Input value to sanitize
        max_length: Maximum length to truncate to
    
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return str(value)
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    # Truncate if too long
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
