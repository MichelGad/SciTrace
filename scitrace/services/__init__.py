"""
Services package for SciTrace

This package contains service classes for business logic and data operations.
"""

from .base_service import BaseService
from .project_service import ProjectService
from .dataset_creation import DatasetCreationService
from .file_operations import FileOperationsService
from .git_operations import GitOperationsService
from .metadata_operations import MetadataOperationsService
from .project_management import ProjectManagementService
from .dataset_integration import DatasetIntegrationService

__all__ = [
    'BaseService', 
    'ProjectService', 
    'DatasetCreationService',
    'FileOperationsService',
    'GitOperationsService',
    'MetadataOperationsService',
    'ProjectManagementService',
    'DatasetIntegrationService'
]
