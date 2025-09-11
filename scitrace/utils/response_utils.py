"""
Response utilities for SciTrace

Provides standardized response formats for API endpoints.
"""

from flask import jsonify, Response
from typing import Dict, Any, Optional, Union
import traceback
import logging


# Configure logging
logger = logging.getLogger(__name__)


class APIResponse:
    """Standardized API response class."""
    
    @staticmethod
    def success(data: Any = None, message: str = None, status_code: int = 200) -> Response:
        """
        Create a standardized success response.
        
        Args:
            data: The response data
            message: Optional success message
            status_code: HTTP status code (default: 200)
        
        Returns:
            Flask Response object
        """
        response = {
            'success': True,
            'status': 'success'
        }
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str, 
        error_code: str = None, 
        details: Any = None, 
        status_code: int = 400,
        exception: Exception = None
    ) -> Response:
        """
        Create a standardized error response.
        
        Args:
            message: Error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
            status_code: HTTP status code (default: 400)
            exception: Optional exception object for logging
        
        Returns:
            Flask Response object
        """
        response = {
            'success': False,
            'status': 'error',
            'error': {
                'message': message
            }
        }
        
        if error_code:
            response['error']['code'] = error_code
        
        if details:
            response['error']['details'] = details
        
        # Log the error if an exception is provided
        if exception:
            logger.error(f"API Error: {message}", exc_info=exception)
        
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(
        errors: Dict[str, Any], 
        message: str = "Validation failed"
    ) -> Response:
        """
        Create a standardized validation error response.
        
        Args:
            errors: Dictionary of validation errors
            message: Error message
        
        Returns:
            Flask Response object
        """
        return APIResponse.error(
            message=message,
            error_code='VALIDATION_ERROR',
            details={'validation_errors': errors},
            status_code=422
        )
    
    @staticmethod
    def not_found(
        resource: str = "Resource", 
        resource_id: str = None
    ) -> Response:
        """
        Create a standardized not found response.
        
        Args:
            resource: The type of resource that was not found
            resource_id: Optional ID of the resource
        
        Returns:
            Flask Response object
        """
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        return APIResponse.error(
            message=message,
            error_code='NOT_FOUND',
            status_code=404
        )
    
    @staticmethod
    def forbidden(
        message: str = "Access denied"
    ) -> Response:
        """
        Create a standardized forbidden response.
        
        Args:
            message: Error message
        
        Returns:
            Flask Response object
        """
        return APIResponse.error(
            message=message,
            error_code='FORBIDDEN',
            status_code=403
        )
    
    @staticmethod
    def unauthorized(
        message: str = "Authentication required"
    ) -> Response:
        """
        Create a standardized unauthorized response.
        
        Args:
            message: Error message
        
        Returns:
            Flask Response object
        """
        return APIResponse.error(
            message=message,
            error_code='UNAUTHORIZED',
            status_code=401
        )
    
    @staticmethod
    def internal_error(
        message: str = "Internal server error",
        exception: Exception = None
    ) -> Response:
        """
        Create a standardized internal server error response.
        
        Args:
            message: Error message
            exception: Optional exception object for logging
        
        Returns:
            Flask Response object
        """
        return APIResponse.error(
            message=message,
            error_code='INTERNAL_ERROR',
            status_code=500,
            exception=exception
        )
    
    @staticmethod
    def method_not_allowed(
        method: str = None,
        allowed_methods: list = None
    ) -> Response:
        """
        Create a standardized method not allowed response.
        
        Args:
            method: The method that was not allowed
            allowed_methods: List of allowed methods
        
        Returns:
            Flask Response object
        """
        message = "Method not allowed"
        if method:
            message += f" ({method})"
        
        details = None
        if allowed_methods:
            details = {'allowed_methods': allowed_methods}
        
        return APIResponse.error(
            message=message,
            error_code='METHOD_NOT_ALLOWED',
            details=details,
            status_code=405
        )
    
    @staticmethod
    def rate_limited(
        message: str = "Rate limit exceeded",
        retry_after: int = None
    ) -> Response:
        """
        Create a standardized rate limit exceeded response.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        
        Returns:
            Flask Response object
        """
        details = None
        if retry_after:
            details = {'retry_after': retry_after}
        
        return APIResponse.error(
            message=message,
            error_code='RATE_LIMITED',
            details=details,
            status_code=429
        )


class PaginatedResponse:
    """Utility for creating paginated responses."""
    
    @staticmethod
    def create(
        data: list,
        page: int,
        per_page: int,
        total: int,
        message: str = None
    ) -> Response:
        """
        Create a paginated response.
        
        Args:
            data: List of items for the current page
            page: Current page number
            per_page: Number of items per page
            total: Total number of items
            message: Optional message
        
        Returns:
            Flask Response object
        """
        total_pages = (total + per_page - 1) // per_page
        
        response_data = {
            'items': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
        return APIResponse.success(
            data=response_data,
            message=message
        )


def handle_exception(exception: Exception, context: str = None) -> Response:
    """
    Handle exceptions and return standardized error responses.
    
    Args:
        exception: The exception that occurred
        context: Optional context information
    
    Returns:
        Flask Response object
    """
    # Log the full exception
    logger.error(f"Exception in {context or 'unknown context'}: {str(exception)}", 
                 exc_info=exception)
    
    # Handle specific exception types
    if isinstance(exception, ValueError):
        return APIResponse.error(
            message=str(exception),
            error_code='INVALID_VALUE',
            status_code=400,
            exception=exception
        )
    
    elif isinstance(exception, PermissionError):
        return APIResponse.forbidden(
            message=str(exception)
        )
    
    elif isinstance(exception, FileNotFoundError):
        return APIResponse.not_found(
            resource="File",
            resource_id=str(exception)
        )
    
    elif isinstance(exception, KeyError):
        return APIResponse.error(
            message=f"Missing required field: {str(exception)}",
            error_code='MISSING_FIELD',
            status_code=400,
            exception=exception
        )
    
    else:
        # Generic internal server error for unhandled exceptions
        return APIResponse.internal_error(
            message="An unexpected error occurred",
            exception=exception
        )


def validate_json_request(required_fields: list = None, optional_fields: list = None) -> Dict[str, Any]:
    """
    Validate JSON request data.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
    
    Returns:
        Dict containing the validated data
    
    Raises:
        ValueError: If validation fails
    """
    from flask import request
    
    if not request.is_json:
        raise ValueError("Request must be JSON")
    
    data = request.get_json()
    if not data:
        raise ValueError("Request body is empty")
    
    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Check for unknown fields (if optional_fields is specified)
    if optional_fields:
        all_allowed_fields = set(required_fields or []) | set(optional_fields or [])
        unknown_fields = [field for field in data.keys() if field not in all_allowed_fields]
        if unknown_fields:
            raise ValueError(f"Unknown fields: {', '.join(unknown_fields)}")
    
    return data


def create_error_handler(app):
    """
    Register global error handlers for the Flask app.
    
    Args:
        app: Flask application instance
    """
    @app.errorhandler(400)
    def bad_request(error):
        return APIResponse.error(
            message="Bad request",
            error_code='BAD_REQUEST',
            status_code=400
        )
    
    @app.errorhandler(401)
    def unauthorized(error):
        return APIResponse.unauthorized()
    
    @app.errorhandler(403)
    def forbidden(error):
        return APIResponse.forbidden()
    
    @app.errorhandler(404)
    def not_found(error):
        return APIResponse.not_found()
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return APIResponse.method_not_allowed()
    
    @app.errorhandler(429)
    def rate_limited(error):
        return APIResponse.rate_limited()
    
    @app.errorhandler(500)
    def internal_error(error):
        return APIResponse.internal_error()
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return handle_exception(error, "global error handler")
