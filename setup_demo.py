#!/usr/bin/env python3
"""
Demo Setup Script for SciTrace

Creates a comprehensive demo environment with the DOM ENV Model dataflow
as shown in the application screenshot.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scitrace import create_app
from scitrace.models import db, User, Project, Task, Dataflow

def create_demo_dataset(dataset_path):
    """Create the DOM ENV Model dataset structure with sample files matching the spider web image."""
    os.makedirs(dataset_path, exist_ok=True)
    
    # Create sample files for each stage matching the new structure
    sample_files = {
        "raw_data": [
            ("ic_ft_icr_ms/run_data.csv", "mz,Intensity,Retention_Time\n123.456,1500,2.34\n234.567,2200,3.45\n345.678,1800,4.12"),
            ("water_parameters/measurements.csv", "Temperature,pH,Conductivity,Dissolved_Oxygen\n25.5,7.2,450,8.1\n26.1,7.0,445,7.9\n24.8,7.4,460,8.3")
        ],
        "preprocessed": [
            ("filtered_data.csv", "Sample_ID,Temperature,pH,Conductivity,Quality_Score\nS001,25.5,7.2,450,0.98\nS002,26.1,7.0,445,0.95"),
            ("cleaned_data.csv", "Sample_ID,Temperature,pH,Conductivity,Outlier_Flag\nS001,25.5,7.2,450,0\nS002,26.1,7.0,445,0\nS003,24.8,7.4,460,0")
        ],
        "scripts": [
            ("data_cleaning.py", "#!/usr/bin/env python3\nimport pandas as pd\nimport numpy as np\n\n# Data cleaning script\ndef clean_data(input_file, output_file):\n    df = pd.read_csv(input_file)\n    # Remove outliers\n    df = df[df['Quality_Score'] > 0.9]\n    df.to_csv(output_file, index=False)\n    print(f'Cleaned data saved to {output_file}')\n"),
            ("analysis.py", "#!/usr/bin/env python3\nimport pandas as pd\nfrom sklearn.ensemble import RandomForestRegressor\n\n# Analysis script\ndef run_analysis(data_file):\n    df = pd.read_csv(data_file)\n    # Perform analysis\n    print('Analysis completed')\n"),
            ("visualization.py", "#!/usr/bin/env python3\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\n# Visualization script\ndef create_plots(data_file):\n    df = pd.read_csv(data_file)\n    # Create plots\n    plt.figure(figsize=(10, 6))\n    sns.heatmap(df.corr(), annot=True)\n    plt.savefig('plots/correlation_heatmap.png')\n    print('Plots created')\n")
        ],
        "results": [
            ("final_report.md", "# Final Research Report\n\n## Summary\nThis report presents the findings from the environmental data analysis.\n\n## Key Results\n- Temperature shows highest correlation with outcomes\n- Random Forest model achieved 94% accuracy\n- Feature importance analysis completed\n\n## Methodology\n1. Data collection from multiple sources\n2. Preprocessing and cleaning\n3. Statistical analysis\n4. Machine learning modeling\n5. Visualization and reporting"),
            ("analysis_summary.csv", "Metric,Value\nAccuracy,0.94\nPrecision,0.92\nRecall,0.95\nF1_Score,0.93\nFeature_Importance_Temperature,0.45\nFeature_Importance_pH,0.32\nFeature_Importance_Conductivity,0.23"),
            ("model_performance.json", '{\n  "model_type": "RandomForest",\n  "accuracy": 0.94,\n  "precision": 0.92,\n  "recall": 0.95,\n  "f1_score": 0.93,\n  "feature_importance": {\n    "Temperature": 0.45,\n    "pH": 0.32,\n    "Conductivity": 0.23\n  }\n}')
        ],
        "plots": [
            ("correlation_heatmap.png", "# PNG image file - Correlation heatmap\n# Shows correlations between all variables\n# Resolution: 1200x800 pixels"),
            ("feature_importance_plot.png", "# PNG image file - Feature importance plot\n# Shows feature effects on predictions\n# Resolution: 1200x800 pixels"),
            ("partial_dependence_plots.png", "# PNG image file - Partial dependence plots\n# Shows feature effects on predictions\n# Resolution: 1200x800 pixels"),
            ("regression_tree_plots.png", "# PNG image file - Decision tree visualization\n# Shows tree structure and splits\n# Resolution: 1000x600 pixels")
        ]
    }
    
    # Create directories and files
    for stage, files in sample_files.items():
        stage_path = os.path.join(dataset_path, stage)
        os.makedirs(stage_path, exist_ok=True)
        
        for filename, content in files:
            # Handle nested directories in filename
            file_path = os.path.join(stage_path, filename)
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Created: {stage}/{filename}")
    
    # Create README
    readme_path = os.path.join(dataset_path, "README.md")
    with open(readme_path, 'w') as f:
        f.write("""# DOM ENV Model Dataset

Environmental data analysis project for water quality assessment.

## Directory Structure
- `raw_data/` - Original water quality measurements and MS data
  - `ic_ft_icr_ms/` - Mass spectrometry data
  - `water_parameters/` - Water quality measurements
- `preprocessed/` - Cleaned and filtered data
- `scripts/` - Analysis and processing scripts
- `results/` - Final reports and analysis outputs
- `plots/` - Generated visualizations and charts

## Project Information
- Created: 2024-01-15
- Dataset Path: """ + dataset_path + """
- Managed by: SciTrace
""")
    
    print(f"✅ Created demo dataset at: {dataset_path}")

def create_demo_dataflow():
    """Create the DOM ENV Model dataflow visualization as a spider web."""
    
    # Define the nodes based on the new spider web structure
    nodes = [
        # Central Dataset Root (Green)
        {"id": 1, "label": "Dataset Root", "type": "dataset_root", "path": "", "color": "#4CAF50", "description": "Root of the research dataset", "is_central": True},
        
        # Main directories with distinct colors
        {"id": 2, "label": "raw_data\n(2 files)", "type": "raw_data", "path": "raw_data", "color": "#87CEEB", "description": "Raw data files", "is_central": False},
        {"id": 3, "label": "preprocessed\n(2 files)", "type": "preprocessed", "path": "preprocessed", "color": "#90EE90", "description": "Preprocessed data files", "is_central": False},
        {"id": 4, "label": "scripts\n(3 files)", "type": "scripts", "path": "scripts", "color": "#4CAF50", "description": "Analysis and processing scripts", "is_central": False},
        {"id": 5, "label": "results\n(3 files)", "type": "results", "path": "results", "color": "#FFA07A", "description": "Final results and outputs", "is_central": False},
        {"id": 6, "label": "plots\n(4 files)", "type": "plots", "path": "plots", "color": "#DDA0DD", "description": "Generated visualizations", "is_central": False},
        
        # Subdirectories under raw_data
        {"id": 7, "label": "ic_ft_icr_ms\n(1 file)", "type": "raw_data", "path": "raw_data/ic_ft_icr_ms", "color": "#87CEEB", "description": "Mass spectrometry data", "is_central": False},
        {"id": 8, "label": "water_parameters\n(1 file)", "type": "raw_data", "path": "raw_data/water_parameters", "color": "#87CEEB", "description": "Water quality measurements", "is_central": False}
    ]
    
    # Define the edges (spider web connections)
    edges = [
        # Connections from Dataset Root to main directories (Subtle gray edges)
        {"from": 1, "to": 2, "arrows": "to", "label": "contains", "color": "#666"},
        {"from": 1, "to": 3, "arrows": "to", "label": "contains", "color": "#666"},
        {"from": 1, "to": 4, "arrows": "to", "label": "contains", "color": "#666"},
        {"from": 1, "to": 5, "arrows": "to", "label": "contains", "color": "#666"},
        {"from": 1, "to": 6, "arrows": "to", "label": "contains", "color": "#666"},
        
        # Connections from raw_data to subdirectories (Subtle gray edges)
        {"from": 2, "to": 7, "arrows": "to", "label": "contains", "color": "#666"},
        {"from": 2, "to": 8, "arrows": "to", "label": "contains", "color": "#666"}
    ]
    
    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "dataset_path": os.path.join(os.path.expanduser("~"), "scitrace_datasets", "DOM_ENV_MODEL"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "workflow_type": "spider_web_directory",
            "total_stages": len(nodes),
            "total_connections": len(edges),
            "description": "Directory structure visualization as spider web with Dataset Root as central node",
            "visualization_type": "spider_web"
        }
    }

def setup_demo():
    """Set up the complete demo environment."""
    print("🚀 Setting up SciTrace Demo Environment")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Ensure database is created
        db.create_all()
        
        # Get or create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("❌ Admin user not found. Please run the installation script first.")
            return
        
        print(f"✅ Using admin user: {admin_user.name}")
        
        # Create demo project (without DataLad dataset initially)
        project = Project.query.filter_by(name="DOM ENV Model").first()
        if not project:
            project = Project(
                project_id="DOM_ENV_MODEL",
                name="DOM ENV Model",
                description="Environmental data analysis project for water quality assessment using machine learning and statistical analysis",
                admin_id=admin_user.id,
                collaborators=json.dumps(["Environmental Research Team", "Data Science Lab"]),
                dataset_path=None,  # No dataset created yet
                status="ongoing"
            )
            db.session.add(project)
            db.session.commit()
            print("✅ Created demo project: DOM ENV Model")
        else:
            print("✅ Demo project already exists")
        
        # Create DataLad dataset for the project if it doesn't exist
        if not project.dataset_path:
            from scitrace.services import DataLadService
            datalad_service = DataLadService()
            
            try:
                # Create dataset in home directory
                home_dir = os.path.expanduser("~")
                dataset_path = os.path.join(home_dir, "scitrace_datasets", "DOM_ENV_MODEL")
                datalad_service.create_dataset(dataset_path, "DOM ENV Model")
                
                # Update project with dataset path
                project.dataset_path = dataset_path
                db.session.commit()
                
                print(f"✅ Created DataLad dataset at: {dataset_path}")
                
                # Create sample files in the dataset
                create_demo_dataset(dataset_path)
                
                # Add all files to DataLad
                import subprocess
                subprocess.run(['datalad', 'save', '-m', 'Add demo sample files'], cwd=dataset_path, check=True)
                
                print("✅ Created demo sample files in DataLad dataset")
                
            except Exception as e:
                print(f"⚠️ Warning: Could not create DataLad dataset: {e}")
        else:
            print(f"✅ Dataset already exists at: {project.dataset_path}")
        
        # Create demo dataflow
        dataflow = Dataflow.query.filter_by(name="DOM ENV Model Workflow").first()
        if not dataflow:
            # Generate dataflow from the dataset
            dataflow_data = create_demo_dataflow()
            
            dataflow = Dataflow(
                name="DOM ENV Model Workflow",
                description="Complete environmental data analysis workflow from raw measurements to machine learning predictions",
                project_id=project.id
            )
            
            dataflow.set_nodes(dataflow_data['nodes'])
            dataflow.set_edges(dataflow_data['edges'])
            dataflow.set_metadata(dataflow_data['metadata'])
            
            db.session.add(dataflow)
            db.session.commit()
            print("✅ Created demo dataflow: DOM ENV Model Workflow")
        else:
            print("✅ Demo dataflow already exists")
        
        # Create demo tasks
        demo_tasks = [
            {
                "title": "Data Collection",
                "description": "Collect water parameters and LC-FT-ICR MS measurements",
                "priority": "urgent",
                "status": "done"
            },
            {
                "title": "Data Preprocessing",
                "description": "Clean and filter the collected data",
                "priority": "medium",
                "status": "done"
            },
            {
                "title": "Statistical Analysis",
                "description": "Perform correlation analysis and PCA",
                "priority": "medium",
                "status": "ongoing"
            },
            {
                "title": "Machine Learning Modeling",
                "description": "Train and evaluate Random Forest model",
                "priority": "medium",
                "status": "ongoing"
            },
            {
                "title": "Visualization",
                "description": "Create plots and visualizations",
                "priority": "low",
                "status": "pending"
            }
        ]
        
        for task_data in demo_tasks:
            existing_task = Task.query.filter_by(title=task_data["title"], project_id=project.id).first()
            if not existing_task:
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    user_id=admin_user.id,
                    project_id=project.id,
                    priority=task_data["priority"],
                    status=task_data["status"]
                )
                db.session.add(task)
        
        db.session.commit()
        print("✅ Created demo tasks")
        
        print("\n🎉 Demo setup completed successfully!")
        print("\nTo explore the demo:")
        print("1. Start SciTrace: python run.py")
        print("2. Open http://localhost:5001 in your browser")
        print("3. Login with: admin / admin123")
        print("4. Go to 'Dataflow' to see the DOM ENV Model Workflow")
        print("5. Click on the dataflow to explore the interactive visualization")
        print("\nThe demo includes:")
        print("- Complete dataset structure with sample files")
        print("- Interactive dataflow visualization")
        print("- Sample tasks and project management")
        print("- Color-coded nodes matching the screenshot")

if __name__ == "__main__":
    setup_demo()
