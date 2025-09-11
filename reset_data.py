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
                        import subprocess
                        
                        # Method 1: Try datalad remove (proper way to remove DataLad datasets)
                        print(f"🗑️  Attempting to remove DataLad dataset: {project.dataset_path}")
                        result = subprocess.run(['datalad', 'remove', '--nocheck', '--recursive', project.dataset_path], 
                                              capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            print(f"✅ Successfully removed DataLad dataset: {project.dataset_path}")
                        else:
                            print(f"⚠️  DataLad remove failed, trying alternative methods...")
                            
                            # Method 2: Try to uninstall the dataset first, then remove
                            try:
                                uninstall_result = subprocess.run(['datalad', 'uninstall', '--recursive', project.dataset_path], 
                                                               capture_output=True, text=True, timeout=30)
                                if uninstall_result.returncode == 0:
                                    print(f"✅ Successfully uninstalled DataLad dataset: {project.dataset_path}")
                                    # Now try to remove the directory
                                    shutil.rmtree(project.dataset_path)
                                    print(f"✅ Deleted dataset directory after uninstall: {project.dataset_path}")
                                else:
                                    raise Exception("Uninstall failed")
                            except Exception as e:
                                print(f"⚠️  Uninstall method failed: {e}")
                                
                                # Method 3: Force remove with sudo (if available)
                                try:
                                    print(f"Attempting force removal with elevated permissions...")
                                    force_result = subprocess.run(['sudo', 'rm', '-rf', project.dataset_path], 
                                                                capture_output=True, text=True, timeout=30)
                                    if force_result.returncode == 0:
                                        print(f"✅ Force removed dataset directory: {project.dataset_path}")
                                    else:
                                        raise Exception("Force removal failed")
                                except Exception as e:
                                    print(f"⚠️  Force removal failed: {e}")
                                    
                                    # Method 4: Try to fix permissions and remove
                                    try:
                                        print(f"Attempting to fix permissions and remove...")
                                        # Fix permissions on git-annex objects
                                        subprocess.run(['find', project.dataset_path, '-name', '*.py', '-exec', 'chmod', '644', '{}', '+'], 
                                                     capture_output=True, timeout=30)
                                        subprocess.run(['find', project.dataset_path, '-name', '*.py', '-exec', 'chmod', '755', '{}', '+'], 
                                                     capture_output=True, timeout=30)
                                        # Now try to remove
                                        shutil.rmtree(project.dataset_path)
                                        print(f"✅ Deleted dataset directory after permission fix: {project.dataset_path}")
                                    except Exception as e:
                                        print(f"❌ All removal methods failed for {project.dataset_path}: {e}")
                                        print(f"   Manual cleanup may be required: sudo rm -rf {project.dataset_path}")
                                        
                    except subprocess.TimeoutExpired:
                        print(f"⚠️  DataLad operations timed out for {project.dataset_path}")
                    except Exception as e:
                        print(f"❌ Unexpected error removing dataset {project.dataset_path}: {e}")
            
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
                        import subprocess
                        
                        # Method 1: Try datalad remove (proper way to remove DataLad datasets)
                        print(f"🗑️  Attempting to remove DataLad dataset: {project.dataset_path}")
                        result = subprocess.run(['datalad', 'remove', '--nocheck', '--recursive', project.dataset_path], 
                                              capture_output=True, text=True, timeout=30)
                        
                        if result.returncode == 0:
                            print(f"✅ Successfully removed DataLad dataset: {project.dataset_path}")
                        else:
                            print(f"⚠️  DataLad remove failed, trying alternative methods...")
                            
                            # Method 2: Try to uninstall the dataset first, then remove
                            try:
                                uninstall_result = subprocess.run(['datalad', 'uninstall', '--recursive', project.dataset_path], 
                                                               capture_output=True, text=True, timeout=30)
                                if uninstall_result.returncode == 0:
                                    print(f"✅ Successfully uninstalled DataLad dataset: {project.dataset_path}")
                                    # Now try to remove the directory
                                    shutil.rmtree(project.dataset_path)
                                    print(f"✅ Deleted dataset directory after uninstall: {project.dataset_path}")
                                else:
                                    raise Exception("Uninstall failed")
                            except Exception as e:
                                print(f"⚠️  Uninstall method failed: {e}")
                                
                                # Method 3: Force remove with sudo (if available)
                                try:
                                    print(f"Attempting force removal with elevated permissions...")
                                    force_result = subprocess.run(['sudo', 'rm', '-rf', project.dataset_path], 
                                                                capture_output=True, text=True, timeout=30)
                                    if force_result.returncode == 0:
                                        print(f"✅ Force removed dataset directory: {project.dataset_path}")
                                    else:
                                        raise Exception("Force removal failed")
                                except Exception as e:
                                    print(f"⚠️  Force removal failed: {e}")
                                    
                                    # Method 4: Try to fix permissions and remove
                                    try:
                                        print(f"Attempting to fix permissions and remove...")
                                        # Fix permissions on git-annex objects
                                        subprocess.run(['find', project.dataset_path, '-name', '*.py', '-exec', 'chmod', '644', '{}', '+'], 
                                                     capture_output=True, timeout=30)
                                        subprocess.run(['find', project.dataset_path, '-name', '*.py', '-exec', 'chmod', '755', '{}', '+'], 
                                                     capture_output=True, timeout=30)
                                        # Now try to remove
                                        shutil.rmtree(project.dataset_path)
                                        print(f"✅ Deleted dataset directory after permission fix: {project.dataset_path}")
                                    except Exception as e:
                                        print(f"❌ All removal methods failed for {project.dataset_path}: {e}")
                                        print(f"   Manual cleanup may be required: sudo rm -rf {project.dataset_path}")
                                        
                    except subprocess.TimeoutExpired:
                        print(f"⚠️  DataLad operations timed out for {project.dataset_path}")
                    except Exception as e:
                        print(f"❌ Unexpected error removing dataset {project.dataset_path}: {e}")
            
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


