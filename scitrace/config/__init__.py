"""
Configuration management for SciTrace

This package contains configuration classes and utilities for different environments.
"""

from .config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from .settings import get_config

__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'get_config']
