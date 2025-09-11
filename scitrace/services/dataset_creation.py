"""
Dataset creation services for SciTrace

Handles DataLad dataset creation and initialization.
"""

import os
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from ..utils.datalad_utils import DataLadUtils, DataLadCommandError
from ..exceptions import DatasetError, ValidationError
from .base_service import BaseService


class DatasetCreationService(BaseService):
    """Service for DataLad dataset creation operations."""
    
    def __init__(self, db=None):
        super().__init__(db)
        self.datalad_utils = DataLadUtils()
        home_dir = os.path.expanduser("~")
        self.base_path = os.environ.get('DATALAD_BASE_PATH', os.path.join(home_dir, 'scitrace_demo_datasets'))
        os.makedirs(self.base_path, exist_ok=True)
    
    def create_dataset(self, dataset_path: str, name: str = None, research_type: str = "general") -> dict:
        """
        Create a new DataLad dataset at the specified path.
        
        Args:
            dataset_path: Path where to create the dataset
            name: Optional name for the dataset
            research_type: Type of research (affects dataset structure)
        
        Returns:
            Dict containing creation result information
        
        Raises:
            DatasetError: If dataset creation fails
            ValidationError: If parameters are invalid
        """
        if not dataset_path:
            raise ValidationError("Dataset path is required")
        
        if os.path.exists(dataset_path):
            raise DatasetError(f"Dataset already exists at {dataset_path}", dataset_path=dataset_path)
        
        try:
            # Create DataLad dataset using the utility
            result = self.datalad_utils.create_dataset(dataset_path, research_type, name)
            
            # Create empty directory structure
            self._create_empty_structure(dataset_path, research_type, name or os.path.basename(dataset_path))
            
            return result
            
        except DataLadCommandError as e:
            raise DatasetError(f"Failed to create DataLad dataset: {e.message}", dataset_path=dataset_path)
        except Exception as e:
            raise DatasetError(f"Unexpected error creating dataset: {str(e)}", dataset_path=dataset_path)
    
    def _create_empty_structure(self, dataset_path: str, research_type: str, project_name: str):
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
        
        # Create basic README
        self._create_basic_readme(dataset_path, project_name, research_type)
        
        # Create .gitignore file
        self._create_gitignore(dataset_path)
        
        # Add empty directories to DataLad
        try:
            self.datalad_utils.save_changes(
                dataset_path, 
                f'Create empty structure for {project_name} ({research_type})'
            )
            print(f"     🔄 Saved empty structure to DataLad: {os.path.basename(dataset_path)}")
        except DataLadCommandError as e:
            print(f"     ⚠️ Warning: Could not save to DataLad: {e.message}")
    
    def _create_basic_readme(self, dataset_path: str, project_name: str, research_type: str):
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
        # Only create README if it doesn't exist as a symlink (Git annex managed)
        if not os.path.islink(readme_path):
            with open(readme_path, 'w') as f:
                f.write(readme_content)
        else:
            print(f"     ⚠️ Skipping README.md creation (already exists as symlink)")
    
    def _create_gitignore(self, dataset_path: str):
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
    
    def create_dataset_with_content(self, dataset_path: str, name: str, research_type: str = "general") -> dict:
        """
        Create a DataLad dataset with sample content.
        
        Args:
            dataset_path: Path where to create the dataset
            name: Name for the dataset
            research_type: Type of research
        
        Returns:
            Dict containing creation result information
        """
        # First create the basic dataset
        result = self.create_dataset(dataset_path, name, research_type)
        
        # Add research-specific content
        self._add_research_content(dataset_path, research_type, name)
        
        return result
    
    def _add_research_content(self, dataset_path: str, research_type: str, project_name: str):
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
                    content = self._create_python_script(filename, research_type, project_name)
                elif filename.endswith('.R'):
                    content = self._create_r_script(filename, research_type, project_name)
                elif filename.endswith('.csv'):
                    content = self._create_csv_data(filename, research_type)
                elif filename.endswith('.json'):
                    content = json.dumps(self._create_json_data(filename, research_type), indent=2)
                elif filename.endswith('.md'):
                    content = self._create_markdown_file(filename, research_type, project_name)
                else:
                    # For other files, create placeholder content
                    content = f"# {filename}\n\nThis is a sample {filename} file for {research_type} research.\n\nGenerated by SciTrace for project: {project_name}\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                # Make Python scripts executable
                if filename.endswith('.py'):
                    os.chmod(file_path, 0o755)
                
                print(f"     ✅ Created: {dir_name}/{filename}")
        
        # Add all files to DataLad
        try:
            self.datalad_utils.save_changes(
                dataset_path, 
                f'Add research content for {project_name} ({research_type})'
            )
            print(f"     🔄 Saved to DataLad: {os.path.basename(dataset_path)}")
        except DataLadCommandError as e:
            print(f"     ⚠️ Warning: Could not save to DataLad: {e.message}")
    
    def _create_python_script(self, filename: str, research_type: str, project_name: str) -> str:
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
    
    def _create_r_script(self, filename: str, research_type: str, project_name: str) -> str:
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
    
    def _create_csv_data(self, filename: str, research_type: str) -> str:
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
    
    def _create_json_data(self, filename: str, research_type: str) -> dict:
        """Create sample JSON data based on research type."""
        import numpy as np
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
    
    def _create_markdown_file(self, filename: str, research_type: str, project_name: str) -> str:
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
