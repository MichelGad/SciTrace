"""
Authentication routes for SciTrace

Handles user login, logout, and authentication.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import subprocess
import os

from ..models import User, db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard.index')
            
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, name, password, confirm_password]):
            flash('All fields are required', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            # Create new user
            user = User(
                username=username,
                email=email,
                name=name,
                password_hash=generate_password_hash(password),
                role='user'
            )
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/profile')
@login_required
def profile():
    """Show user profile."""
    return render_template('auth/profile.html', user=current_user)

@bp.route('/shutdown', methods=['POST'])
@login_required
def shutdown():
    """Shutdown the Flask application using stop_flask.py script."""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        stop_script_path = os.path.join(project_root, 'stop_flask.py')
        
        # Check if the script exists
        if not os.path.exists(stop_script_path):
            return jsonify({'success': False, 'message': 'Stop script not found'}), 500
        
        # Execute the stop script
        result = subprocess.run(['python3', stop_script_path], 
                              capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': 'Flask application shutdown initiated'})
        else:
            return jsonify({'success': False, 'message': f'Error: {result.stderr}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
