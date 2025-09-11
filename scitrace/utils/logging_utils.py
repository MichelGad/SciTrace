"""
Logging utilities for SciTrace

Provides consistent logging configuration and utilities throughout the application.
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import json
import traceback
from functools import wraps

from ..exceptions import LoggingError


class SciTraceFormatter(logging.Formatter):
    """Custom formatter for SciTrace logs."""
    
    def __init__(self, include_context: bool = True):
        """
        Initialize the formatter.
        
        Args:
            include_context: Whether to include context information in logs
        """
        self.include_context = include_context
        
        # Base format
        base_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        
        # Extended format with context
        if include_context:
            base_format += ' | %(context)s'
        
        super().__init__(base_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        """Format the log record."""
        # Add context information if available
        if self.include_context and hasattr(record, 'context'):
            if isinstance(record.context, dict):
                record.context = json.dumps(record.context, default=str)
            else:
                record.context = str(record.context)
        else:
            record.context = ''
        
        return super().format(record)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""
    
    def __init__(self, context: Dict[str, Any] = None):
        """
        Initialize the context filter.
        
        Args:
            context: Default context information
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record):
        """Add context to the log record."""
        record.context = self.context.copy()
        
        # Add request information if available
        try:
            from flask import request, g
            if request:
                record.context.update({
                    'request_id': getattr(g, 'request_id', None),
                    'user_id': getattr(g, 'user_id', None),
                    'endpoint': request.endpoint,
                    'method': request.method,
                    'remote_addr': request.remote_addr
                })
        except ImportError:
            pass  # Flask not available
        
        return True


class LoggingManager:
    """Centralized logging manager for SciTrace."""
    
    def __init__(self):
        self.loggers: Dict[str, logging.Logger] = {}
        self.handlers: Dict[str, logging.Handler] = {}
        self.initialized = False
    
    def setup_logging(
        self,
        log_level: str = 'INFO',
        log_file: str = 'scitrace.log',
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
        include_context: bool = True
    ):
        """
        Set up logging configuration.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Log file path
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            console_output: Whether to output to console
            include_context: Whether to include context in logs
        """
        try:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file) if os.path.dirname(log_file) else 'logs'
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Set root logger level
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, log_level.upper()))
            
            # Clear existing handlers
            root_logger.handlers.clear()
            
            # Create formatter
            formatter = SciTraceFormatter(include_context=include_context)
            
            # File handler with rotation
            if log_file:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setFormatter(formatter)
                file_handler.addFilter(ContextFilter())
                root_logger.addHandler(file_handler)
                self.handlers['file'] = file_handler
            
            # Console handler
            if console_output:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(formatter)
                console_handler.addFilter(ContextFilter())
                root_logger.addHandler(console_handler)
                self.handlers['console'] = console_handler
            
            # Set specific logger levels
            self._configure_logger_levels()
            
            self.initialized = True
            
            # Log initialization
            logger = self.get_logger(__name__)
            logger.info("Logging system initialized", extra={
                'context': {
                    'log_level': log_level,
                    'log_file': log_file,
                    'console_output': console_output,
                    'include_context': include_context
                }
            })
            
        except Exception as e:
            raise LoggingError(f"Failed to setup logging: {str(e)}")
    
    def _configure_logger_levels(self):
        """Configure specific logger levels."""
        # Reduce noise from third-party libraries
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('git').setLevel(logging.WARNING)
        
        # Set SciTrace loggers to DEBUG for development
        if os.environ.get('FLASK_ENV') == 'development':
            logging.getLogger('scitrace').setLevel(logging.DEBUG)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance.
        
        Args:
            name: Logger name
        
        Returns:
            Logger instance
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def add_handler(self, name: str, handler: logging.Handler):
        """
        Add a custom handler.
        
        Args:
            name: Handler name
            handler: Handler instance
        """
        self.handlers[name] = handler
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
    
    def remove_handler(self, name: str):
        """
        Remove a handler.
        
        Args:
            name: Handler name
        """
        if name in self.handlers:
            handler = self.handlers[name]
            root_logger = logging.getLogger()
            root_logger.removeHandler(handler)
            del self.handlers[name]
    
    def set_level(self, level: str):
        """
        Set the logging level.
        
        Args:
            level: Logging level
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dictionary with logging statistics
        """
        stats = {
            'initialized': self.initialized,
            'handlers': list(self.handlers.keys()),
            'loggers': list(self.loggers.keys()),
            'root_level': logging.getLogger().level,
            'root_handlers': len(logging.getLogger().handlers)
        }
        
        # Add file handler stats if available
        if 'file' in self.handlers:
            file_handler = self.handlers['file']
            if hasattr(file_handler, 'baseFilename'):
                stats['log_file'] = file_handler.baseFilename
                if os.path.exists(file_handler.baseFilename):
                    stats['log_file_size'] = os.path.getsize(file_handler.baseFilename)
        
        return stats


# Global logging manager instance
logging_manager = LoggingManager()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging_manager.get_logger(name)


def setup_logging(**kwargs):
    """
    Set up logging configuration.
    
    Args:
        **kwargs: Logging configuration options
    """
    logging_manager.setup_logging(**kwargs)


def log_function_call(func):
    """
    Decorator to log function calls.
    
    Args:
        func: Function to decorate
    
    Returns:
        Decorated function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        logger.debug(f"Calling {func.__name__}", extra={
            'context': {
                'function': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_count': len(kwargs)
            }
        })
        
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful completion
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Completed {func.__name__} in {duration:.3f}s", extra={
                'context': {
                    'function': func.__name__,
                    'duration': duration,
                    'success': True
                }
            })
            
            return result
            
        except Exception as e:
            # Log error
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error in {func.__name__}: {str(e)}", extra={
                'context': {
                    'function': func.__name__,
                    'duration': duration,
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            }, exc_info=True)
            
            raise
    
    return wrapper


def log_database_operation(operation: str, table: str = None, record_id: str = None):
    """
    Log database operations.
    
    Args:
        operation: Database operation (CREATE, READ, UPDATE, DELETE)
        table: Table name
        record_id: Record ID
    """
    logger = get_logger('scitrace.database')
    logger.info(f"Database {operation}", extra={
        'context': {
            'operation': operation,
            'table': table,
            'record_id': record_id
        }
    })


def log_api_request(method: str, endpoint: str, status_code: int, duration: float, user_id: str = None):
    """
    Log API requests.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
        user_id: User ID (if authenticated)
    """
    logger = get_logger('scitrace.api')
    
    # Determine log level based on status code
    if status_code >= 500:
        log_level = logging.ERROR
    elif status_code >= 400:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    
    logger.log(log_level, f"API {method} {endpoint} - {status_code}", extra={
        'context': {
            'method': method,
            'endpoint': endpoint,
            'status_code': status_code,
            'duration': duration,
            'user_id': user_id
        }
    })


def log_datalad_operation(operation: str, dataset_path: str = None, success: bool = True, 
                         error: str = None, duration: float = None):
    """
    Log DataLad operations.
    
    Args:
        operation: DataLad operation
        dataset_path: Dataset path
        success: Whether operation was successful
        error: Error message if failed
        duration: Operation duration in seconds
    """
    logger = get_logger('scitrace.datalad')
    
    log_level = logging.INFO if success else logging.ERROR
    message = f"DataLad {operation}"
    if not success:
        message += f" - Failed: {error}"
    
    logger.log(log_level, message, extra={
        'context': {
            'operation': operation,
            'dataset_path': dataset_path,
            'success': success,
            'error': error,
            'duration': duration
        }
    })


def log_file_operation(operation: str, file_path: str, success: bool = True, 
                      error: str = None, file_size: int = None):
    """
    Log file operations.
    
    Args:
        operation: File operation
        file_path: File path
        success: Whether operation was successful
        error: Error message if failed
        file_size: File size in bytes
    """
    logger = get_logger('scitrace.files')
    
    log_level = logging.INFO if success else logging.ERROR
    message = f"File {operation}: {file_path}"
    if not success:
        message += f" - Failed: {error}"
    
    logger.log(log_level, message, extra={
        'context': {
            'operation': operation,
            'file_path': file_path,
            'success': success,
            'error': error,
            'file_size': file_size
        }
    })


def log_user_action(action: str, user_id: str, resource_type: str = None, 
                   resource_id: str = None, details: Dict[str, Any] = None):
    """
    Log user actions.
    
    Args:
        action: User action
        user_id: User ID
        resource_type: Type of resource affected
        resource_id: Resource ID
        details: Additional details
    """
    logger = get_logger('scitrace.user_actions')
    
    logger.info(f"User action: {action}", extra={
        'context': {
            'action': action,
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {}
        }
    })


def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, 
                      details: Dict[str, Any] = None):
    """
    Log security events.
    
    Args:
        event_type: Type of security event
        user_id: User ID (if applicable)
        ip_address: IP address
        details: Additional details
    """
    logger = get_logger('scitrace.security')
    
    logger.warning(f"Security event: {event_type}", extra={
        'context': {
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'details': details or {}
        }
    })


def log_performance_metric(metric_name: str, value: float, unit: str = None, 
                          context: Dict[str, Any] = None):
    """
    Log performance metrics.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Unit of measurement
        context: Additional context
    """
    logger = get_logger('scitrace.performance')
    
    logger.info(f"Performance metric: {metric_name} = {value}{unit or ''}", extra={
        'context': {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'context': context or {}
        }
    })


class LogContext:
    """Context manager for adding context to logs."""
    
    def __init__(self, **context):
        """
        Initialize log context.
        
        Args:
            **context: Context variables
        """
        self.context = context
        self.old_context = {}
    
    def __enter__(self):
        """Enter the context."""
        # Store old context
        for key in self.context:
            if hasattr(logging, key):
                self.old_context[key] = getattr(logging, key)
        
        # Set new context
        for key, value in self.context.items():
            setattr(logging, key, value)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        # Restore old context
        for key, value in self.old_context.items():
            setattr(logging, key, value)


def with_log_context(**context):
    """
    Decorator to add context to logs.
    
    Args:
        **context: Context variables
    
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with LogContext(**context):
                return func(*args, **kwargs)
        return wrapper
    return decorator
