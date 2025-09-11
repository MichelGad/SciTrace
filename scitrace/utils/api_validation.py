"""
API validation utilities for SciTrace

Provides decorators and utilities for validating API requests and parameters.
"""

import functools
from typing import Dict, List, Optional, Any, Callable
from flask import request, jsonify, current_app

from .path_validation import PathValidator
from .response_utils import APIResponse
from ..exceptions import ValidationError, SecurityError


def validate_json_request(required_fields: List[str] = None, optional_fields: List[str] = None):
    """
    Decorator to validate JSON request data.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names (for validation if present)
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Check if request has JSON data
                if not request.is_json:
                    return APIResponse.error("Request must be JSON", 400)
                
                data = request.get_json()
                if not data:
                    return APIResponse.error("No JSON data provided", 400)
                
                # Validate required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return APIResponse.error(f"Missing required fields: {', '.join(missing_fields)}", 400)
                
                # Validate optional fields if present
                if optional_fields:
                    for field in optional_fields:
                        if field in data and data[field] is None:
                            return APIResponse.error(f"Field '{field}' cannot be null", 400)
                
                # Add validated data to kwargs
                kwargs['validated_data'] = data
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Request validation failed: {str(e)}", 400)
        
        return wrapper
    return decorator


def validate_path_parameter(param_name: str, path_type: str = "path", check_security: bool = True):
    """
    Decorator to validate path parameters.
    
    Args:
        param_name: Name of the path parameter
        path_type: Type of path ("file", "directory", "dataset")
        check_security: Whether to perform security validation
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                path = kwargs.get(param_name)
                if not path:
                    return APIResponse.error(f"{param_name} parameter is required", 400)
                
                # Validate path based on type
                if path_type == "file":
                    validated_path = PathValidator.validate_file_exists(path)
                elif path_type == "directory":
                    validated_path = PathValidator.validate_directory_exists(path)
                elif path_type == "dataset":
                    validated_path = PathValidator.validate_dataset_path(path)
                else:
                    validated_path = PathValidator.validate_path_exists(path)
                
                # Check security if requested
                if check_security:
                    validated_path = PathValidator.validate_path_security(validated_path)
                
                # Replace the parameter with validated path
                kwargs[param_name] = validated_path
                return func(*args, **kwargs)
                
            except ValidationError as e:
                return APIResponse.error(f"Path validation failed: {str(e)}", 400)
            except SecurityError as e:
                return APIResponse.error(f"Security validation failed: {str(e)}", 403)
            except Exception as e:
                return APIResponse.error(f"Path validation error: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_project_access(project_param: str = "project_id"):
    """
    Decorator to validate user access to a project.
    
    Args:
        project_param: Name of the project parameter
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask_login import current_user
                from ..models import Project
                
                project_id = kwargs.get(project_param)
                if not project_id:
                    return APIResponse.error("Project ID is required", 400)
                
                # Get project from database
                project = Project.query.get(project_id)
                if not project:
                    return APIResponse.error("Project not found", 404)
                
                # Check user access
                if project.admin_id != current_user.id:
                    return APIResponse.error("Access denied to project", 403)
                
                # Add project to kwargs
                kwargs['project'] = project
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Project access validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_task_access(task_param: str = "task_id"):
    """
    Decorator to validate user access to a task.
    
    Args:
        task_param: Name of the task parameter
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask_login import current_user
                from ..models import Task
                
                task_id = kwargs.get(task_param)
                if not task_id:
                    return APIResponse.error("Task ID is required", 400)
                
                # Get task from database
                task = Task.query.get(task_id)
                if not task:
                    return APIResponse.error("Task not found", 404)
                
                # Check user access
                if task.user_id != current_user.id:
                    return APIResponse.error("Access denied to task", 403)
                
                # Add task to kwargs
                kwargs['task'] = task
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Task access validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_dataflow_access(dataflow_param: str = "dataflow_id"):
    """
    Decorator to validate user access to a dataflow.
    
    Args:
        dataflow_param: Name of the dataflow parameter
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask_login import current_user
                from ..models import Dataflow
                
                dataflow_id = kwargs.get(dataflow_param)
                if not dataflow_id:
                    return APIResponse.error("Dataflow ID is required", 400)
                
                # Get dataflow from database
                dataflow = Dataflow.query.get(dataflow_id)
                if not dataflow:
                    return APIResponse.error("Dataflow not found", 404)
                
                # Check user access through project
                if dataflow.project.admin_id != current_user.id:
                    return APIResponse.error("Access denied to dataflow", 403)
                
                # Add dataflow to kwargs
                kwargs['dataflow'] = dataflow
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Dataflow access validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_admin_access():
    """
    Decorator to validate that the user has admin access.
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                from flask_login import current_user
                
                if current_user.role != 'admin':
                    return APIResponse.error("Admin access required", 403)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Admin access validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_dataset_path_from_project(project_param: str = "project_id", dataset_param: str = "dataset_path"):
    """
    Decorator to validate and get dataset path from a project.
    
    Args:
        project_param: Name of the project parameter
        dataset_param: Name of the dataset parameter to add to kwargs
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                project = kwargs.get('project')
                if not project:
                    return APIResponse.error("Project not found", 404)
                
                # Get dataset path from project
                dataset_path = project.dataset_path
                if not dataset_path:
                    return APIResponse.error("No dataset path found for project", 404)
                
                # Validate dataset path
                try:
                    validated_path = PathValidator.validate_dataset_path(dataset_path)
                    kwargs[dataset_param] = validated_path
                except ValidationError as e:
                    return APIResponse.error(f"Dataset validation failed: {str(e)}", 400)
                except SecurityError as e:
                    return APIResponse.error(f"Dataset security validation failed: {str(e)}", 403)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Dataset path validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def validate_stage_name(stage_param: str = "stage_name"):
    """
    Decorator to validate stage names for dataflow operations.
    
    Args:
        stage_param: Name of the stage parameter
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                stage_name = kwargs.get(stage_param)
                if not stage_name:
                    return APIResponse.error("Stage name is required", 400)
                
                # Valid stage names
                valid_stages = [
                    'raw_data', 'preprocessed', 'analysis', 'modeling', 
                    'visualization', 'scripts', 'results', 'plots', 'dataset_root'
                ]
                
                if stage_name not in valid_stages:
                    return APIResponse.error(f"Invalid stage name. Valid stages: {', '.join(valid_stages)}", 400)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                return APIResponse.error(f"Stage name validation failed: {str(e)}", 500)
        
        return wrapper
    return decorator


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle common API errors and return standardized responses.
    
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return APIResponse.error(f"Validation error: {str(e)}", 400)
        except SecurityError as e:
            return APIResponse.error(f"Security error: {str(e)}", 403)
        except FileNotFoundError as e:
            return APIResponse.error(f"File not found: {str(e)}", 404)
        except PermissionError as e:
            return APIResponse.error(f"Permission denied: {str(e)}", 403)
        except Exception as e:
            current_app.logger.error(f"API error in {func.__name__}: {str(e)}")
            return APIResponse.error(f"Internal server error: {str(e)}", 500)
    
    return wrapper
