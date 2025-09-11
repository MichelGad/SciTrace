"""
Settings utilities for SciTrace

Provides functions to load and manage configuration settings.
"""

import os
from typing import Optional, Dict, Any
from .config import config


def get_config(config_name: Optional[str] = None):
    """
    Get configuration class based on environment.
    
    Args:
        config_name: Configuration name (development, production, testing)
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])


def get_setting(key: str, default: Any = None, config_name: Optional[str] = None) -> Any:
    """
    Get a specific setting value.
    
    Args:
        key: Setting key
        default: Default value if setting not found
        config_name: Configuration name (optional)
    
    Returns:
        Setting value
    """
    config_class = get_config(config_name)
    return getattr(config_class, key, default)


def get_database_url() -> str:
    """Get database URL from configuration."""
    return get_setting('SQLALCHEMY_DATABASE_URI')


def get_datalad_base_path() -> str:
    """Get DataLad base path from configuration."""
    return get_setting('DATALAD_BASE_PATH')


def get_upload_folder() -> str:
    """Get upload folder path from configuration."""
    return get_setting('UPLOAD_FOLDER')


def get_secret_key() -> str:
    """Get secret key from configuration."""
    return get_setting('SECRET_KEY')


def is_development() -> bool:
    """Check if running in development mode."""
    return os.environ.get('FLASK_ENV', 'development') == 'development'


def is_production() -> bool:
    """Check if running in production mode."""
    return os.environ.get('FLASK_ENV', 'development') == 'production'


def is_testing() -> bool:
    """Check if running in testing mode."""
    return os.environ.get('FLASK_ENV', 'development') == 'testing'


def get_feature_flags() -> Dict[str, bool]:
    """Get all feature flags."""
    return {
        'datalad_integration': get_setting('ENABLE_DATALAD_INTEGRATION', True),
        'git_operations': get_setting('ENABLE_GIT_OPERATIONS', True),
        'file_uploads': get_setting('ENABLE_FILE_UPLOADS', True),
        'api_documentation': get_setting('ENABLE_API_DOCUMENTATION', True),
        'metrics': get_setting('ENABLE_METRICS', False)
    }


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration."""
    return {
        'level': get_setting('LOG_LEVEL', 'INFO'),
        'file': get_setting('LOG_FILE', 'scitrace.log'),
        'max_bytes': 10240000,  # 10MB
        'backup_count': 10
    }


def get_security_config() -> Dict[str, Any]:
    """Get security configuration."""
    return {
        'session_cookie_secure': get_setting('SESSION_COOKIE_SECURE', False),
        'session_cookie_httponly': get_setting('SESSION_COOKIE_HTTPONLY', True),
        'session_cookie_samesite': get_setting('SESSION_COOKIE_SAMESITE', 'Lax'),
        'csrf_enabled': get_setting('WTF_CSRF_ENABLED', True)
    }


def get_performance_config() -> Dict[str, Any]:
    """Get performance configuration."""
    return {
        'database_pool_size': get_setting('DATABASE_POOL_SIZE', 10),
        'database_pool_timeout': get_setting('DATABASE_POOL_TIMEOUT', 20),
        'database_pool_recycle': get_setting('DATABASE_POOL_RECYCLE', 3600),
        'cache_type': get_setting('CACHE_TYPE', 'simple'),
        'cache_default_timeout': get_setting('CACHE_DEFAULT_TIMEOUT', 300)
    }


def validate_config() -> Dict[str, Any]:
    """
    Validate configuration settings.
    
    Returns:
        Dict containing validation results
    """
    errors = []
    warnings = []
    
    # Check required settings
    if not get_secret_key() or get_secret_key() == 'dev-secret-key-change-in-production':
        if is_production():
            errors.append("SECRET_KEY must be set in production")
        else:
            warnings.append("Using default SECRET_KEY (change for production)")
    
    # Check database URL
    db_url = get_database_url()
    if not db_url:
        errors.append("Database URL must be configured")
    
    # Check DataLad base path
    datalad_path = get_datalad_base_path()
    if not os.path.exists(datalad_path):
        try:
            os.makedirs(datalad_path, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create DataLad base path: {e}")
    
    # Check upload folder
    upload_folder = get_upload_folder()
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload folder: {e}")
    
    # Check feature flags
    feature_flags = get_feature_flags()
    if feature_flags['datalad_integration'] and not os.environ.get('DATALAD_AVAILABLE'):
        warnings.append("DataLad integration enabled but DataLad may not be available")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def load_env_file(env_file: str = '.env') -> None:
    """
    Load environment variables from a file.
    
    Args:
        env_file: Path to the environment file
    """
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
