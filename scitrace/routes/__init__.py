"""
Routes package for SciTrace

Contains all the route blueprints for the application.
"""

from . import auth, dashboard, projects, dataflow, api, tasks

__all__ = ['auth', 'dashboard', 'projects', 'dataflow', 'api', 'tasks']
