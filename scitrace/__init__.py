"""
SciTrace - Research Data Management Platform

A modern web interface for DataLad-based research data management
with visual dataflow representation and project dashboard.
"""

__version__ = "0.1.0"
__author__ = "SciTrace Team"
__email__ = "info@scitrace.org"

from .app import create_app
from .models import Project, Task, User, Dataflow
from .services import ProjectService

__all__ = [
    'create_app',
    'Project',
    'Task', 
    'User',
    'Dataflow',
    'ProjectService'
]
