"""
SciTrace Flask Application

Main application entry point with routes for dashboard and dataflow visualization.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

from .models import db, User, Project, Task, Dataflow
from .services import ProjectService

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='assets')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///scitrace.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Initialize services
    project_service = ProjectService()
    
    # Register blueprints
    from .routes import auth, dashboard, projects, dataflow, tasks
    from .routes.api import dataflow_api_bp, git_api_bp, file_api_bp, admin_api_bp, project_api_bp
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(dataflow.bp)
    app.register_blueprint(tasks.bp)
    
    # Register API blueprints
    app.register_blueprint(dataflow_api_bp)
    app.register_blueprint(git_api_bp)
    app.register_blueprint(file_api_bp)
    app.register_blueprint(admin_api_bp)
    app.register_blueprint(project_api_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                email='admin@scitrace.org',
                password_hash=generate_password_hash('admin123'),
                role='admin',
                name='Michel Gad'
            )
            db.session.add(admin_user)
            db.session.commit()
    
    return app
