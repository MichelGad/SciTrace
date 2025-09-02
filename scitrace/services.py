"""
Services for SciTrace

This file maintains backward compatibility by importing from the separated service files.
For new code, please import directly from datalad_services or project_services.
"""

# Import the separated services for backward compatibility
from .datalad_services import DataLadService
from .project_services import ProjectService

# Re-export the classes for backward compatibility
__all__ = ['DataLadService', 'ProjectService']
