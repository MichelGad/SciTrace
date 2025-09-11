"""
Configuration classes for SciTrace

Provides environment-specific configuration settings.
"""

import os
from pathlib import Path


class Config:
    """Base configuration class."""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///scitrace.db'
    
    # DataLad settings
    DATALAD_BASE_PATH = os.environ.get('DATALAD_BASE_PATH') or os.path.join(os.path.expanduser('~'), 'scitrace_demo_datasets')
    DATALAD_TIMEOUT = int(os.environ.get('DATALAD_TIMEOUT', '300'))
    
    # File upload settings
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16')) * 1024 * 1024  # 16MB default
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.expanduser('~'), 'scitrace_uploads')
    
    # Security settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE') or 'scitrace.log'
    
    # API settings
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100 per hour')
    
    # Cache settings
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # Email settings (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # External service settings
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')
    
    # Feature flags
    ENABLE_DATALAD_INTEGRATION = os.environ.get('ENABLE_DATALAD_INTEGRATION', 'true').lower() in ['true', 'on', '1']
    ENABLE_GIT_OPERATIONS = os.environ.get('ENABLE_GIT_OPERATIONS', 'true').lower() in ['true', 'on', '1']
    ENABLE_FILE_UPLOADS = os.environ.get('ENABLE_FILE_UPLOADS', 'true').lower() in ['true', 'on', '1']
    ENABLE_API_DOCUMENTATION = os.environ.get('ENABLE_API_DOCUMENTATION', 'true').lower() in ['true', 'on', '1']
    
    # Performance settings
    DATABASE_POOL_SIZE = int(os.environ.get('DATABASE_POOL_SIZE', '10'))
    DATABASE_POOL_TIMEOUT = int(os.environ.get('DATABASE_POOL_TIMEOUT', '20'))
    DATABASE_POOL_RECYCLE = int(os.environ.get('DATABASE_POOL_RECYCLE', '3600'))
    
    # Monitoring settings
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'false').lower() in ['true', 'on', '1']
    METRICS_ENDPOINT = os.environ.get('METRICS_ENDPOINT', '/metrics')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs(Config.DATALAD_BASE_PATH, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Set up logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                os.path.join('logs', Config.LOG_FILE),
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
            app.logger.info('SciTrace startup')


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///scitrace_dev.db'
    
    # More permissive settings for development
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    
    # Enable debug toolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    
    # Development logging
    LOG_LEVEL = 'DEBUG'
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('SciTrace running in development mode')


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///scitrace_prod.db'
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    WTF_CSRF_ENABLED = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Performance settings
    DATABASE_POOL_SIZE = 20
    DATABASE_POOL_TIMEOUT = 30
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('SciTrace running in production mode')


class TestingConfig(Config):
    """Testing configuration."""
    
    DEBUG = False
    TESTING = True
    
    # Testing-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Disable external services for testing
    ENABLE_DATALAD_INTEGRATION = False
    ENABLE_GIT_OPERATIONS = False
    
    # Testing logging
    LOG_LEVEL = 'ERROR'
    
    # Use temporary directories for testing
    DATALAD_BASE_PATH = os.path.join(os.path.expanduser('~'), 'scitrace_test_datasets')
    UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'scitrace_test_uploads')
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('SciTrace running in testing mode')


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
