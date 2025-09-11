"""
Path validation utilities for SciTrace

Provides reusable functions for validating file paths and directory access.
"""

import os
from typing import List, Optional, Tuple
from pathlib import Path

from ..exceptions import ValidationError, SecurityError


class PathValidator:
    """Utility class for path validation operations."""
    
    # Default allowed base paths for security
    DEFAULT_ALLOWED_PATHS = [
        os.path.expanduser('~'),  # Home directory
        '/Users',
        '/home',
        '/tmp',
        '/var/tmp'
    ]
    
    # Common dataset base paths
    DATASET_BASE_PATHS = [
        os.path.join(os.path.expanduser('~'), 'scitrace_demo_datasets'),
        os.path.join(os.path.expanduser('~'), 'datasets'),
        os.path.join(os.path.expanduser('~'), 'research_data')
    ]
    
    @classmethod
    def validate_path_exists(cls, path: str, path_type: str = "path") -> str:
        """
        Validate that a path exists.
        
        Args:
            path: Path to validate
            path_type: Type of path for error messages (e.g., "file", "directory")
        
        Returns:
            Normalized absolute path
        
        Raises:
            ValidationError: If path doesn't exist
        """
        if not path:
            raise ValidationError(f"{path_type.title()} path is required")
        
        # Normalize the path
        normalized_path = os.path.abspath(path)
        
        if not os.path.exists(normalized_path):
            raise ValidationError(f"{path_type.title()} does not exist: {normalized_path}")
        
        return normalized_path
    
    @classmethod
    def validate_directory_exists(cls, directory_path: str) -> str:
        """
        Validate that a directory exists.
        
        Args:
            directory_path: Directory path to validate
        
        Returns:
            Normalized absolute directory path
        
        Raises:
            ValidationError: If directory doesn't exist or is not a directory
        """
        normalized_path = cls.validate_path_exists(directory_path, "directory")
        
        if not os.path.isdir(normalized_path):
            raise ValidationError(f"Path is not a directory: {normalized_path}")
        
        return normalized_path
    
    @classmethod
    def validate_file_exists(cls, file_path: str) -> str:
        """
        Validate that a file exists.
        
        Args:
            file_path: File path to validate
        
        Returns:
            Normalized absolute file path
        
        Raises:
            ValidationError: If file doesn't exist or is not a file
        """
        normalized_path = cls.validate_path_exists(file_path, "file")
        
        if not os.path.isfile(normalized_path):
            raise ValidationError(f"Path is not a file: {normalized_path}")
        
        return normalized_path
    
    @classmethod
    def validate_path_security(cls, path: str, allowed_paths: Optional[List[str]] = None) -> str:
        """
        Validate that a path is within allowed directories for security.
        
        Args:
            path: Path to validate
            allowed_paths: List of allowed base paths (defaults to DEFAULT_ALLOWED_PATHS)
        
        Returns:
            Normalized absolute path
        
        Raises:
            SecurityError: If path is not within allowed directories
            ValidationError: If path is invalid
        """
        if not path:
            raise ValidationError("Path is required")
        
        # Normalize the path
        normalized_path = os.path.abspath(path)
        
        # Use default allowed paths if none provided
        if allowed_paths is None:
            allowed_paths = cls.DEFAULT_ALLOWED_PATHS
        
        # Check if the path is within any allowed directory
        is_allowed = any(normalized_path.startswith(allowed_path) for allowed_path in allowed_paths)
        
        if not is_allowed:
            raise SecurityError(f"Access denied: Path not in allowed directories: {normalized_path}")
        
        return normalized_path
    
    @classmethod
    def validate_dataset_path(cls, dataset_path: str) -> str:
        """
        Validate a dataset path for DataLad operations.
        
        Args:
            dataset_path: Dataset path to validate
        
        Returns:
            Normalized absolute dataset path
        
        Raises:
            ValidationError: If dataset path is invalid
            SecurityError: If path is not secure
        """
        # First validate security
        normalized_path = cls.validate_path_security(dataset_path)
        
        # Check if it's a directory
        if not os.path.isdir(normalized_path):
            raise ValidationError(f"Dataset path is not a directory: {normalized_path}")
        
        # Check for DataLad indicators
        datalad_indicators = ['.datalad', '.git']
        has_indicators = any(os.path.exists(os.path.join(normalized_path, indicator)) 
                           for indicator in datalad_indicators)
        
        if not has_indicators:
            raise ValidationError(f"Path does not appear to be a DataLad dataset: {normalized_path}")
        
        return normalized_path
    
    @classmethod
    def find_dataset_path(cls, project_name: str, base_paths: Optional[List[str]] = None) -> Optional[str]:
        """
        Find a dataset path for a project.
        
        Args:
            project_name: Name of the project
            base_paths: List of base paths to search (defaults to DATASET_BASE_PATHS)
        
        Returns:
            Dataset path if found, None otherwise
        """
        if base_paths is None:
            base_paths = cls.DATASET_BASE_PATHS
        
        # Common project directory patterns
        project_patterns = [
            project_name,
            project_name.replace(' ', '_'),
            project_name.replace(' ', '-'),
            f"*{project_name}*",
            f"*{project_name.replace(' ', '_')}*"
        ]
        
        for base_path in base_paths:
            if not os.path.exists(base_path):
                continue
            
            for pattern in project_patterns:
                # Try exact match first
                exact_path = os.path.join(base_path, pattern)
                if os.path.exists(exact_path) and os.path.isdir(exact_path):
                    return os.path.abspath(exact_path)
                
                # Try pattern matching
                try:
                    import glob
                    matches = glob.glob(os.path.join(base_path, pattern))
                    for match in matches:
                        if os.path.isdir(match):
                            return os.path.abspath(match)
                except Exception:
                    continue
        
        return None
    
    @classmethod
    def validate_relative_path(cls, base_path: str, relative_path: str) -> str:
        """
        Validate a relative path within a base directory.
        
        Args:
            base_path: Base directory path
            relative_path: Relative path to validate
        
        Returns:
            Normalized absolute path
        
        Raises:
            ValidationError: If path is invalid or outside base directory
            SecurityError: If path traversal is detected
        """
        # Validate base path
        normalized_base = cls.validate_directory_exists(base_path)
        
        if not relative_path:
            raise ValidationError("Relative path is required")
        
        # Check for path traversal attempts
        if '..' in relative_path or relative_path.startswith('/'):
            raise SecurityError("Path traversal detected in relative path")
        
        # Construct full path
        full_path = os.path.join(normalized_base, relative_path)
        normalized_full = os.path.abspath(full_path)
        
        # Ensure the full path is within the base directory
        if not normalized_full.startswith(normalized_base):
            raise SecurityError("Relative path escapes base directory")
        
        return normalized_full
    
    @classmethod
    def get_safe_filename(cls, filename: str) -> str:
        """
        Get a safe filename by removing or replacing dangerous characters.
        
        Args:
            filename: Original filename
        
        Returns:
            Safe filename
        
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename:
            raise ValidationError("Filename is required")
        
        # Remove or replace dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        safe_filename = filename
        
        for char in dangerous_chars:
            safe_filename = safe_filename.replace(char, '_')
        
        # Remove leading/trailing whitespace and dots
        safe_filename = safe_filename.strip(' .')
        
        # Ensure filename is not empty after cleaning
        if not safe_filename:
            raise ValidationError("Filename is empty after cleaning")
        
        # Limit length
        if len(safe_filename) > 255:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:255-len(ext)] + ext
        
        return safe_filename
    
    @classmethod
    def validate_file_extension(cls, file_path: str, allowed_extensions: List[str]) -> str:
        """
        Validate that a file has an allowed extension.
        
        Args:
            file_path: File path to validate
            allowed_extensions: List of allowed extensions (with or without dots)
        
        Returns:
            Normalized file path
        
        Raises:
            ValidationError: If file extension is not allowed
        """
        normalized_path = cls.validate_file_exists(file_path)
        
        # Get file extension
        _, ext = os.path.splitext(normalized_path)
        ext = ext.lower()
        
        # Normalize allowed extensions (ensure they start with dots)
        normalized_allowed = []
        for allowed_ext in allowed_extensions:
            if not allowed_ext.startswith('.'):
                allowed_ext = '.' + allowed_ext
            normalized_allowed.append(allowed_ext.lower())
        
        if ext not in normalized_allowed:
            raise ValidationError(f"File extension '{ext}' is not allowed. Allowed extensions: {', '.join(normalized_allowed)}")
        
        return normalized_path
    
    @classmethod
    def create_secure_temp_path(cls, prefix: str = "scitrace_", suffix: str = "") -> str:
        """
        Create a secure temporary file path.
        
        Args:
            prefix: Prefix for the temporary file
            suffix: Suffix for the temporary file
        
        Returns:
            Secure temporary file path
        """
        import tempfile
        
        # Create a secure temporary file
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)  # Close the file descriptor
        
        return temp_path
    
    @classmethod
    def get_path_info(cls, path: str) -> dict:
        """
        Get information about a path.
        
        Args:
            path: Path to analyze
        
        Returns:
            Dictionary containing path information
        """
        if not path:
            return {'exists': False, 'error': 'Path is empty'}
        
        try:
            normalized_path = os.path.abspath(path)
            stat_info = os.stat(normalized_path)
            
            return {
                'exists': True,
                'path': normalized_path,
                'is_file': os.path.isfile(normalized_path),
                'is_directory': os.path.isdir(normalized_path),
                'size': stat_info.st_size,
                'permissions': oct(stat_info.st_mode)[-3:],
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'accessed': stat_info.st_atime
            }
        except Exception as e:
            return {
                'exists': False,
                'error': str(e),
                'path': path
            }
