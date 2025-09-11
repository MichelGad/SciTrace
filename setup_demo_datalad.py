#!/usr/bin/env python3
"""
SciTrace Demo Setup Script

This script creates 3 realistic research projects with DataLad integration:
1. Environmental Research (Water Quality Analysis)
2. Biomedical Research (Clinical Data Analysis) 
3. Computational Research (Machine Learning Pipeline)

Each project includes:
- DataLad dataset with proper structure
- Sample data files and scripts
- Realistic research content
- Dataflow visualization
- Database entries

Usage: python setup_demo_datalad.py
"""

import os
import sys
import subprocess
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add the scitrace package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scitrace'))

# Import required modules at the top level
from scitrace.services import DatasetCreationService, FileOperationsService, MetadataOperationsService
from scitrace.models import db, Project, Dataflow, User
from scitrace.app import create_app

def check_datalad():
    """Check if DataLad is available and working."""
    try:
        # Use full path to datalad
        datalad_path = '/opt/homebrew/bin/datalad'
        if not os.path.exists(datalad_path):
            datalad_path = 'datalad'  # fallback
        
        result = subprocess.run([datalad_path, '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ DataLad version: {result.stdout.strip()}")
        return True, result.stdout.strip()
    except FileNotFoundError:
        error_msg = "DataLad command not found. Please install DataLad first: pip install datalad"
        print(f"❌ {error_msg}")
        return False, error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"DataLad command failed: {e.stderr.strip()}"
        print(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error checking DataLad: {str(e)}"
        print(f"❌ {error_msg}")
        return False, error_msg

def create_demo_projects():
    """Create the demo project with DataLad integration."""
    
    # Demo project configuration - Environmental Water Quality Research only
    demo_projects = [
        {
            'name': 'Environmental Water Quality Research',
            'description': 'Comprehensive analysis of water quality parameters across multiple sampling sites. Includes data collection, statistical analysis, and visualization of environmental trends.',
            'research_type': 'environmental',
            'dataset_spec': '3-5/2-4',
            'seed': 42
        }
    ]
    
    created_projects = []
    
    for i, project_config in enumerate(demo_projects, 1):
        print(f"\n🌱 Creating Demo Project {i}/1: {project_config['name']}")
        print("=" * 60)
        
        try:
            # Create project using the DataLad service
            project_data = create_single_demo_project(project_config, i)
            created_projects.append(project_data)
            print(f"✅ Successfully created: {project_config['name']}")
            
        except Exception as e:
            print(f"❌ Failed to create project {project_config['name']}: {e}")
            continue
    
    return created_projects

def create_single_demo_project(project_config, project_num):
    """Create a single demo project with DataLad dataset."""
    
    try:
        # Create Flask app context
        print(f"     🔧 Initializing Flask app context...")
        app = create_app()
        
        with app.app_context():
            # Get admin user (assuming it exists)
            print(f"     👤 Setting up admin user...")
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                # Create admin user if it doesn't exist
                admin_user = User(
                    username='admin',
                    email='admin@scitrace.local',
                    password_hash='admin123',  # This should be hashed in production
                    name='Admin User',
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"     ✅ Created admin user")
            else:
                print(f"     ✅ Found existing admin user")
            
            # Create project in database
            print(f"     📊 Creating project in database...")
            project = Project(
                project_id=f"DEMO{project_num:03d}",
                name=project_config['name'],
                description=project_config['description'],
                admin_id=admin_user.id,
                collaborators=json.dumps(['demo_user@scitrace.local']),
                status='ongoing',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.session.add(project)
            db.session.commit()
            print(f"     ✅ Project created in database: {project.project_id}")
            
            # Create DataLad dataset
            print(f"     🗂️ Initializing DataLad service...")
            dataset_service = DatasetCreationService()
            
            # Generate unique dataset path
            dataset_name = f"demo_{project_config['research_type']}_{project_num}"
            dataset_path = os.path.join(dataset_service.base_path, dataset_name)
            
            print(f"     📁 Creating DataLad dataset at: {dataset_path}")
            
            # Check if dataset path already exists and clean it up
            if os.path.exists(dataset_path):
                print(f"     🧹 Cleaning up existing dataset at: {dataset_path}")
                try:
                    import shutil
                    shutil.rmtree(dataset_path)
                    print(f"     ✅ Successfully cleaned up existing dataset")
                except Exception as e:
                    print(f"     ⚠️ Warning: Could not clean up existing dataset: {e}")
                    # Try to use a different name
                    import time
                    timestamp = int(time.time())
                    dataset_name = f"demo_{project_config['research_type']}_{project_num}_{timestamp}"
                    dataset_path = os.path.join(dataset_service.base_path, dataset_name)
                    print(f"     📁 Using alternative dataset path: {dataset_path}")
            
            # Create dataset using create-test-dataset
            dataset_info = dataset_service.create_dataset(
                dataset_path=dataset_path,
                name=project_config['name'],
                research_type=project_config['research_type']
            )
            
            print(f"     ✅ Dataset created successfully")
            
            # Add research content (simplified version without pandas dependency)
            print(f"     📝 Adding research content...")
            add_simple_research_content(
                dataset_path=dataset_path,
                research_type=project_config['research_type'],
                project_name=project_config['name']
            )
            
            # Update project with dataset path
            print(f"     🔗 Linking project to dataset...")
            project.dataset_path = dataset_path
            db.session.commit()
            
            # Create dataflow for visualization using actual dataset structure
            print(f"     🔄 Creating dataflow visualization...")
            dataflow = create_demo_dataflow_from_dataset(project, dataset_path)
            db.session.add(dataflow)
            db.session.commit()
            
            print(f"     ✅ Created dataflow: {dataflow.name}")
            
            return {
                'project': project,
                'dataflow': dataflow,
                'dataset_path': dataset_path,
                'dataset_info': dataset_info,
                'project_name': project.name,
                'dataflow_name': dataflow.name
            }
            
    except Exception as e:
        error_msg = f"Failed to create demo project '{project_config['name']}': {str(e)}"
        print(f"     ❌ {error_msg}")
        raise Exception(error_msg)

def add_simple_research_content(dataset_path, research_type, project_name):
    """Add research-specific content to the dataset without external dependencies."""
    print(f"Adding {research_type} research content to {os.path.basename(dataset_path)}...")
    
    # Create research-specific directories and files
    research_structure = {
        "environmental": {
            "raw_data": ["water_samples.csv", "air_quality.csv", "soil_samples.csv"],
            "scripts": ["data_cleaning.py", "statistical_analysis.py", "visualization.py"],
            "results": ["water_quality_report.txt", "statistical_summary.txt", "correlation_analysis.txt"],
            "plots": ["water_quality_trends.txt", "correlation_heatmap.txt", "geographic_distribution.txt"]
        },
        "biomedical": {
            "raw_data": ["patient_records.csv", "lab_results.csv", "imaging_data.csv"],
            "scripts": ["data_preprocessing.py", "statistical_tests.py", "machine_learning.py"],
            "results": ["clinical_analysis_report.txt", "statistical_results.txt", "ml_model_performance.txt"],
            "plots": ["patient_demographics.txt", "treatment_outcomes.txt", "feature_importance.txt"]
        },
        "computational": {
            "raw_data": ["training_data.csv", "validation_data.csv", "test_data.csv"],
            "scripts": ["model_training.py", "hyperparameter_tuning.py", "evaluation.py"],
            "results": ["model_performance.txt", "training_metrics.txt", "hyperparameter_results.txt"],
            "plots": ["training_curves.txt", "confusion_matrix.txt", "feature_importance.txt"]
        },
        "general": {
            "raw_data": ["input_data.csv", "reference_data.csv"],
            "scripts": ["main_analysis.py", "data_processing.py", "visualization.py"],
            "results": ["analysis_report.txt", "results_summary.txt", "output_data.txt"],
            "plots": ["main_results.txt", "data_overview.txt", "analysis_charts.txt"]
        }
    }
    
    if research_type not in research_structure:
        research_type = "general"
    
    dirs = research_structure[research_type]
    
    for dir_name, files in dirs.items():
        dir_path = os.path.join(dataset_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        
        # Create sample files
        for filename in files:
            file_path = os.path.join(dir_path, filename)
            
            if filename.endswith('.py'):
                content = create_simple_python_script(filename, research_type, project_name)
            elif filename.endswith('.csv'):
                content = create_simple_csv_data(filename, research_type)
            elif filename.endswith('.txt'):
                content = create_simple_text_file(filename, research_type, project_name)
            else:
                # For other files, create placeholder content
                content = f"# {filename}\n\nThis is a sample {filename} file for {research_type} research.\n\nGenerated by SciTrace for project: {project_name}\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            # Make Python scripts executable
            if filename.endswith('.py'):
                os.chmod(file_path, 0o755)
            
            print(f"     ✅ Created: {dir_name}/{filename}")
    
    # Create project-specific README (skip if already exists as symlink)
    readme_path = os.path.join(dataset_path, 'README.md')
    if not os.path.islink(readme_path):
        create_simple_project_readme(dataset_path, project_name, research_type)
    else:
        print(f"     ⚠️ Skipping README.md creation (already exists as symlink)")
    
    # Create .gitignore file (skip if already exists as symlink)
    gitignore_path = os.path.join(dataset_path, '.gitignore')
    if not os.path.islink(gitignore_path):
        create_gitignore_file(dataset_path)
    else:
        print(f"     ⚠️ Skipping .gitignore creation (already exists as symlink)")
    
    # Add all files to DataLad
    try:
        subprocess.run(['datalad', 'save', '-m', f'Add research content for {project_name} ({research_type})'], 
                     cwd=dataset_path, check=True, capture_output=True)
        print(f"     🔄 Saved to DataLad: {os.path.basename(dataset_path)}")
    except subprocess.CalledProcessError as e:
        print(f"     ⚠️ Warning: Could not save to DataLad: {e}")

def create_simple_python_script(filename, research_type, project_name):
    """Create a simple Python script without external dependencies."""
    if "cleaning" in filename.lower():
        return f'''#!/usr/bin/env python3
"""
Data Cleaning Script for {research_type.title()} Research
Project: {project_name}
Generated by SciTrace
"""

import csv
import os
from datetime import datetime

def clean_data(input_file, output_file):
    """Clean and preprocess the input data."""
    print(f"Loading data from {{input_file}}...")
    
    # Load data
    try:
        with open(input_file, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        print(f"Loaded {{len(data)}} rows")
    except Exception as e:
        print(f"Error loading data: {{e}}")
        return None
    
    # Basic cleaning
    cleaned_data = []
    for row in data:
        if row and any(cell.strip() for cell in row):  # Remove empty rows
            cleaned_data.append(row)
    
    # Save cleaned data
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(cleaned_data)
    
    print(f"Cleaned data saved to {{output_file}}")
    return cleaned_data

if __name__ == "__main__":
    import sys
    
    print("Data cleaning script for {research_type} research")
    print("Project: {project_name}")
    print("Generated: {datetime.now()}")
    
    # Get command line arguments
    if len(sys.argv) < 3:
        print("Usage: python3 data_cleaning.py <input_file> <output_file>")
        print("Example: python3 data_cleaning.py raw_data/water_samples.csv results/cleaned_data.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {{output_dir}}")
    
    # Clean the data
    cleaned_data = clean_data(input_file, output_file)
    
    if cleaned_data:
        print(f"✅ Successfully cleaned {{len(cleaned_data)}} rows of data")
        print(f"📁 Input: {{input_file}}")
        print(f"📁 Output: {{output_file}}")
    else:
        print("❌ Data cleaning failed")
        sys.exit(1)
'''
    elif "analysis" in filename.lower():
        return f'''#!/usr/bin/env python3
"""
Statistical Analysis Script for {research_type.title()} Research
Project: {project_name}
Generated by SciTrace
"""

import csv
import statistics
from datetime import datetime

def analyze_data(input_file):
    """Perform basic statistical analysis."""
    print(f"Analyzing data from {{input_file}}...")
    
    try:
        with open(input_file, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        
        if len(data) < 2:
            print("Not enough data for analysis")
            return
        
        # Basic statistics
        numeric_data = []
        for row in data[1:]:  # Skip header
            for cell in row:
                try:
                    numeric_data.append(float(cell))
                except ValueError:
                    continue
        
        if numeric_data:
            print(f"Data points: {{len(numeric_data)}}")
            print(f"Mean: {{statistics.mean(numeric_data):.2f}}")
            print(f"Median: {{statistics.median(numeric_data):.2f}}")
            print(f"Standard deviation: {{statistics.stdev(numeric_data):.2f}}")
        else:
            print("No numeric data found for analysis")
            
    except Exception as e:
        print(f"Error during analysis: {{e}}")

if __name__ == "__main__":
    print("Statistical analysis script for {research_type} research")
    print("Project: {project_name}")
    print("Generated: {datetime.now()}")
'''
    else:
        return f'''#!/usr/bin/env python3
"""
{filename.replace('.py', '').replace('_', ' ').title()} Script for {research_type.title()} Research
Project: {project_name}
Generated by SciTrace
"""

from datetime import datetime

def main():
    """Main function for {filename}."""
    print("Script: {filename}")
    print("Research Type: {research_type}")
    print("Project: {project_name}")
    print("Generated: {datetime.now()}")
    print("This is a sample script for demonstration purposes.")

if __name__ == "__main__":
    main()
'''

def create_simple_csv_data(filename, research_type):
    """Create simple CSV data files."""
    if "water" in filename.lower():
        return """date,temperature,ph,turbidity,conductivity
2024-01-01,15.2,7.1,2.3,450
2024-01-02,14.8,7.3,1.9,445
2024-01-03,16.1,7.0,2.8,460
2024-01-04,15.7,7.2,2.1,452
2024-01-05,14.9,7.4,1.7,438"""
    elif "air" in filename.lower():
        return """timestamp,pm25,pm10,co2,temperature,humidity
2024-01-01T08:00:00,12,25,420,22.5,65
2024-01-01T12:00:00,15,32,450,24.1,58
2024-01-01T16:00:00,18,38,480,25.3,52
2024-01-01T20:00:00,14,29,435,23.8,61
2024-01-02T08:00:00,11,23,415,21.9,68"""
    elif "patient" in filename.lower():
        return """patient_id,age,gender,diagnosis,treatment,outcome
P001,45,F,Hypertension,Medication,Improved
P002,62,M,Diabetes,Diet+Exercise,Stable
P003,38,F,Asthma,Inhaler,Improved
P004,71,M,Heart Disease,Surgery,Recovery
P005,29,F,Anxiety,Therapy,Improved"""
    elif "training" in filename.lower():
        return """sample_id,feature1,feature2,feature3,label
S001,0.23,0.45,0.67,0
S002,0.34,0.56,0.78,1
S003,0.12,0.34,0.56,0
S004,0.67,0.89,0.12,1
S005,0.45,0.67,0.89,0"""
    else:
        return """id,value1,value2,value3,category
1,10.5,20.3,30.7,A
2,15.2,25.8,35.1,B
3,12.8,22.4,32.9,A
4,18.6,28.7,38.2,B
5,11.3,21.6,31.4,A"""

def create_simple_text_file(filename, research_type, project_name):
    """Create simple text files with sample content."""
    if "report" in filename.lower():
        return f"""Report: {filename.replace('.txt', '').replace('_', ' ').title()}
Project: {project_name}
Research Type: {research_type.title()}
Generated: {datetime.now()}

This is a sample report file demonstrating the research workflow.
The report contains analysis results and findings from the {research_type} research project.

Key Findings:
- Sample data was collected and processed
- Basic analysis was performed
- Results were documented and visualized

Next Steps:
- Review and validate results
- Prepare for publication
- Plan follow-up studies

Generated by SciTrace Demo Setup
"""
    elif "plot" in filename.lower():
        return f"""Plot Description: {filename.replace('.txt', '').replace('_', ' ').title()}
Project: {project_name}
Research Type: {research_type.title()}
Generated: {datetime.now()}

This file describes a visualization plot for the research project.
In a real scenario, this would contain the actual plot image.

Plot Details:
- Type: {filename.replace('.txt', '').replace('_', ' ').title()}
- Data Source: {research_type} research data
- Purpose: Demonstrate research findings
- Format: Visualization chart

Generated by SciTrace Demo Setup
"""
    else:
        return f"""File: {filename}
Project: {project_name}
Research Type: {research_type.title()}
Generated: {datetime.now()}

This is a sample file for demonstration purposes.
Content would vary based on the specific research needs.

Generated by SciTrace Demo Setup
"""

def create_gitignore_file(dataset_path):
    """Create a .gitignore file with common patterns."""
    gitignore_content = """# macOS system files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# R
.Rhistory
.RData
.Ruserdata

# Temporary files
*.tmp
*.temp
*.log

# Data files (uncomment if you want to ignore large data files)
# *.csv
# *.xlsx
# *.h5
# *.hdf5
"""
    
    gitignore_path = os.path.join(dataset_path, '.gitignore')
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    print(f"     ✅ Created .gitignore file")

def create_simple_project_readme(dataset_path, project_name, research_type):
    """Create a simple project README file."""
    readme_content = f"""# {project_name}

## Project Overview
This dataset contains research data and analysis for the {project_name} project.

## Research Type
{research_type.title()} Research

## Directory Structure
- `raw_data/` - Original data files
- `scripts/` - Analysis and processing scripts
- `results/` - Analysis results and outputs
- `plots/` - Visualizations and charts

## DataLad Commands
```bash
# Get the latest version
datalad get .

# Add new files
datalad save -m "Add new file"

# Save changes
datalad save -m "Description of changes"

# Check status
datalad status
```

## Project Information
- Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Dataset Path: {dataset_path}
- Research Type: {research_type.title()}
- Managed by: SciTrace

## Getting Started
1. Add your data files to the appropriate directories
2. Create analysis scripts in the scripts/ directory
3. Save your work with DataLad commands
4. Use SciTrace to visualize your dataflow

## Demo Content
This project contains sample files and scripts for demonstration purposes.
You can run the Python scripts to see basic data processing examples.
"""
        
    readme_path = os.path.join(dataset_path, 'README.md')
    with open(readme_path, 'w') as f:
        f.write(readme_content)

def create_demo_dataflow_from_dataset(project, dataset_path):
    """Create a demo dataflow for the project using actual dataset structure."""
    
    # Use MetadataOperationsService to generate dataflow from actual dataset
    metadata_service = MetadataOperationsService()
    dataflow_data = metadata_service.create_dataflow_from_dataset(dataset_path)
    
    # Create dataflow with repository view (actual file structure)
    dataflow = Dataflow(
        name=f"{project.name} - Dataflow",
        description=f"Interactive dataflow visualization for {project.name}. Shows the actual dataset structure with file organization and DataLad tracking status.",
        project_id=project.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        nodes=json.dumps(dataflow_data['nodes']),
        edges=json.dumps(dataflow_data['edges']),
        flow_metadata=json.dumps({
            'research_type': 'environmental',
            'demo_project': True,
            'created_by': 'setup_demo_datalad.py',
            'dataset_path': dataset_path,
            'node_count': len(dataflow_data['nodes']),
            'edge_count': len(dataflow_data['edges']),
            'view_type': 'repository'  # This is the repository view
        })
    )
    
    return dataflow

def create_demo_dataflow(project, project_config):
    """Create a demo dataflow for the project (legacy method - kept for reference)."""
    
    # Generate realistic nodes based on research type
    nodes = generate_demo_nodes(project_config['research_type'])
    edges = generate_demo_edges(nodes)
    
    # Create dataflow
    dataflow = Dataflow(
        name=f"{project_config['name']} - Dataflow",
        description=f"Interactive dataflow visualization for {project_config['name']}. Shows the complete research workflow from data collection to final results.",
        project_id=project.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        nodes=json.dumps(nodes),
        edges=json.dumps(edges),
        flow_metadata=json.dumps({
            'research_type': project_config['research_type'],
            'demo_project': True,
            'created_by': 'setup_demo_datalad.py',
            'node_count': len(nodes),
            'edge_count': len(edges)
        })
    )
    
    return dataflow

def generate_demo_nodes(research_type):
    """Generate realistic nodes for the dataflow based on research type."""
    
    if research_type == 'environmental':
        nodes = [
            {'id': 1, 'label': 'Water Sample Collection', 'group': 'data_collection', 'x': 100, 'y': 100},
            {'id': 2, 'label': 'Air Quality Monitoring', 'group': 'data_collection', 'x': 100, 'y': 200},
            {'id': 3, 'label': 'Soil Sample Analysis', 'group': 'data_collection', 'x': 100, 'y': 300},
            {'id': 4, 'label': 'Data Cleaning & Validation', 'group': 'processing', 'x': 300, 'y': 150},
            {'id': 5, 'label': 'Statistical Analysis', 'group': 'analysis', 'x': 500, 'y': 150},
            {'id': 6, 'label': 'Correlation Analysis', 'group': 'analysis', 'x': 500, 'y': 250},
            {'id': 7, 'label': 'Geographic Visualization', 'group': 'visualization', 'x': 700, 'y': 150},
            {'id': 8, 'label': 'Trend Analysis', 'group': 'visualization', 'x': 700, 'y': 250},
            {'id': 9, 'label': 'Final Report', 'group': 'output', 'x': 900, 'y': 200}
        ]
    elif research_type == 'biomedical':
        nodes = [
            {'id': 1, 'label': 'Patient Data Collection', 'group': 'data_collection', 'x': 100, 'y': 100},
            {'id': 2, 'label': 'Lab Results Processing', 'group': 'data_collection', 'x': 100, 'y': 200},
            {'id': 3, 'label': 'Imaging Data Analysis', 'group': 'data_collection', 'x': 100, 'y': 300},
            {'id': 4, 'label': 'Data Preprocessing', 'group': 'processing', 'x': 300, 'y': 150},
            {'id': 5, 'label': 'Statistical Tests', 'group': 'analysis', 'x': 500, 'y': 150},
            {'id': 6, 'label': 'Machine Learning Models', 'group': 'analysis', 'x': 500, 'y': 250},
            {'id': 7, 'label': 'Treatment Outcome Analysis', 'group': 'analysis', 'x': 500, 'y': 350},
            {'id': 8, 'label': 'Clinical Reports', 'group': 'output', 'x': 700, 'y': 200},
            {'id': 9, 'label': 'Patient Demographics', 'group': 'visualization', 'x': 700, 'y': 300}
        ]
    else:  # computational
        nodes = [
            {'id': 1, 'label': 'Training Data Preparation', 'group': 'data_collection', 'x': 100, 'y': 100},
            {'id': 2, 'label': 'Validation Data Split', 'group': 'data_collection', 'x': 100, 'y': 200},
            {'id': 3, 'label': 'Model Architecture', 'group': 'processing', 'x': 300, 'y': 100},
            {'id': 4, 'label': 'Hyperparameter Tuning', 'group': 'processing', 'x': 300, 'y': 200},
            {'id': 5, 'label': 'Model Training', 'group': 'analysis', 'x': 500, 'y': 100},
            {'id': 6, 'label': 'Performance Evaluation', 'group': 'analysis', 'x': 500, 'y': 200},
            {'id': 7, 'label': 'Cross-validation', 'group': 'analysis', 'x': 500, 'y': 300},
            {'id': 8, 'label': 'Model Deployment', 'group': 'output', 'x': 700, 'y': 150},
            {'id': 9, 'label': 'Performance Metrics', 'group': 'visualization', 'x': 700, 'y': 250}
        ]
    
    return nodes

def generate_demo_edges(nodes):
    """Generate edges connecting the nodes in a logical flow."""
    edges = []
    
    # Create a logical flow from left to right
    for i in range(len(nodes) - 1):
        edges.append({
            'id': i + 1,
            'from': nodes[i]['id'],
            'to': nodes[i + 1]['id'],
            'arrows': 'to',
            'smooth': {'type': 'cubicBezier'}
        })
    
    # Add some cross-connections for realism
    if len(nodes) >= 6:
        edges.append({
            'id': len(edges) + 1,
            'from': nodes[1]['id'],
            'to': nodes[4]['id'],
            'arrows': 'to',
            'smooth': {'type': 'cubicBezier'},
            'dashes': True
        })
    
    return edges

def create_sample_scripts():
    """Create additional sample scripts that can be run to see output."""
    
    scripts_dir = os.path.join(os.path.dirname(__file__), 'demo_scripts')
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Create a simple data analysis script
    analysis_script = '''#!/usr/bin/env python3
"""
Sample Data Analysis Script
Generated by SciTrace Demo Setup

This script demonstrates basic data analysis operations that you can run
to see output and understand the research workflow.
"""

import csv
import statistics
import os
from datetime import datetime

def generate_sample_data():
    """Generate sample research data."""
    import random
    random.seed(42)
    
    # Create sample dataset
    data = []
    for i in range(100):
        data.append([
            f"2024-01-{i+1:02d}",
            round(random.uniform(15, 25), 1),  # temperature
            round(random.uniform(60, 80), 1),  # humidity
            round(random.uniform(1000, 1020), 1),  # pressure
            round(random.exponential(5), 1)  # wind speed
        ])
    
    return data

def analyze_data(data):
    """Perform basic statistical analysis."""
    print("📊 Data Analysis Results")
    print("=" * 40)
    
    print(f"Dataset shape: {len(data)} rows")
    print(f"Date range: {data[0][0]} to {data[-1][0]}")
    print()
    
    # Extract numeric columns (skip date column)
    temperatures = [float(row[1]) for row in data]
    humidities = [float(row[2]) for row in data]
    pressures = [float(row[3]) for row in data]
    wind_speeds = [float(row[4]) for row in data]
    
    print("📈 Statistical Summary:")
    print(f"Temperature - Mean: {statistics.mean(temperatures):.2f}, Std: {statistics.stdev(temperatures):.2f}")
    print(f"Humidity - Mean: {statistics.mean(humidities):.2f}, Std: {statistics.stdev(humidities):.2f}")
    print(f"Pressure - Mean: {statistics.mean(pressures):.2f}, Std: {statistics.stdev(pressures):.2f}")
    print(f"Wind Speed - Mean: {statistics.mean(wind_speeds):.2f}, Std: {statistics.stdev(wind_speeds):.2f}")
    print()
    
    # Save data to CSV
    csv_path = os.path.join(os.path.dirname(__file__), 'demo_scripts', 'sample_data.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'temperature', 'humidity', 'pressure', 'wind_speed'])
        writer.writerows(data)
    
    print(f"💾 Data saved to: {csv_path}")
    return data

def main():
    """Main function to run the analysis."""
    print("🚀 Starting Sample Data Analysis")
    print("=" * 50)
    print(f"Generated at: {datetime.now()}")
    print()
    
    try:
        # Generate sample data
        print("📊 Generating sample research data...")
        data = generate_sample_data()
        print(f"✅ Generated {len(data)} data points")
        print()
        
        # Analyze the data
        analyzed_data = analyze_data(data)
        
        print("🎉 Analysis completed successfully!")
        print("📁 Check the demo_scripts directory for output files")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    # Create a simple R script
    r_script = '''#!/usr/bin/env Rscript
# Sample R Analysis Script
# Generated by SciTrace Demo Setup
#
# This script demonstrates basic R analysis operations that you can run
# to see output and understand the research workflow.

# Generate sample data
set.seed(42)
n <- 100

sample_data <- data.frame(
  x = rnorm(n, mean = 0, sd = 1),
  y = rnorm(n, mean = 0, sd = 1),
  group = sample(c("A", "B", "C"), n, replace = TRUE),
  value = rgamma(n, shape = 2, rate = 1)
)

# Basic statistics
cat("\\n📊 Data Summary\\n")
cat("===============\\n")
cat("Dataset dimensions:", nrow(sample_data), "x", ncol(sample_data), "\\n")
cat("\\nSummary statistics:\\n")
print(summary(sample_data))

# Group analysis
cat("\\n📈 Group Analysis\\n")
cat("=================\\n")
group_summary <- aggregate(value ~ group, data = sample_data, FUN = function(x) {
  c(count = length(x), mean = mean(x), sd = sd(x))
})
print(group_summary)

# Save data
write.csv(sample_data, "demo_scripts/sample_r_data.csv", row.names = FALSE)

cat("\\n✅ R analysis completed successfully!\\n")
cat("📁 Data saved to demo_scripts/sample_r_data.csv\\n")
'''
    
    # Write the scripts
    with open(os.path.join(scripts_dir, 'sample_analysis.py'), 'w') as f:
        f.write(analysis_script)
    
    with open(os.path.join(scripts_dir, 'sample_analysis.R'), 'w') as f:
        f.write(r_script)
    
    # Make scripts executable
    os.chmod(os.path.join(scripts_dir, 'sample_analysis.py'), 0o755)
    os.chmod(os.path.join(scripts_dir, 'sample_analysis.R'), 0o755)
    
    print(f"📝 Created sample scripts in: {scripts_dir}")
    return scripts_dir

def main():
    """Main function to set up the demo environment."""
    print("🚀 SciTrace Demo Environment Setup")
    print("=" * 50)
    print("This script will create 1 Environmental Water Quality Research project with:")
    print("• DataLad dataset using create-test-dataset")
    print("• Sample environmental research data and scripts")
    print("• Interactive dataflow visualization")
    print("• Database entries for SciTrace")
    print()
    
    # Check prerequisites
    datalad_available, datalad_info = check_datalad()
    if not datalad_available:
        print(f"❌ Setup failed: {datalad_info}")
        sys.exit(1)
    
    try:
        # Create demo projects
        print("🌱 Creating demo projects...")
        created_projects = create_demo_projects()
        
        if not created_projects:
            print("❌ No demo projects were created successfully")
            sys.exit(1)
        
        # Create sample scripts
        print("\n📝 Creating sample analysis scripts...")
        scripts_dir = create_sample_scripts()
        
        # Summary
        print("\n🎉 Demo Environment Setup Complete!")
        print("=" * 50)
        print(f"✅ Created {len(created_projects)} Environmental Water Quality Research project:")
        
        for i, project_data in enumerate(created_projects, 1):
            # Extract information before objects become detached
            project_name = project_data.get('project_name', f"Demo Project {i}")
            dataset_path = project_data.get('dataset_path', 'Unknown')
            dataflow_name = project_data.get('dataflow_name', f"Dataflow {i}")
            print(f"   {i}. {project_name}")
            print(f"      📁 Dataset: {dataset_path}")
            print(f"      🔄 Dataflow: {dataflow_name}")
        
        print(f"\n📝 Sample scripts created in: {scripts_dir}")
        print("\n🚀 Next Steps:")
        print("1. Start SciTrace: python run.py")
        print("2. Login with admin/admin123")
        print("3. View your Environmental Water Quality Research project in the dashboard")
        print("4. Run sample scripts to see output:")
        print(f"   • Python: python {os.path.join(scripts_dir, 'sample_analysis.py')}")
        print(f"   • R: Rscript {os.path.join(scripts_dir, 'sample_analysis.R')}")
        print("\n💡 The demo project includes realistic environmental research data and")
        print("   can be used to explore all SciTrace features!")
        
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
