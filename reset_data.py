#!/usr/bin/env python3
"""
SciTrace - Data Reset Utility

Command-line utility to reset all projects and dataflows.
Useful for development and testing purposes.
"""

import os
import sys
import shutil
from scitrace import create_app
from scitrace.models import Project, Task, Dataflow, User, db

def reset_all_data():
    """Reset all projects, tasks, and dataflows for all users."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting data reset...")
            
            # Count existing data
            project_count = Project.query.count()
            task_count = Task.query.count()
            dataflow_count = Dataflow.query.count()
            
            print(f"📊 Found {project_count} projects, {task_count} tasks, {dataflow_count} dataflows")
            
            if project_count == 0 and task_count == 0 and dataflow_count == 0:
                print("✅ No data to reset. Database is already empty.")
                return
            
            # Get all projects to delete their datasets
            all_projects = Project.query.all()
            
            # Delete physical DataLad datasets first
            for project in all_projects:
                if project.dataset_path and os.path.exists(project.dataset_path):
                    try:
                        shutil.rmtree(project.dataset_path)
                        print(f"🗑️  Deleted dataset directory: {project.dataset_path}")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete dataset directory {project.dataset_path}: {e}")
            
            # Delete all tasks first (due to foreign key constraints)
            Task.query.delete()
            print("🗑️  Deleted all tasks")
            
            # Delete all dataflows
            Dataflow.query.delete()
            print("🗑️  Deleted all dataflows")
            
            # Delete all projects
            Project.query.delete()
            print("🗑️  Deleted all projects")
            
            # Commit changes
            db.session.commit()
            print("✅ Data reset completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during reset: {e}")
            sys.exit(1)

def reset_user_data(user_id):
    """Reset all projects, tasks, and dataflows for a specific user."""
    app = create_app()
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"❌ User with ID {user_id} not found")
                return
            
            print(f"🔄 Starting data reset for user: {user.name} (ID: {user_id})")
            
            # Get user's projects
            user_projects = Project.query.filter_by(admin_id=user_id).all()
            
            if not user_projects:
                print("✅ No data to reset for this user.")
                return
            
            # Delete physical DataLad datasets first
            for project in user_projects:
                if project.dataset_path and os.path.exists(project.dataset_path):
                    try:
                        shutil.rmtree(project.dataset_path)
                        print(f"🗑️  Deleted dataset directory: {project.dataset_path}")
                    except Exception as e:
                        print(f"⚠️  Warning: Could not delete dataset directory {project.dataset_path}: {e}")
            
            # Delete all tasks for these projects
            for project in user_projects:
                Task.query.filter_by(project_id=project.id).delete()
            
            # Delete all dataflows for these projects
            for project in user_projects:
                Dataflow.query.filter_by(project_id=project.id).delete()
            
            # Delete all projects for the user
            Project.query.filter_by(admin_id=user_id).delete()
            
            # Commit changes
            db.session.commit()
            print(f"✅ Data reset completed for user {user.name}!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during reset: {e}")
            sys.exit(1)

def list_users():
    """List all users in the database."""
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in database.")
            return
        
        print("👥 Users in database:")
        for user in users:
            project_count = Project.query.filter_by(admin_id=user.id).count()
            print(f"  ID: {user.id}, Name: {user.name}, Username: {user.username}, Projects: {project_count}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python reset_data.py all                    # Reset all data")
        print("  python reset_data.py user <user_id>         # Reset data for specific user")
        print("  python reset_data.py list                   # List all users")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'all':
        reset_all_data()
    elif command == 'user':
        if len(sys.argv) < 3:
            print("❌ Please provide a user ID")
            sys.exit(1)
        try:
            user_id = int(sys.argv[2])
            reset_user_data(user_id)
        except ValueError:
            print("❌ User ID must be a number")
            sys.exit(1)
    elif command == 'list':
        list_users()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


