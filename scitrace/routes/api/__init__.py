"""
API routes package for SciTrace

Contains focused API modules for different functionality areas.
"""

from .dataflow_api import bp as dataflow_api_bp
from .git_api import bp as git_api_bp
from .file_api import bp as file_api_bp
from .admin_api import bp as admin_api_bp
from .project_api import bp as project_api_bp

__all__ = [
    'dataflow_api_bp',
    'git_api_bp', 
    'file_api_bp',
    'admin_api_bp',
    'project_api_bp'
]
