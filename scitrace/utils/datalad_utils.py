"""
DataLad command utilities for SciTrace

Provides centralized subprocess calls and error handling for DataLad operations.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import shutil

from .response_utils import APIResponse, handle_exception

# Configure logging
logger = logging.getLogger(__name__)


class DataLadCommandError(Exception):
    """Custom exception for DataLad command errors."""
    
    def __init__(self, message: str, command: List[str], returncode: int, 
                 stdout: str = "", stderr: str = ""):
        self.message = message
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super().__init__(self.message)


class DataLadUtils:
    """Utility class for DataLad operations with centralized error handling."""
    
    def __init__(self, timeout: int = 300, check_datalad: bool = True):
        """
        Initialize DataLad utilities.
        
        Args:
            timeout: Default timeout for subprocess calls in seconds
            check_datalad: Whether to check if DataLad is available on initialization
        """
        self.timeout = timeout
        self.datalad_available = False
        
        if check_datalad:
            self.datalad_available = self._check_datalad_availability()
    
    def _check_datalad_availability(self) -> bool:
        """Check if DataLad is available in the system."""
        try:
            result = self._run_command(['datalad', '--version'], timeout=10)
            logger.info(f"DataLad available: {result['stdout'].strip()}")
            return True
        except (DataLadCommandError, FileNotFoundError):
            logger.warning("DataLad not available in system PATH")
            return False
    
    def _run_command(
        self, 
        command: List[str], 
        cwd: str = None, 
        timeout: int = None,
        capture_output: bool = True,
        check: bool = True
    ) -> Dict[str, Any]:
        """
        Run a command with standardized error handling.
        
        Args:
            command: Command to run as a list of strings
            cwd: Working directory for the command
            timeout: Timeout in seconds (uses instance default if None)
            capture_output: Whether to capture stdout/stderr
            check: Whether to raise exception on non-zero return code
        
        Returns:
            Dict containing returncode, stdout, stderr, and command info
        
        Raises:
            DataLadCommandError: If command fails and check=True
        """
        if timeout is None:
            timeout = self.timeout
        
        logger.debug(f"Running command: {' '.join(command)} in {cwd or 'current directory'}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                check=False  # We'll handle the return code ourselves
            )
            
            response = {
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else '',
                'stderr': result.stderr if capture_output else '',
                'command': command,
                'cwd': cwd,
                'timeout': timeout
            }
            
            if check and result.returncode != 0:
                error_msg = f"Command failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()}"
                
                raise DataLadCommandError(
                    message=error_msg,
                    command=command,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
            
            return response
            
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout} seconds"
            raise DataLadCommandError(
                message=error_msg,
                command=command,
                returncode=-1,
                stdout=e.stdout or '',
                stderr=e.stderr or ''
            )
        except FileNotFoundError as e:
            error_msg = f"Command not found: {command[0]}"
            raise DataLadCommandError(
                message=error_msg,
                command=command,
                returncode=-1,
                stdout='',
                stderr=str(e)
            )
    
    def create_dataset(
        self, 
        dataset_path: str, 
        research_type: str = "general",
        name: str = None
    ) -> Dict[str, Any]:
        """
        Create a new DataLad dataset.
        
        Args:
            dataset_path: Path where to create the dataset
            research_type: Type of research (affects dataset structure)
            name: Optional name for the dataset
        
        Returns:
            Dict containing creation result information
        """
        if not self.datalad_available:
            raise DataLadCommandError(
                message="DataLad is not available",
                command=['datalad'],
                returncode=-1
            )
        
        if os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset already exists at {dataset_path}",
                command=['datalad', 'create'],
                returncode=-1
            )
        
        try:
            # Create DataLad dataset using simple datalad create
            cmd = ['datalad', 'create', dataset_path]
            
            result = self._run_command(cmd, timeout=60)  # Shorter timeout for simple create
            
            # Verify dataset was created
            if not os.path.exists(os.path.join(dataset_path, '.git')):
                raise DataLadCommandError(
                    message="DataLad dataset was not created properly - missing .git directory",
                    command=cmd,
                    returncode=-1
                )
            
            return {
                'dataset_path': dataset_path,
                'status': 'created',
                'research_type': research_type,
                'message': f'Created DataLad dataset with {research_type} research structure',
                'command_output': result['stdout']
            }
            
        except DataLadCommandError:
            raise
        except Exception as e:
            raise DataLadCommandError(
                message=f"Unexpected error creating dataset: {str(e)}",
                command=['datalad', 'create-test-dataset'],
                returncode=-1
            )
    
    def save_changes(
        self, 
        dataset_path: str, 
        message: str, 
        files: List[str] = None
    ) -> Dict[str, Any]:
        """
        Save changes to a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
            message: Commit message
            files: Optional list of specific files to save
        
        Returns:
            Dict containing save result information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'save'],
                returncode=-1
            )
        
        cmd = ['datalad', 'save', '-m', message]
        
        if files:
            cmd.extend(files)
        
        result = self._run_command(cmd, cwd=dataset_path)
        
        return {
            'status': 'saved',
            'message': message,
            'files': files,
            'command_output': result['stdout']
        }
    
    def get_status(self, dataset_path: str) -> Dict[str, Any]:
        """
        Get the status of a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing status information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'status'],
                returncode=-1
            )
        
        result = self._run_command(['datalad', 'status'], cwd=dataset_path)
        
        return {
            'status_output': result['stdout'],
            'dataset_path': dataset_path
        }
    
    def get_log(self, dataset_path: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get the commit log of a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
            limit: Maximum number of commits to return
        
        Returns:
            Dict containing log information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'log'],
                returncode=-1
            )
        
        result = self._run_command(['datalad', 'log', '-n', str(limit)], cwd=dataset_path)
        
        return {
            'log_output': result['stdout'],
            'dataset_path': dataset_path,
            'limit': limit
        }
    
    def run_command(
        self, 
        dataset_path: str, 
        command: str, 
        inputs: List[str] = None,
        outputs: List[str] = None,
        message: str = None
    ) -> Dict[str, Any]:
        """
        Run a command in a DataLad dataset with input/output tracking.
        
        Args:
            dataset_path: Path to the dataset
            command: Command to run
            inputs: List of input file paths
            outputs: List of output file paths
            message: Optional commit message
        
        Returns:
            Dict containing command execution result
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'run'],
                returncode=-1
            )
        
        # Handle existing output files that might be symbolic links
        # Extract output files from the command (simple parsing)
        import re
        output_files = []
        
        if outputs:
            output_files = outputs
        else:
            # Try to extract output files from command (basic parsing)
            # Look for patterns like "output.csv" or "results/file.csv"
            output_patterns = re.findall(r'\b(?:results|outputs?|plots?)/[^\s]+\.(?:csv|txt|json|png|jpg|pdf)\b', command)
            output_files = output_patterns
        
        # Remove existing output files if they are symbolic links
        removed_links = []
        for output_file in output_files:
            full_output_path = os.path.join(dataset_path, output_file)
            if os.path.exists(full_output_path) and os.path.islink(full_output_path):
                try:
                    os.unlink(full_output_path)
                    removed_links.append(output_file)
                    print(f"Removed existing symbolic link: {output_file}")
                except Exception as e:
                    print(f"Warning: Could not remove {output_file}: {e}")
        
        # If we removed symbolic links, we need to save the deletions first
        if removed_links:
            try:
                save_cmd = ['datalad', 'save', '-m', f'Remove symbolic links for script execution: {", ".join(removed_links)}']
                save_result = self._run_command(save_cmd, cwd=dataset_path, timeout=60)
                print(f"Saved deletions for removed symbolic links: {removed_links}")
                print(f"Save result: {save_result}")
            except Exception as e:
                print(f"Warning: Could not save deletions for removed symbolic links: {e}")
                # Continue anyway - the command might still work
        
        cmd = ['datalad', 'run', '-m', message or f'Run command: {command}']
        
        # Add input files
        if inputs:
            for input_file in inputs:
                cmd.extend(['-i', input_file])
        
        # Add output files
        if outputs:
            for output_file in outputs:
                cmd.extend(['-o', output_file])
        
        cmd.append(command)
        
        result = self._run_command(cmd, cwd=dataset_path, timeout=600)
        
        return {
            'status': 'completed',
            'command': command,
            'inputs': inputs,
            'outputs': outputs,
            'message': message,
            'command_output': result['stdout'],
            'returncode': result['returncode']
        }
    
    def add_file(
        self, 
        dataset_path: str, 
        file_path: str, 
        message: str = None
    ) -> Dict[str, Any]:
        """
        Add a file to a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
            file_path: Path to the file to add (relative to dataset)
            message: Optional commit message
        
        Returns:
            Dict containing add result information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'save'],
                returncode=-1
            )
        
        full_file_path = os.path.join(dataset_path, file_path)
        if not os.path.exists(full_file_path):
            raise DataLadCommandError(
                message=f"File does not exist: {full_file_path}",
                command=['datalad', 'save'],
                returncode=-1
            )
        
        commit_message = message or f'Add file: {file_path}'
        result = self._run_command(
            ['datalad', 'save', '-m', commit_message, file_path], 
            cwd=dataset_path
        )
        
        return {
            'status': 'added',
            'file_path': file_path,
            'message': commit_message,
            'command_output': result['stdout']
        }
    
    def remove_dataset(self, dataset_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Remove a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset to remove
            force: Whether to force removal without confirmation
        
        Returns:
            Dict containing removal result information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'remove'],
                returncode=-1
            )
        
        cmd = ['datalad', 'remove']
        if force:
            cmd.append('--nocheck')
        cmd.extend(['--recursive', dataset_path])
        
        result = self._run_command(cmd, timeout=600)
        
        return {
            'status': 'removed',
            'dataset_path': dataset_path,
            'command_output': result['stdout']
        }
    
    def get_metadata(self, dataset_path: str) -> Dict[str, Any]:
        """
        Get metadata for a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing metadata information
        """
        if not os.path.exists(dataset_path):
            raise DataLadCommandError(
                message=f"Dataset path does not exist: {dataset_path}",
                command=['datalad', 'metadata'],
                returncode=-1
            )
        
        result = self._run_command(['datalad', 'metadata', 'show'], cwd=dataset_path, check=False)
        
        return {
            'metadata_output': result['stdout'],
            'dataset_path': dataset_path,
            'has_metadata': result['returncode'] == 0
        }
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """
        Validate a DataLad dataset.
        
        Args:
            dataset_path: Path to the dataset
        
        Returns:
            Dict containing validation results
        """
        if not os.path.exists(dataset_path):
            return {
                'valid': False,
                'errors': [f"Dataset path does not exist: {dataset_path}"]
            }
        
        errors = []
        warnings = []
        
        # Check for .git directory
        if not os.path.exists(os.path.join(dataset_path, '.git')):
            errors.append("Missing .git directory - not a valid git repository")
        
        # Check for .datalad directory
        if not os.path.exists(os.path.join(dataset_path, '.datalad')):
            warnings.append("Missing .datalad directory - may not be a DataLad dataset")
        
        # Try to get status
        try:
            status_result = self.get_status(dataset_path)
        except DataLadCommandError as e:
            errors.append(f"Failed to get dataset status: {e.message}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'dataset_path': dataset_path
        }


# Global instance for convenience
datalad_utils = DataLadUtils()


def get_datalad_utils() -> DataLadUtils:
    """Get the global DataLadUtils instance."""
    return datalad_utils
