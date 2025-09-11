"""
Dataflow routes for SciTrace

Handles dataflow creation, visualization, and management.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timezone
import json
import os

from ..models import Dataflow, Project, db
from ..services import DatasetCreationService, MetadataOperationsService

bp = Blueprint('dataflow', __name__, url_prefix='/dataflow')

@bp.route('/')
@login_required
def index():
    """Show all dataflows for the current user."""
    # Get all projects for the current user
    projects = Project.query.filter_by(admin_id=current_user.id).all()
    
    # Get all dataflows for these projects
    dataflows = []
    for project in projects:
        project_dataflows = Dataflow.query.filter_by(project_id=project.id).all()
        dataflows.extend(project_dataflows)
    
    return render_template('dataflow/index.html',
                         dataflows=dataflows,
                         projects=projects,
                         user=current_user)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new dataflow."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        project_id = request.form.get('project_id')
        research_type = request.form.get('research_type', 'general')
        storage_path = request.form.get('storage_path')
        
        if not name or not project_id:
            flash('Name and project are required', 'error')
            return redirect(url_for('dataflow.create'))
        
        if not storage_path:
            flash('Storage location is required', 'error')
            return redirect(url_for('dataflow.create'))
        
        # Check if user has access to the project
        project = Project.query.get_or_404(project_id)
        if project.admin_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('dataflow.create'))
        
        try:
            # Create dataflow
            dataflow = Dataflow(
                name=name,
                description=description,
                project_id=project_id
            )
            
            # Create dataset in the selected location if project doesn't have one
            if not project.dataset_path:
                dataset_service = DatasetCreationService()
                dataset_name = f"{project.name.lower().replace(' ', '_')}_dataset"
                dataset_path = os.path.join(storage_path, dataset_name)
                
                # Create the dataset with research type
                dataset_service.create_dataset(dataset_path, project.name, research_type)
                
                # Update project with dataset path
                project.dataset_path = dataset_path
                db.session.commit()
            
            # Generate dataflow from dataset
            metadata_service = MetadataOperationsService()
            dataflow_data = metadata_service.create_dataflow_from_dataset(project.dataset_path)
            
            dataflow.set_nodes(dataflow_data['nodes'])
            dataflow.set_edges(dataflow_data['edges'])
            dataflow.set_metadata(dataflow_data['metadata'])
            
            db.session.add(dataflow)
            db.session.commit()
            
            flash('Dataflow created successfully!', 'success')
            return redirect(url_for('dataflow.view', dataflow_id=dataflow.id))
            
        except Exception as e:
            flash(f'Error creating dataflow: {str(e)}', 'error')
            return redirect(url_for('dataflow.create'))
    
    # Get user's projects for the form
    projects = Project.query.filter_by(admin_id=current_user.id).all()
    
    return render_template('dataflow/create.html',
                         projects=projects,
                         user=current_user)

@bp.route('/<int:dataflow_id>')
@login_required
def view(dataflow_id):
    """View a specific dataflow."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    return render_template('dataflow/view.html',
                         dataflow=dataflow,
                         user=current_user)

@bp.route('/<int:dataflow_id>/git-log')
@login_required
def git_log(dataflow_id):
    """View git log for a specific dataflow's dataset."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    return render_template('dataflow/git_log.html',
                         dataflow=dataflow,
                         user=current_user)

@bp.route('/<int:dataflow_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(dataflow_id):
    """Edit a dataflow."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('dataflow.edit', dataflow_id=dataflow_id))
        
        try:
            dataflow.name = name
            dataflow.description = description
            dataflow.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            flash('Dataflow updated successfully!', 'success')
            return redirect(url_for('dataflow.view', dataflow_id=dataflow.id))
            
        except Exception as e:
            flash(f'Error updating dataflow: {str(e)}', 'error')
            return redirect(url_for('dataflow.edit', dataflow_id=dataflow_id))
    
    return render_template('dataflow/edit.html',
                         dataflow=dataflow,
                         user=current_user)

@bp.route('/<int:dataflow_id>/delete', methods=['POST'])
@login_required
def delete(dataflow_id):
    """Delete a dataflow."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    try:
        db.session.delete(dataflow)
        db.session.commit()
        
        flash('Dataflow deleted successfully!', 'success')
        return redirect(url_for('dataflow.index'))
        
    except Exception as e:
        flash(f'Error deleting dataflow: {str(e)}', 'error')
        return redirect(url_for('dataflow.view', dataflow_id=dataflow_id))

@bp.route('/project/<int:project_id>')
@login_required
def project_dataflows(project_id):
    """Show all dataflows for a specific project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    # Get all dataflows for this project
    dataflows = Dataflow.query.filter_by(project_id=project_id).all()
    
    return render_template('dataflow/index.html',
                         dataflows=dataflows,
                         project=project,
                         user=current_user)

@bp.route('/project/<int:project_id>/create', methods=['GET', 'POST'])
@login_required
def create_for_project(project_id):
    """Create a new dataflow for a specific project."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    if project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        storage_path = request.form.get('storage_path')
        
        if not name:
            flash('Name is required', 'error')
            return redirect(url_for('dataflow.create_for_project', project_id=project_id))
        
        if not storage_path:
            flash('Storage location is required', 'error')
            return redirect(url_for('dataflow.create_for_project', project_id=project_id))
        
        try:
            # Create dataflow
            dataflow = Dataflow(
                name=name,
                description=description,
                project_id=project_id
            )
            
            # Create dataset in the selected location if project doesn't have one
            if not project.dataset_path:
                dataset_service = DatasetCreationService()
                dataset_name = f"{project.name.lower().replace(' ', '_')}_dataset"
                dataset_path = os.path.join(storage_path, dataset_name)
                
                # Create the dataset
                dataset_service.create_dataset(dataset_path, project.name)
                
                # Update project with dataset path
                project.dataset_path = dataset_path
                db.session.commit()
            
            # Generate dataflow from dataset
            metadata_service = MetadataOperationsService()
            dataflow_data = metadata_service.create_dataflow_from_dataset(project.dataset_path)
            
            dataflow.set_nodes(dataflow_data['nodes'])
            dataflow.set_edges(dataflow_data['edges'])
            dataflow.set_metadata(dataflow_data['metadata'])
            
            db.session.add(dataflow)
            db.session.commit()
            
            flash('Dataflow created successfully!', 'success')
            return redirect(url_for('dataflow.view', dataflow_id=dataflow.id))
            
        except Exception as e:
            flash(f'Error creating dataflow: {str(e)}', 'error')
            return redirect(url_for('dataflow.create_for_project', project_id=project_id))
    
    return render_template('dataflow/create.html',
                         project=project,
                         user=current_user)

@bp.route('/<int:dataflow_id>/lifecycle')
@login_required
def lifecycle_view(dataflow_id):
    """View the conceptual data lifecycle workflow for a dataflow."""
    dataflow = Dataflow.query.get_or_404(dataflow_id)
    
    # Check if user has access to this dataflow
    if dataflow.project.admin_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('dataflow.index'))
    
    return render_template('dataflow/lifecycle.html',
                         dataflow=dataflow,
                         user=current_user)
