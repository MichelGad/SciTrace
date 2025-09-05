"""
DataLad Services for SciTrace

Handles DataLad operations and dataset management.
"""

import os
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


class DataLadService:
    """Service for DataLad operations."""
    
    def __init__(self):
        home_dir = os.path.expanduser("~")
        self.base_path = os.environ.get('DATALAD_BASE_PATH', os.path.join(home_dir, 'scitrace_demo_datasets'))
        os.makedirs(self.base_path, exist_ok=True)
    
    def create_dataset(self, dataset_path, name=None, research_type="general"):
        """Create a new DataLad dataset at the specified path using the demo structure."""
        
        if os.path.exists(dataset_path):
            raise Exception(f"Dataset already exists at {dataset_path}")
        
        try:
            # Create DataLad dataset using create-test-dataset (like demo)
            print(f"Creating DataLad dataset at: {dataset_path}")
            
            # Use create-test-dataset for consistent structure with demo
            cmd = ['datalad', 'create-test-dataset']
            
            # Add research type specific parameters
            if research_type == "environmental":
                cmd.extend(['--spec', '3-5/2-4'])
            elif research_type == "biomedical":
                cmd.extend(['--spec', '4-6/2-3'])
            elif research_type == "computational":
                cmd.extend(['--spec', '2-4/3-5'])
            else:
                # Default structure for general research
                cmd.extend(['--spec', '3-4/2-3'])
            
            # Add seed for reproducibility
            import random
            seed = random.randint(1, 1000)
            cmd.extend(['--seed', str(seed)])
            
            cmd.append(dataset_path)
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"DataLad create-test-dataset result: {result.stdout}")
            
            # Verify dataset was created (create-test-dataset creates .git directory)
            if not os.path.exists(os.path.join(dataset_path, '.git')):
                raise Exception("DataLad dataset was not created properly - missing .git directory")
            
            # Create empty directory structure without sample files
            self.create_empty_structure(dataset_path, research_type, name)
            
            return {
                'dataset_path': dataset_path,
                'status': 'created',
                'research_type': research_type,
                'seed': seed,
                'message': f'Created empty DataLad dataset with {research_type} research structure'
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create DataLad dataset: {e.stderr}")
    
    def create_empty_structure(self, dataset_path, research_type, project_name):
        """Create empty directory structure without sample files."""
        print(f"Creating empty directory structure for {research_type} research...")
        
        # Create research-specific directories (empty)
        research_dirs = {
            "environmental": ["raw_data", "scripts", "results", "plots"],
            "biomedical": ["raw_data", "scripts", "results", "plots"],
            "computational": ["raw_data", "scripts", "results", "plots"],
            "general": ["raw_data", "scripts", "results", "plots"]
        }
        
        dirs = research_dirs.get(research_type, research_dirs["general"])
        
        for dir_name in dirs:
            dir_path = os.path.join(dataset_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            print(f"     ✅ Created empty directory: {dir_name}")
        
        # Create basic README without sample content
        self.create_basic_readme(dataset_path, project_name, research_type)
        
        # Create .gitignore file
        self.create_gitignore(dataset_path)
        
        # Add empty directories to DataLad
        try:
            subprocess.run(['datalad', 'save', '-m', f'Create empty structure for {project_name} ({research_type})'], 
                         cwd=dataset_path, check=True, capture_output=True)
            print(f"     🔄 Saved empty structure to DataLad: {os.path.basename(dataset_path)}")
        except subprocess.CalledProcessError as e:
            print(f"     ⚠️ Warning: Could not save to DataLad: {e}")
    
    def create_basic_readme(self, dataset_path, project_name, research_type):
        """Create a basic README file without sample content."""
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
"""
        
        readme_path = os.path.join(dataset_path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    def create_gitignore(self, dataset_path):
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
    
    def add_research_content(self, dataset_path, research_type, project_name):
        """Add research-specific content to the dataset."""
        print(f"Adding {research_type} research content to {os.path.basename(dataset_path)}...")
        
        # Create research-specific directories and files
        research_structure = {
            "environmental": {
                "raw_data": ["water_samples", "air_quality", "soil_samples"],
                "scripts": ["data_cleaning.py", "statistical_analysis.R", "visualization.py"],
                "results": ["water_quality_report.pdf", "statistical_summary.csv", "correlation_analysis.json"],
                "plots": ["water_quality_trends.png", "correlation_heatmap.png", "geographic_distribution.png"]
            },
            "biomedical": {
                "raw_data": ["patient_records", "lab_results", "imaging_data"],
                "scripts": ["data_preprocessing.py", "statistical_tests.R", "machine_learning.py"],
                "results": ["clinical_analysis_report.pdf", "statistical_results.csv", "ml_model_performance.json"],
                "plots": ["patient_demographics.png", "treatment_outcomes.png", "feature_importance.png"]
            },
            "computational": {
                "raw_data": ["training_data", "validation_data", "test_data"],
                "scripts": ["model_training.py", "hyperparameter_tuning.py", "evaluation.py"],
                "results": ["model_performance.pdf", "training_metrics.csv", "hyperparameter_results.json"],
                "plots": ["training_curves.png", "confusion_matrix.png", "feature_importance.png"]
            },
            "general": {
                "raw_data": ["input_data", "reference_data"],
                "scripts": ["main_analysis.py", "data_processing.py", "visualization.py"],
                "results": ["analysis_report.pdf", "results_summary.csv", "output_data.json"],
                "plots": ["main_results.png", "data_overview.png", "analysis_charts.png"]
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
                    content = self.create_python_script(filename, research_type, project_name)
                elif filename.endswith('.R'):
                    content = self.create_r_script(filename, research_type, project_name)
                elif filename.endswith('.csv'):
                    content = self.create_csv_data(filename, research_type)
                elif filename.endswith('.json'):
                    content = json.dumps(self.create_json_data(filename, research_type), indent=2)
                elif filename.endswith('.md'):
                    content = self.create_markdown_file(filename, research_type, project_name)
                else:
                    # For other files, create placeholder content
                    content = f"# {filename}\n\nThis is a sample {filename} file for {research_type} research.\n\nGenerated by SciTrace for project: {project_name}\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Make Python scripts executable
                if filename.endswith('.py'):
                    os.chmod(file_path, 0o755)
                
                print(f"     ✅ Created: {dir_name}/{filename}")
        
        # Create project-specific README
        self.create_project_readme(dataset_path, project_name, research_type)
        
        # Add all files to DataLad
        try:
            subprocess.run(['datalad', 'save', '-m', f'Add research content for {project_name} ({research_type})'], 
                         cwd=dataset_path, check=True, capture_output=True)
            print(f"     🔄 Saved to DataLad: {os.path.basename(dataset_path)}")
        except subprocess.CalledProcessError as e:
            print(f"     ⚠️ Warning: Could not save to DataLad: {e}")
    
    def create_project_readme(self, dataset_path, project_name, research_type):
        """Create a project-specific README file."""
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
"""
            
        readme_path = os.path.join(dataset_path, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)
    
    def create_python_script(self, filename, research_type, project_name):
        """Create a realistic Python script based on research type."""
        if "cleaning" in filename.lower():
            return f'''#!/usr/bin/env python3
"""
Data Cleaning Script for {research_type.title()} Research
Project: {project_name}
Generated by SciTrace
"""

import pandas as pd
import numpy as np
from pathlib import Path

def clean_data(input_file, output_file):
    """Clean and preprocess the input data."""
    print(f"Loading data from {{input_file}}...")
    
    # Load data
    try:
        data = pd.read_csv(input_file)
        print(f"Loaded {{len(data)}} rows and {{len(data.columns)}} columns")
    except Exception as e:
        print(f"Error loading data: {{e}}")
        return None
    
    # Basic cleaning
    data = data.dropna()
    data = data.drop_duplicates()
    
    # Save cleaned data
    data.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {{output_file}}")
    
    return data

if __name__ == "__main__":
    import sys
    
    print("Data cleaning script for {research_type} research")
    print("Project: {project_name}")
    print("Generated by SciTrace")
    
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
    
    if cleaned_data is not None:
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
Data Analysis Script for {research_type.title()} Research
Project: {project_name}
Generated by SciTrace
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_data(data_file):
    """Perform basic statistical analysis on the data."""
    print(f"Analyzing data from {{data_file}}...")
    
    # Load data
    data = pd.read_csv(data_file)
    
    # Basic statistics
    print("\\nData Summary:")
    print(data.describe())
    
    # Create visualizations
    plt.figure(figsize=(10, 6))
    data.hist(bins=20)
    plt.title(f"Data Distribution - {{project_name}}")
    plt.savefig("plots/data_distribution.png")
    plt.close()
    
    print("Analysis complete. Check plots/ directory for visualizations.")
    
    return data.describe()

if __name__ == "__main__":
    analyze_data("preprocessed/cleaned_data.csv")
'''
        else:
            return f'''#!/usr/bin/env python3
"""
{filename.replace('.py', '').replace('_', ' ').title()} Script
Project: {project_name}
Research Type: {research_type.title()}
Generated by SciTrace
"""

def main():
    """Main function for {filename}."""
    print(f"Running {{filename}} for {{project_name}}")
    print(f"Research type: {{research_type}}")
    
    # TODO: Implement your analysis here
    
    print("Script execution complete!")

if __name__ == "__main__":
    main()
'''
    
    def create_r_script(self, filename, research_type, project_name):
        """Create a realistic R script based on research type."""
        return f'''# {filename}
# {research_type.title()} Research Script
# Project: {project_name}
# Generated by SciTrace

# Load required libraries
library(tidyverse)
library(ggplot2)

# Set working directory
setwd("{research_type}")

# TODO: Implement your R analysis here
print("R script loaded successfully!")

# Example: Create a simple plot
# data <- data.frame(x = 1:10, y = rnorm(10))
# ggplot(data, aes(x, y)) + geom_point() + ggtitle("{project_name}")
'''
    
    def create_csv_data(self, filename, research_type):
        """Create sample CSV data based on research type."""
        import pandas as pd
        import numpy as np
        
        if "summary" in filename.lower():
            data = {
                'metric': ['mean', 'std', 'min', 'max', 'count'],
                'value': [np.random.normal(100, 20), np.random.normal(15, 5), 
                         np.random.uniform(50, 150), np.random.uniform(150, 250), 
                         np.random.randint(100, 1000)]
            }
        else:
            # Create sample data
            n_samples = np.random.randint(50, 200)
            data = {
                'id': range(1, n_samples + 1),
                'value': np.random.normal(100, 20, n_samples),
                'category': np.random.choice(['A', 'B', 'C'], n_samples),
                'timestamp': pd.date_range(start='2024-01-01', periods=n_samples, freq='D')
            }
        
        return pd.DataFrame(data).to_csv(index=False)
    
    def create_json_data(self, filename, research_type):
        """Create sample JSON data based on research type."""
        return {
            "project": f"{research_type}_research",
            "analysis_date": datetime.now().isoformat(),
            "parameters": {
                "sample_size": np.random.randint(100, 1000),
                "confidence_level": 0.95,
                "method": "standard_analysis"
            },
            "results": {
                "mean": np.random.normal(100, 20),
                "std": np.random.normal(15, 5),
                "p_value": np.random.uniform(0, 1)
            }
        }
    
    def create_markdown_file(self, filename, research_type, project_name):
        """Create a markdown file based on research type."""
        return f"""# {filename.replace('.md', '').replace('_', ' ').title()}

## Project: {project_name}
**Research Type:** {research_type.title()}

## Overview
This document contains analysis results and findings for the {project_name} project.

## Key Findings
- Sample analysis completed successfully
- Data quality assessment performed
- Statistical tests conducted

## Next Steps
1. Review results
2. Validate findings
3. Prepare final report

---
*Generated by SciTrace on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def get_dataset_info(self, dataset_path):
        """Get information about a DataLad dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Get dataset status
            result = subprocess.run(['datalad', 'status'], cwd=dataset_path, 
                                  capture_output=True, text=True, check=True)
            
            # Get dataset metadata
            meta_result = subprocess.run(['datalad', 'metadata', 'show'], cwd=dataset_path,
                                       capture_output=True, text=True)
            
            return {
                'path': dataset_path,
                'status': result.stdout,
                'metadata': meta_result.stdout if meta_result.returncode == 0 else None,
                'exists': True
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get dataset info: {e.stderr}")
    
    def get_stage_files(self, dataset_path, stage_name):
        """Get actual files and metadata for a specific stage in the dataset."""
        if not os.path.exists(dataset_path):
            return None
        
        # Handle dataset root case
        if stage_name == '.':
            stage_path = dataset_path
            display_name = 'Dataset Root'
        else:
            stage_path = os.path.join(dataset_path, stage_name)
            display_name = stage_name.replace('_', ' ').title()
        
        if not os.path.exists(stage_path):
            return {
                'stage_name': display_name,
                'path': stage_path,
                'files': [],
                'metadata': {
                    'file_count': 0,
                    'total_size': '0 B',
                    'last_modified': None,
                    'stage_type': display_name,
                    'datalad_status': 'unknown'
                }
            }
        
        try:
            files = []
            deleted_files = []
            total_size = 0
            tracked_files = 0
            untracked_files = 0
            
            # Get DataLad status for the stage directory
            datalad_status = self._get_datalad_status(dataset_path, stage_name)
            
            # Get deleted files from DataLad status
            deleted_files = self._get_deleted_files(dataset_path, stage_name)
            
            # Get all files in the stage directory
            # For dataset root, only show files directly in root, not subdirectories
            if stage_name == '.':
                # Only get files directly in the root directory
                for filename in os.listdir(stage_path):
                    file_path = os.path.join(stage_path, filename)
                    if os.path.isfile(file_path) and filename != '.DS_Store':
                        rel_path = filename
                        root = stage_path
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        total_size += file_size
                        
                        # Determine file type
                        file_ext = os.path.splitext(filename)[1].lower()
                        file_type = self._get_file_type(file_ext)
                        
                        # Check if file is tracked by DataLad
                        git_path = rel_path
                        is_tracked = self._check_file_in_git(dataset_path, git_path)
                        if is_tracked:
                            tracked_files += 1
                        else:
                            untracked_files += 1
                        
                        files.append({
                            'name': filename,
                            'path': rel_path,
                            'size': self._format_file_size(file_size),
                            'type': file_type,
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'size_bytes': file_size,
                            'tracked': is_tracked,
                            'status': 'Tracked' if is_tracked else 'Not tracked by DataLad'
                        })
            else:
                # For other stages, walk through all subdirectories
                for root, dirs, filenames in os.walk(stage_path):
                    for filename in filenames:
                        # Skip .DS_Store files
                        if filename == '.DS_Store':
                            continue
                            
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, stage_path)
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        file_size = stat.st_size
                        total_size += file_size
                        
                        # Determine file type
                        file_ext = os.path.splitext(filename)[1].lower()
                        file_type = self._get_file_type(file_ext)
                        
                        # Check if file is tracked by DataLad
                        git_path = os.path.join(stage_name, rel_path)
                        is_tracked = self._check_file_in_git(dataset_path, git_path)
                        if is_tracked:
                            tracked_files += 1
                        else:
                            untracked_files += 1
                        
                        files.append({
                            'name': filename,
                            'path': rel_path,
                            'size': self._format_file_size(file_size),
                            'type': file_type,
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'size_bytes': file_size,
                            'tracked': is_tracked,
                            'status': 'Tracked' if is_tracked else 'Not tracked by DataLad'
                        })
            
            # Sort files by size (largest first)
            files.sort(key=lambda x: x['size_bytes'], reverse=True)
            
            # Get stage metadata
            stage_stat = os.stat(stage_path)
            metadata = {
                'file_count': len(files),
                'tracked_files': tracked_files,
                'untracked_files': untracked_files,
                'deleted_files': len(deleted_files),
                'total_size': self._format_file_size(total_size),
                'last_modified': datetime.fromtimestamp(stage_stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                'stage_type': display_name,
                'path': stage_path,
                'datalad_status': 'mixed' if untracked_files > 0 else 'clean' if tracked_files > 0 else 'empty'
            }
            
            return {
                'stage_name': display_name,
                'path': stage_path,
                'files': files,
                'deleted_files': deleted_files,
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'stage_name': display_name,
                'path': stage_path,
                'error': str(e),
                'files': [],
                'metadata': {}
            }
    
    def _get_file_type(self, extension):
        """Get human-readable file type from extension."""
        type_map = {
            '.csv': 'CSV',
            '.xlsx': 'Excel',
            '.xls': 'Excel',
            '.json': 'JSON',
            '.txt': 'Text',
            '.md': 'Markdown',
            '.py': 'Python',
            '.r': 'R Script',
            '.R': 'R Script',
            '.pkl': 'Pickle',
            '.png': 'PNG Image',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.pdf': 'PDF',
            '.html': 'HTML',
            '.docx': 'Word',
            '.zip': 'ZIP Archive',
            '.gz': 'GZIP Archive',
            '.tar': 'TAR Archive'
        }
        return type_map.get(extension, 'Unknown')
    
    def _get_datalad_status(self, dataset_path, stage_name):
        """Get DataLad status for a specific stage directory."""
        try:
            # Run datalad status command for the stage directory
            stage_path = os.path.join(dataset_path, stage_name)
            result = subprocess.run(
                ['datalad', 'status', stage_path], 
                cwd=dataset_path, 
                capture_output=True, 
                text=True,
                check=False  # Don't raise exception if command fails
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                # If status fails, try to get status for the whole dataset
                result = subprocess.run(
                    ['datalad', 'status'], 
                    cwd=dataset_path, 
                    capture_output=True, 
                    text=True,
                    check=False
                )
                return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            print(f"Warning: Could not get DataLad status: {e}")
            return ""
    
    def _is_file_tracked(self, datalad_status, file_path):
        """Check if a file is tracked by DataLad based on status output."""
        # First check if file is explicitly mentioned as untracked in status
        if datalad_status and (f"?? {file_path}" in datalad_status or f"?? {file_path}/" in datalad_status):
            return False
        
        # For more reliable detection, we'll use git ls-files
        # This method will be called with the dataset_path context
        return True  # We'll refine this in the calling method
    
    def _check_file_in_git(self, dataset_path, file_path):
        """Check if a file is tracked in git (more reliable method)."""
        try:
            # Use git ls-files to check if file is tracked
            full_path = os.path.join(dataset_path, file_path)
            result = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', file_path],
                cwd=dataset_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _get_deleted_files(self, dataset_path, stage_name):
        """Get list of deleted files in a stage from DataLad status."""
        try:
            # Get DataLad status for the stage
            result = subprocess.run(
                ['datalad', 'status', stage_name],
                cwd=dataset_path,
                capture_output=True, 
                text=True,
                check=False
            )
            
            deleted_files = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('deleted:'):
                        # Extract filename from "deleted: path/to/file (symlink)"
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            file_info = parts[1].strip()
                            # Remove any additional info in parentheses
                            if '(' in file_info:
                                file_info = file_info.split('(')[0].strip()
                            # Get just the filename
                            filename = os.path.basename(file_info)
                            deleted_files.append({
                                'name': filename,
                                'path': file_info,
                                'status': 'Deleted',
                                'type': 'deleted'
                            })
            
            return deleted_files
        except Exception as e:
            print(f"Error getting deleted files: {e}")
            return []
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_file_tree(self, dataset_path):
        """Get file tree structure of a dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        def build_tree(path, relative_path=""):
            tree = []
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    relative_item_path = os.path.join(relative_path, item) if relative_path else item
                    
                    if os.path.isdir(item_path):
                        # Skip .git and .datalad directories
                        if item in ['.git', '.datalad']:
                            continue
                        
                        children = build_tree(item_path, relative_item_path)
                        tree.append({
                            'name': item,
                            'path': relative_item_path,
                            'type': 'directory',
                            'children': children
                        })
                    else:
                        # Skip .DS_Store files
                        if item == '.DS_Store':
                            continue
                            
                        tree.append({
                            'name': item,
                            'path': relative_item_path,
                            'type': 'file',
                            'size': os.path.getsize(item_path)
                        })
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(dataset_path)
    
    def add_file_to_dataset(self, dataset_path, file_path, commit_message=None):
        """Add a file to a DataLad dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        if not os.path.exists(file_path):
            raise Exception("File does not exist")
        
        try:
            # Copy file to dataset
            filename = os.path.basename(file_path)
            dest_path = os.path.join(dataset_path, filename)
            
            # Copy file
            import shutil
            shutil.copy2(file_path, dest_path)
            
            # Add to DataLad
            subprocess.run(['datalad', 'save', '-m', f'Add file: {filename}'], cwd=dataset_path, check=True, capture_output=True)
            
            # Commit if message provided
            if commit_message:
                subprocess.run(['datalad', 'save', '-m', commit_message], cwd=dataset_path, check=True, capture_output=True)
            
            return {
                'file_path': dest_path,
                'status': 'added',
                'message': f'File {filename} added to dataset'
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to add file to dataset: {e.stderr.decode()}")
    
    def create_directory_in_dataset(self, dataset_path, dir_name, commit_message=None):
        """Create a directory in a DataLad dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            dir_path = os.path.join(dataset_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            
            # Add to DataLad
            subprocess.run(['datalad', 'save', '-m', f'Add directory: {dir_name}'], cwd=dataset_path, check=True, capture_output=True)
            
            # Commit if message provided
            if commit_message:
                subprocess.run(['datalad', 'save', '-m', commit_message], cwd=dataset_path, check=True, capture_output=True)
            
            return {
                'dir_path': dir_path,
                'status': 'created',
                'message': f'Directory {dir_name} created in dataset'
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to create directory in dataset: {e.stderr.decode()}")
    
    def run_command_in_dataset(self, dataset_path, command, commit_message=None):
        """Run a command in a DataLad dataset and track changes."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            # Run command
            result = subprocess.run(command, cwd=dataset_path, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Command failed: {result.stderr}")
            
            # Add any new files to DataLad
            subprocess.run(['datalad', 'save', '-m', f'Track changes from command: {command}'], cwd=dataset_path, check=True, capture_output=True)
            
            # Commit if message provided
            if commit_message:
                subprocess.run(['datalad', 'save', '-m', commit_message], cwd=dataset_path, check=True, capture_output=True)
            
            return {
                'command': command,
                'status': 'completed',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to run command in dataset: {e.stderr.decode()}")
    
    def get_dataset_history(self, dataset_path):
        """Get the commit history of a DataLad dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            result = subprocess.run(['datalad', 'log'], cwd=dataset_path, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get dataset history: {e.stderr}")
    
    def get_dataset_status(self, dataset_path):
        """Get the current status of a DataLad dataset."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        try:
            result = subprocess.run(['datalad', 'status'], cwd=dataset_path, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to get dataset status: {e.stderr}")
    
    def create_dataflow_from_dataset(self, dataset_path):
        """Create a dataflow visualization from dataset structure as a spider web."""
        if not os.path.exists(dataset_path):
            raise Exception("Dataset path does not exist")
        
        # Get actual dataset structure
        file_tree = self.get_file_tree(dataset_path)
        
        # Analyze dataset content and create spider web workflow
        nodes = []
        edges = []
        node_id = 1
        
        # Define directory types and their colors (matching the new structure)
        directory_types = {
            'raw_data': {'color': '#87CEEB', 'type': 'raw_data', 'description': 'Raw data files'},
            'preprocessed': {'color': '#90EE90', 'type': 'preprocessed', 'description': 'Preprocessed data files'},
            'scripts': {'color': '#4CAF50', 'type': 'scripts', 'description': 'Analysis and processing scripts'},
            'results': {'color': '#FFA07A', 'type': 'results', 'description': 'Final results and outputs'},
            'plots': {'color': '#DDA0DD', 'type': 'plots', 'description': 'Generated visualizations'}
        }
        
        # Create central "Dataset Root" node (green, like in the image)
        central_node = {
            'id': node_id,
            'label': 'Dataset Root',
            'type': 'dataset_root',
            'path': dataset_path,
            'color': '#4CAF50',  # Green like in the image
            'description': 'Root of the research dataset',
            'file_count': 0,
            'is_central': True
        }
        nodes.append(central_node)
        central_node_id = node_id
        node_id += 1
        
        # Create nodes for each directory that exists
        directory_nodes = {}
        for item in file_tree:
            if item['type'] == 'directory' and item['name'] in directory_types:
                dir_type = directory_types[item['name']]
                
                # Count files in this directory and check tracking status (excluding .DS_Store)
                file_count = len([f for f in item.get('children', []) if f['type'] == 'file' and f['name'] != '.DS_Store'])
                
                # Get tracking status for this directory
                stage_data = self.get_stage_files(dataset_path, item['name'])
                tracked_count = stage_data['metadata']['tracked_files'] if stage_data else 0
                untracked_count = stage_data['metadata']['untracked_files'] if stage_data else 0
                deleted_count = stage_data['metadata']['deleted_files'] if stage_data else 0
                
                # Determine node color based on status
                base_color = dir_type['color']
                if deleted_count > 0:
                    # Red for deleted files
                    node_color = '#FF6B6B'  # Red for deleted files
                elif untracked_count > 0:
                    # Orange for untracked files
                    node_color = '#FFA500'  # Orange for warning
                else:
                    node_color = base_color
                
                # Create label with status information
                status_parts = []
                if file_count > 0:
                    status_parts.append(f"{file_count} files")
                if untracked_count > 0:
                    status_parts.append(f"{untracked_count} untracked")
                if deleted_count > 0:
                    status_parts.append(f"{deleted_count} deleted")
                
                if status_parts:
                    label = f"{item['name']}\n({', '.join(status_parts)})"
                else:
                    label = f"{item['name']}\n(0 files)"
                
                node = {
                    'id': node_id,
                    'label': label,
                    'type': dir_type['type'],
                    'path': item['path'],
                    'color': node_color,
                    'description': dir_type['description'],
                    'file_count': file_count,
                    'tracked_files': tracked_count,
                    'untracked_files': untracked_count,
                    'deleted_files': deleted_count,
                    'has_untracked': untracked_count > 0,
                    'has_deleted': deleted_count > 0,
                    'is_central': False
                }
                nodes.append(node)
                directory_nodes[item['name']] = node_id
                node_id += 1
        
        # Add missing workflow stages (even if directories don't exist yet)
        missing_stages = {
            'scripts': {'color': '#4CAF50', 'type': 'scripts', 'description': 'Analysis and processing scripts'},
            'results': {'color': '#FFA07A', 'type': 'results', 'description': 'Final results and outputs'},
            'plots': {'color': '#DDA0DD', 'type': 'plots', 'description': 'Generated visualizations'}
        }
        
        for stage_name, stage_info in missing_stages.items():
            if stage_name not in directory_nodes:
                node = {
                    'id': node_id,
                    'label': f"{stage_name}\n(0 files)",
                    'type': stage_info['type'],
                    'path': f"{stage_name}/",
                    'color': stage_info['color'],
                    'description': stage_info['description'],
                    'file_count': 0,
                    'is_central': False
                }
                nodes.append(node)
                directory_nodes[stage_name] = node_id
                node_id += 1
        
        # Create spider web connections - all directories connect to Dataset Root
        for dir_name, dir_node_id in directory_nodes.items():
            edge = {
                'from': central_node_id,
                'to': dir_node_id,
                'arrows': 'to',
                'label': 'contains',
                'color': '#666'  # Subtle gray edges
            }
            edges.append(edge)
        
        # Create connections between related directories
        # Raw data connects to subdirectories
        if 'raw_data' in directory_nodes:
            raw_data_subdirs = ['ic_ft_icr_ms', 'water_parameters']
            for subdir in raw_data_subdirs:
                if subdir in directory_nodes:
                    edge = {
                        'from': directory_nodes['raw_data'],
                        'to': directory_nodes[subdir],
                        'arrows': 'to',
                        'label': 'contains',
                        'color': '#666'
                    }
                    edges.append(edge)
        
        # If no directories found, create a basic spider web
        if len(nodes) == 1:  # Only central node exists
            basic_dirs = ['raw_data', 'preprocessed', 'scripts', 'results', 'plots']
            for dir_name in basic_dirs:
                dir_info = directory_types.get(dir_name, {'color': '#87CEEB', 'type': 'raw_data', 'description': f'{dir_name} directory'})
                node = {
                    'id': node_id,
                    'label': f"{dir_name}\n(0 files)",
                    'type': dir_info['type'],
                    'path': f"{dir_name}/",
                    'color': dir_info['color'],
                    'description': dir_info['description'],
                    'file_count': 0,
                    'is_central': False
                }
                nodes.append(node)
                
                # Connect to central node
                edge = {
                    'from': central_node_id,
                    'to': node_id,
                    'arrows': 'to',
                    'label': 'contains',
                    'color': '#666'
                }
                edges.append(edge)
                node_id += 1
        
        # Create metadata
        metadata = {
            'dataset_path': dataset_path,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'workflow_type': 'spider_web_directory',
            'total_stages': len(nodes),
            'total_connections': len(edges),
            'description': 'Directory structure visualization as spider web with Dataset Root as central node',
            'visualization_type': 'spider_web'
        }
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': metadata
        }
