"""
File operation utilities for SciTrace

Provides utility functions for common file operations and path handling.
"""

import os
import shutil
import stat
import mimetypes
import hashlib
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

from ..exceptions import FileOperationError, ValidationError

logger = logging.getLogger(__name__)


class FileUtils:
    """Utility class for file operations."""
    
    # Common file extensions and their types
    FILE_TYPES = {
        'text': ['.txt', '.md', '.rst', '.log'],
        'code': ['.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml'],
        'data': ['.csv', '.tsv', '.json', '.xml', '.h5', '.hdf5', '.parquet'],
        'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
        'archive': ['.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'],
        'executable': ['.exe', '.app', '.deb', '.rpm', '.dmg']
    }
    
    # Dangerous file extensions that should be restricted
    DANGEROUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.sh', '.ps1']
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'text': 10 * 1024 * 1024,      # 10MB
        'code': 5 * 1024 * 1024,       # 5MB
        'data': 100 * 1024 * 1024,     # 100MB
        'image': 50 * 1024 * 1024,     # 50MB
        'document': 25 * 1024 * 1024,  # 25MB
        'archive': 200 * 1024 * 1024,  # 200MB
        'default': 10 * 1024 * 1024    # 10MB
    }
    
    @staticmethod
    def get_file_type(file_path: str) -> str:
        """
        Get the type of a file based on its extension.
        
        Args:
            file_path: Path to the file
        
        Returns:
            File type string
        """
        ext = Path(file_path).suffix.lower()
        
        for file_type, extensions in FileUtils.FILE_TYPES.items():
            if ext in extensions:
                return file_type
        
        return 'unknown'
    
    @staticmethod
    def is_dangerous_file(file_path: str) -> bool:
        """
        Check if a file is potentially dangerous.
        
        Args:
            file_path: Path to the file
        
        Returns:
            True if file is dangerous, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in FileUtils.DANGEROUS_EXTENSIONS
    
    @staticmethod
    def get_max_file_size(file_path: str) -> int:
        """
        Get the maximum allowed size for a file type.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Maximum file size in bytes
        """
        file_type = FileUtils.get_file_type(file_path)
        return FileUtils.MAX_FILE_SIZES.get(file_type, FileUtils.MAX_FILE_SIZES['default'])
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_directories: List[str] = None) -> bool:
        """
        Validate a file path for security.
        
        Args:
            file_path: Path to validate
            allowed_directories: List of allowed directory prefixes
        
        Returns:
            True if path is valid, False otherwise
        
        Raises:
            ValidationError: If path is invalid
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        
        # Check for path traversal attacks
        if '..' in file_path or file_path.startswith('/'):
            raise ValidationError("Invalid file path: contains path traversal")
        
        # Check if path is within allowed directories
        if allowed_directories:
            is_allowed = any(abs_path.startswith(os.path.abspath(d)) for d in allowed_directories)
            if not is_allowed:
                raise ValidationError(f"File path not in allowed directories: {file_path}")
        
        return True
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Create a safe filename by removing dangerous characters.
        
        Args:
            filename: Original filename
        
        Returns:
            Safe filename
        """
        # Remove or replace dangerous characters
        dangerous_chars = '<>:"/\\|?*'
        safe_name = filename
        
        for char in dangerous_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        safe_name = safe_name.strip('. ')
        
        # Ensure filename is not empty
        if not safe_name:
            safe_name = 'unnamed_file'
        
        # Limit length
        if len(safe_name) > 255:
            name, ext = os.path.splitext(safe_name)
            safe_name = name[:255-len(ext)] + ext
        
        return safe_name
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dict containing file information
        
        Raises:
            FileOperationError: If file cannot be accessed
        """
        try:
            if not os.path.exists(file_path):
                raise FileOperationError(f"File does not exist: {file_path}", file_path=file_path)
            
            stat_info = os.stat(file_path)
            path_obj = Path(file_path)
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Calculate file hash (for small files)
            file_hash = None
            if stat_info.st_size < 10 * 1024 * 1024:  # Only for files < 10MB
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                except Exception:
                    pass  # Hash calculation is optional
            
            return {
                'name': path_obj.name,
                'path': file_path,
                'size': stat_info.st_size,
                'size_human': FileUtils.format_file_size(stat_info.st_size),
                'type': FileUtils.get_file_type(file_path),
                'mime_type': mime_type,
                'extension': path_obj.suffix.lower(),
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path),
                'is_dangerous': FileUtils.is_dangerous_file(file_path),
                'permissions': stat.filemode(stat_info.st_mode),
                'created': stat_info.st_ctime,
                'modified': stat_info.st_mtime,
                'accessed': stat_info.st_atime,
                'hash': file_hash
            }
            
        except Exception as e:
            raise FileOperationError(f"Failed to get file info: {str(e)}", file_path=file_path)
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
        
        Returns:
            True if copy was successful
        
        Raises:
            FileOperationError: If copy operation fails
        """
        try:
            # Validate source file
            if not os.path.exists(source):
                raise FileOperationError(f"Source file does not exist: {source}", 
                                       file_path=source, operation="copy")
            
            if not os.path.isfile(source):
                raise FileOperationError(f"Source is not a file: {source}", 
                                       file_path=source, operation="copy")
            
            # Check if destination exists
            if os.path.exists(destination) and not overwrite:
                raise FileOperationError(f"Destination file exists: {destination}", 
                                       file_path=destination, operation="copy")
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, destination)
            
            logger.info(f"Copied file from {source} to {destination}")
            return True
            
        except Exception as e:
            raise FileOperationError(f"Failed to copy file: {str(e)}", 
                                   file_path=source, operation="copy")
    
    @staticmethod
    def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Whether to overwrite existing files
        
        Returns:
            True if move was successful
        
        Raises:
            FileOperationError: If move operation fails
        """
        try:
            # Validate source file
            if not os.path.exists(source):
                raise FileOperationError(f"Source file does not exist: {source}", 
                                       file_path=source, operation="move")
            
            if not os.path.isfile(source):
                raise FileOperationError(f"Source is not a file: {source}", 
                                       file_path=source, operation="move")
            
            # Check if destination exists
            if os.path.exists(destination) and not overwrite:
                raise FileOperationError(f"Destination file exists: {destination}", 
                                       file_path=destination, operation="move")
            
            # Create destination directory if needed
            dest_dir = os.path.dirname(destination)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Move the file
            shutil.move(source, destination)
            
            logger.info(f"Moved file from {source} to {destination}")
            return True
            
        except Exception as e:
            raise FileOperationError(f"Failed to move file: {str(e)}", 
                                   file_path=source, operation="move")
    
    @staticmethod
    def delete_file(file_path: str, safe: bool = True) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            safe: Whether to use safe deletion (move to trash)
        
        Returns:
            True if deletion was successful
        
        Raises:
            FileOperationError: If deletion fails
        """
        try:
            if not os.path.exists(file_path):
                raise FileOperationError(f"File does not exist: {file_path}", 
                                       file_path=file_path, operation="delete")
            
            if not os.path.isfile(file_path):
                raise FileOperationError(f"Path is not a file: {file_path}", 
                                       file_path=file_path, operation="delete")
            
            if safe:
                # Move to trash instead of permanent deletion
                trash_dir = os.path.join(os.path.expanduser('~'), '.Trash')
                if not os.path.exists(trash_dir):
                    trash_dir = tempfile.gettempdir()
                
                trash_path = os.path.join(trash_dir, os.path.basename(file_path))
                counter = 1
                while os.path.exists(trash_path):
                    name, ext = os.path.splitext(os.path.basename(file_path))
                    trash_path = os.path.join(trash_dir, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.move(file_path, trash_path)
                logger.info(f"Moved file to trash: {file_path} -> {trash_path}")
            else:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            
            return True
            
        except Exception as e:
            raise FileOperationError(f"Failed to delete file: {str(e)}", 
                                   file_path=file_path, operation="delete")
    
    @staticmethod
    def create_directory(dir_path: str, parents: bool = True, exist_ok: bool = True) -> bool:
        """
        Create a directory.
        
        Args:
            dir_path: Path to the directory to create
            parents: Whether to create parent directories
            exist_ok: Whether to ignore if directory already exists
        
        Returns:
            True if creation was successful
        
        Raises:
            FileOperationError: If creation fails
        """
        try:
            os.makedirs(dir_path, exist_ok=exist_ok)
            logger.info(f"Created directory: {dir_path}")
            return True
            
        except Exception as e:
            raise FileOperationError(f"Failed to create directory: {str(e)}", 
                                   file_path=dir_path, operation="create_directory")
    
    @staticmethod
    def list_directory(dir_path: str, include_hidden: bool = False, 
                      file_types: List[str] = None) -> List[Dict[str, Any]]:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to the directory
            include_hidden: Whether to include hidden files
            file_types: Optional list of file types to filter by
        
        Returns:
            List of file/directory information dictionaries
        
        Raises:
            FileOperationError: If listing fails
        """
        try:
            if not os.path.exists(dir_path):
                raise FileOperationError(f"Directory does not exist: {dir_path}", 
                                       file_path=dir_path, operation="list_directory")
            
            if not os.path.isdir(dir_path):
                raise FileOperationError(f"Path is not a directory: {dir_path}", 
                                       file_path=dir_path, operation="list_directory")
            
            items = []
            for item_name in os.listdir(dir_path):
                # Skip hidden files if not requested
                if not include_hidden and item_name.startswith('.'):
                    continue
                
                item_path = os.path.join(dir_path, item_name)
                item_info = FileUtils.get_file_info(item_path)
                
                # Filter by file type if specified
                if file_types and item_info['type'] not in file_types:
                    continue
                
                items.append(item_info)
            
            # Sort by name
            items.sort(key=lambda x: x['name'].lower())
            
            return items
            
        except Exception as e:
            raise FileOperationError(f"Failed to list directory: {str(e)}", 
                                   file_path=dir_path, operation="list_directory")
    
    @staticmethod
    def get_directory_size(dir_path: str) -> Tuple[int, int]:
        """
        Get the total size and file count of a directory.
        
        Args:
            dir_path: Path to the directory
        
        Returns:
            Tuple of (total_size_bytes, file_count)
        
        Raises:
            FileOperationError: If calculation fails
        """
        try:
            if not os.path.exists(dir_path):
                raise FileOperationError(f"Directory does not exist: {dir_path}", 
                                       file_path=dir_path, operation="get_directory_size")
            
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        file_count += 1
                    except (OSError, IOError):
                        # Skip files that can't be accessed
                        continue
            
            return total_size, file_count
            
        except Exception as e:
            raise FileOperationError(f"Failed to get directory size: {str(e)}", 
                                   file_path=dir_path, operation="get_directory_size")
    
    @staticmethod
    def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
        """
        Find files matching a pattern in a directory.
        
        Args:
            directory: Directory to search in
            pattern: File pattern to match (e.g., "*.py", "*.txt")
            recursive: Whether to search recursively
        
        Returns:
            List of matching file paths
        
        Raises:
            FileOperationError: If search fails
        """
        try:
            if not os.path.exists(directory):
                raise FileOperationError(f"Directory does not exist: {directory}", 
                                       file_path=directory, operation="find_files")
            
            import glob
            
            if recursive:
                search_pattern = os.path.join(directory, "**", pattern)
                files = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(directory, pattern)
                files = glob.glob(search_pattern)
            
            # Filter out directories
            files = [f for f in files if os.path.isfile(f)]
            
            return files
            
        except Exception as e:
            raise FileOperationError(f"Failed to find files: {str(e)}", 
                                   file_path=directory, operation="find_files")
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
        """
        Read a text file safely.
        
        Args:
            file_path: Path to the file
            encoding: File encoding
        
        Returns:
            File contents as string
        
        Raises:
            FileOperationError: If reading fails
        """
        try:
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = FileUtils.get_max_file_size(file_path)
            
            if file_size > max_size:
                raise FileOperationError(f"File too large: {file_size} bytes (max: {max_size})", 
                                       file_path=file_path, operation="read")
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
                
        except Exception as e:
            raise FileOperationError(f"Failed to read file: {str(e)}", 
                                   file_path=file_path, operation="read")
    
    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8', 
                       create_dirs: bool = True) -> bool:
        """
        Write content to a text file safely.
        
        Args:
            file_path: Path to the file
            content: Content to write
            encoding: File encoding
            create_dirs: Whether to create parent directories
        
        Returns:
            True if writing was successful
        
        Raises:
            FileOperationError: If writing fails
        """
        try:
            # Create parent directories if needed
            if create_dirs:
                parent_dir = os.path.dirname(file_path)
                if parent_dir and not os.path.exists(parent_dir):
                    os.makedirs(parent_dir, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Wrote content to file: {file_path}")
            return True
            
        except Exception as e:
            raise FileOperationError(f"Failed to write file: {str(e)}", 
                                   file_path=file_path, operation="write")
