"""
Configuration file for Team Task Manager application.
Handles database configuration and environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # Use DATABASE_URL from environment (Railway) or fallback to local PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/team_task_manager'
    
    # Disable track modifications to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login configuration
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration for Railway deployment."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Enable for HTTPS


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
