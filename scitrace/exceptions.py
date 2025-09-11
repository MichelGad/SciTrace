"""
Custom exceptions for SciTrace

Provides specific exception classes for better error handling and debugging.
"""


class SciTraceException(Exception):
    """Base exception class for all SciTrace-specific exceptions."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SciTraceException):
    """Exception raised when validation fails."""
    
    def __init__(self, message: str, field: str = None, value: any = None, details: dict = None):
        self.field = field
        self.value = value
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            details=details or {}
        )


class AuthenticationError(SciTraceException):
    """Exception raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(
            message=message,
            error_code='AUTHENTICATION_ERROR',
            details=details or {}
        )


class AuthorizationError(SciTraceException):
    """Exception raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", resource: str = None, details: dict = None):
        self.resource = resource
        super().__init__(
            message=message,
            error_code='AUTHORIZATION_ERROR',
            details=details or {}
        )


class ProjectError(SciTraceException):
    """Exception raised for project-related errors."""
    
    def __init__(self, message: str, project_id: str = None, details: dict = None):
        self.project_id = project_id
        super().__init__(
            message=message,
            error_code='PROJECT_ERROR',
            details=details or {}
        )


class TaskError(SciTraceException):
    """Exception raised for task-related errors."""
    
    def __init__(self, message: str, task_id: str = None, details: dict = None):
        self.task_id = task_id
        super().__init__(
            message=message,
            error_code='TASK_ERROR',
            details=details or {}
        )


class DataflowError(SciTraceException):
    """Exception raised for dataflow-related errors."""
    
    def __init__(self, message: str, dataflow_id: str = None, details: dict = None):
        self.dataflow_id = dataflow_id
        super().__init__(
            message=message,
            error_code='DATAFLOW_ERROR',
            details=details or {}
        )


class DataLadError(SciTraceException):
    """Exception raised for DataLad-related errors."""
    
    def __init__(self, message: str, command: list = None, returncode: int = None, 
                 stdout: str = "", stderr: str = "", details: dict = None):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            message=message,
            error_code='DATALAD_ERROR',
            details=details or {}
        )


class DatasetError(SciTraceException):
    """Exception raised for dataset-related errors."""
    
    def __init__(self, message: str, dataset_path: str = None, details: dict = None):
        self.dataset_path = dataset_path
        super().__init__(
            message=message,
            error_code='DATASET_ERROR',
            details=details or {}
        )


class FileOperationError(SciTraceException):
    """Exception raised for file operation errors."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None, details: dict = None):
        self.file_path = file_path
        self.operation = operation
        super().__init__(
            message=message,
            error_code='FILE_OPERATION_ERROR',
            details=details or {}
        )


class GitOperationError(SciTraceException):
    """Exception raised for Git operation errors."""
    
    def __init__(self, message: str, command: list = None, returncode: int = None,
                 stdout: str = "", stderr: str = "", details: dict = None):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(
            message=message,
            error_code='GIT_OPERATION_ERROR',
            details=details or {}
        )


class ConfigurationError(SciTraceException):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        self.config_key = config_key
        super().__init__(
            message=message,
            error_code='CONFIGURATION_ERROR',
            details=details or {}
        )


class DatabaseError(SciTraceException):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, operation: str = None, table: str = None, details: dict = None):
        self.operation = operation
        self.table = table
        super().__init__(
            message=message,
            error_code='DATABASE_ERROR',
            details=details or {}
        )


class ServiceError(SciTraceException):
    """Exception raised for service-related errors."""
    
    def __init__(self, message: str, service_name: str = None, details: dict = None):
        self.service_name = service_name
        super().__init__(
            message=message,
            error_code='SERVICE_ERROR',
            details=details or {}
        )


class ExternalServiceError(SciTraceException):
    """Exception raised for external service errors."""
    
    def __init__(self, message: str, service_name: str = None, status_code: int = None, details: dict = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(
            message=message,
            error_code='EXTERNAL_SERVICE_ERROR',
            details=details or {}
        )


class ResourceNotFoundError(SciTraceException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, details: dict = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message,
            error_code='RESOURCE_NOT_FOUND',
            details=details or {}
        )


class ResourceConflictError(SciTraceException):
    """Exception raised when there's a conflict with a resource."""
    
    def __init__(self, message: str, resource_type: str = None, resource_id: str = None, details: dict = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message,
            error_code='RESOURCE_CONFLICT',
            details=details or {}
        )


class RateLimitError(SciTraceException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: dict = None):
        self.retry_after = retry_after
        super().__init__(
            message=message,
            error_code='RATE_LIMIT_EXCEEDED',
            details=details or {}
        )


class TimeoutError(SciTraceException):
    """Exception raised when an operation times out."""
    
    def __init__(self, message: str, timeout_seconds: int = None, operation: str = None, details: dict = None):
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        super().__init__(
            message=message,
            error_code='TIMEOUT_ERROR',
            details=details or {}
        )


class NetworkError(SciTraceException):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, url: str = None, status_code: int = None, details: dict = None):
        self.url = url
        self.status_code = status_code
        super().__init__(
            message=message,
            error_code='NETWORK_ERROR',
            details=details or {}
        )


class SerializationError(SciTraceException):
    """Exception raised for serialization/deserialization errors."""
    
    def __init__(self, message: str, data_type: str = None, details: dict = None):
        self.data_type = data_type
        super().__init__(
            message=message,
            error_code='SERIALIZATION_ERROR',
            details=details or {}
        )


class CacheError(SciTraceException):
    """Exception raised for cache-related errors."""
    
    def __init__(self, message: str, cache_key: str = None, operation: str = None, details: dict = None):
        self.cache_key = cache_key
        self.operation = operation
        super().__init__(
            message=message,
            error_code='CACHE_ERROR',
            details=details or {}
        )


class LoggingError(SciTraceException):
    """Exception raised for logging-related errors."""
    
    def __init__(self, message: str, logger_name: str = None, details: dict = None):
        self.logger_name = logger_name
        super().__init__(
            message=message,
            error_code='LOGGING_ERROR',
            details=details or {}
        )


# Exception mapping for error handling
EXCEPTION_MAPPING = {
    ValidationError: {'status_code': 422, 'error_code': 'VALIDATION_ERROR'},
    AuthenticationError: {'status_code': 401, 'error_code': 'AUTHENTICATION_ERROR'},
    AuthorizationError: {'status_code': 403, 'error_code': 'AUTHORIZATION_ERROR'},
    ProjectError: {'status_code': 400, 'error_code': 'PROJECT_ERROR'},
    TaskError: {'status_code': 400, 'error_code': 'TASK_ERROR'},
    DataflowError: {'status_code': 400, 'error_code': 'DATAFLOW_ERROR'},
    DataLadError: {'status_code': 500, 'error_code': 'DATALAD_ERROR'},
    DatasetError: {'status_code': 400, 'error_code': 'DATASET_ERROR'},
    FileOperationError: {'status_code': 400, 'error_code': 'FILE_OPERATION_ERROR'},
    GitOperationError: {'status_code': 500, 'error_code': 'GIT_OPERATION_ERROR'},
    ConfigurationError: {'status_code': 500, 'error_code': 'CONFIGURATION_ERROR'},
    DatabaseError: {'status_code': 500, 'error_code': 'DATABASE_ERROR'},
    ServiceError: {'status_code': 500, 'error_code': 'SERVICE_ERROR'},
    ExternalServiceError: {'status_code': 502, 'error_code': 'EXTERNAL_SERVICE_ERROR'},
    ResourceNotFoundError: {'status_code': 404, 'error_code': 'RESOURCE_NOT_FOUND'},
    ResourceConflictError: {'status_code': 409, 'error_code': 'RESOURCE_CONFLICT'},
    RateLimitError: {'status_code': 429, 'error_code': 'RATE_LIMIT_EXCEEDED'},
    TimeoutError: {'status_code': 408, 'error_code': 'TIMEOUT_ERROR'},
    NetworkError: {'status_code': 502, 'error_code': 'NETWORK_ERROR'},
    SerializationError: {'status_code': 400, 'error_code': 'SERIALIZATION_ERROR'},
    CacheError: {'status_code': 500, 'error_code': 'CACHE_ERROR'},
    LoggingError: {'status_code': 500, 'error_code': 'LOGGING_ERROR'},
}


def get_exception_info(exception: SciTraceException) -> dict:
    """
    Get standardized information from a SciTrace exception.
    
    Args:
        exception: The SciTrace exception instance
    
    Returns:
        Dict containing exception information
    """
    exception_type = type(exception)
    mapping = EXCEPTION_MAPPING.get(exception_type, {
        'status_code': 500,
        'error_code': 'UNKNOWN_ERROR'
    })
    
    return {
        'message': exception.message,
        'error_code': exception.error_code or mapping['error_code'],
        'status_code': mapping['status_code'],
        'details': exception.details,
        'exception_type': exception_type.__name__
    }
