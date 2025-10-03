# Demo Setup Guide

This guide covers setting up and exploring SciTrace with sample data and demo scenarios.

## 🚀 Quick Demo Setup

### Prerequisites

#### System Requirements
- Python 3.8 or higher
- Git installed
- DataLad installed (optional but recommended)
- 2GB free disk space
- Modern web browser

#### Installation Check
```bash
# Check Python version
python --version

# Check Git installation
git --version

# Check DataLad installation (optional)
datalad --version
```

### Demo Data Installation

#### Automatic Demo Setup
```bash
# Clone SciTrace repository
git clone https://github.com/scitrace/scitrace.git
cd scitrace

# Install dependencies
pip install -r requirements.txt

# Run demo setup script
python setup_demo_datalad.py

# Start SciTrace
python run.py
```

#### Manual Demo Setup
```bash
# Create demo project
python -c "
from scitrace.services import ServiceFactory
from scitrace.models import User, Project

# Create demo user
user = User(username='demo', email='demo@scitrace.org')
user.set_password('demo123')
db.session.add(user)
db.session.commit()

# Create demo project
project = Project(
    name='Environmental Research Demo',
    description='Sample environmental research project',
    research_type='environmental',
    user_id=user.id
)
db.session.add(project)
db.session.commit()
"
```

## 📊 Demo Scenarios

### Scenario 1: Environmental Research

#### Project Overview
- **Research Type**: Environmental
- **Focus**: Water quality analysis
- **Data Sources**: Sensor data, lab measurements
- **Analysis**: Statistical analysis, visualization

#### Demo Data Structure
```
demo_environmental/
├── raw_data/
│   ├── sensor_readings.csv
│   ├── lab_measurements.csv
│   └── metadata.json
├── scripts/
│   ├── data_cleaning.py
│   ├── statistical_analysis.py
│   └── visualization.R
├── results/
│   ├── analysis_results.csv
│   ├── quality_report.pdf
│   └── plots/
│       ├── temperature_trends.png
│       └── quality_distribution.png
└── documentation/
    ├── README.md
    └── analysis_notes.md
```

#### Demo Workflow
1. **Data Collection**: Import sensor and lab data
2. **Data Cleaning**: Process and validate data
3. **Analysis**: Perform statistical analysis
4. **Visualization**: Create charts and plots
5. **Documentation**: Record findings and methods

### Scenario 2: Biomedical Research

#### Project Overview
- **Research Type**: Biomedical
- **Focus**: Clinical trial data analysis
- **Data Sources**: Patient records, lab results
- **Analysis**: Survival analysis, statistical modeling

#### Demo Data Structure
```
demo_biomedical/
├── patient_data/
│   ├── demographics.csv
│   ├── clinical_measures.csv
│   └── outcomes.csv
├── analysis/
│   ├── survival_analysis.R
│   ├── statistical_modeling.py
│   └── risk_assessment.py
├── results/
│   ├── survival_curves.png
│   ├── model_parameters.csv
│   └── risk_scores.csv
└── reports/
    ├── clinical_report.pdf
    └── statistical_summary.md
```

### Scenario 3: Computational Research

#### Project Overview
- **Research Type**: Computational
- **Focus**: Machine learning model development
- **Data Sources**: Training datasets, test data
- **Analysis**: Model training, validation, optimization

#### Demo Data Structure
```
demo_computational/
├── datasets/
│   ├── training_data.csv
│   ├── test_data.csv
│   └── validation_data.csv
├── models/
│   ├── model_training.py
│   ├── hyperparameter_tuning.py
│   └── model_evaluation.py
├── results/
│   ├── model_performance.csv
│   ├── feature_importance.png
│   └── confusion_matrix.png
└── notebooks/
    ├── exploratory_analysis.ipynb
    └── model_development.ipynb
```

## 🎯 Demo Features

### Interactive Exploration

#### Dataflow Visualization
- **Network Graph**: Interactive node-link diagram
- **Timeline View**: Data evolution over time
- **Dependency Tree**: File relationships
- **Filter Options**: Filter by type, date, size

#### Project Management
- **Project Dashboard**: Overview of all projects
- **Task Management**: Create and track tasks
- **Collaboration**: Share projects with team members
- **Version Control**: Track changes and history

### Data Analysis Tools

#### Statistical Analysis
```python
# Example analysis script
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# Load data
data = pd.read_csv('raw_data/sensor_readings.csv')

# Basic statistics
summary = data.describe()
print(summary)

# Correlation analysis
correlation_matrix = data.corr()
print(correlation_matrix)

# Visualization
plt.figure(figsize=(10, 6))
plt.scatter(data['temperature'], data['quality'])
plt.xlabel('Temperature')
plt.ylabel('Quality Score')
plt.title('Temperature vs Quality')
plt.show()
```

#### Data Visualization
```r
# Example R visualization
library(ggplot2)
library(dplyr)

# Load data
data <- read.csv('raw_data/lab_measurements.csv')

# Create visualization
ggplot(data, aes(x = date, y = value, color = parameter)) +
  geom_line() +
  geom_point() +
  facet_wrap(~parameter, scales = "free_y") +
  labs(title = "Laboratory Measurements Over Time",
       x = "Date",
       y = "Value") +
  theme_minimal()
```

## 🔧 Demo Configuration

### Environment Setup

#### Development Environment
```bash
# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///instance/scitrace_demo.db

# Start development server
python run.py
```

#### Production Environment
```bash
# Set production environment
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/scitrace
export SECRET_KEY=your-secret-key

# Start production server
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Demo Data Configuration

#### Sample Data Generation
```python
# Generate sample data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sensor data
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
sensor_data = pd.DataFrame({
    'timestamp': dates,
    'temperature': np.random.normal(20, 5, len(dates)),
    'humidity': np.random.normal(60, 10, len(dates)),
    'pressure': np.random.normal(1013, 10, len(dates))
})

# Save to file
sensor_data.to_csv('demo_data/sensor_readings.csv', index=False)
```

#### DataLad Dataset Creation
```bash
# Create DataLad dataset
datalad create demo_dataset
cd demo_dataset

# Add sample data
datalad add demo_data/

# Create initial commit
git add .
git commit -m "Add demo data"

# Configure dataset
datalad config --local annex.auto-commit false
```

## 📋 Demo Checklist

### Pre-Demo Setup
- [ ] System requirements met
- [ ] Dependencies installed
- [ ] Demo data generated
- [ ] Database initialized
- [ ] User accounts created
- [ ] Sample projects created
- [ ] DataLad datasets configured
- [ ] Git repositories initialized

### Demo Execution
- [ ] Application started
- [ ] Demo scenarios prepared
- [ ] Sample data loaded
- [ ] Features demonstrated
- [ ] User interactions tested
- [ ] Performance verified
- [ ] Error handling tested
- [ ] Documentation reviewed

### Post-Demo Cleanup
- [ ] Demo data archived
- [ ] Temporary files cleaned
- [ ] Database reset
- [ ] Logs reviewed
- [ ] Performance metrics collected
- [ ] User feedback collected
- [ ] Issues documented
- [ ] Improvements identified

## 🆘 Demo Troubleshooting

### Common Issues

#### Data Loading Problems
```bash
# Check data file permissions
ls -la demo_data/

# Verify data format
file demo_data/sensor_readings.csv

# Test data loading
python -c "import pandas as pd; print(pd.read_csv('demo_data/sensor_readings.csv').head())"
```

#### Database Issues
```bash
# Check database connection
python -c "from scitrace import db; print(db.engine.url)"

# Reset database
rm instance/scitrace_demo.db
python -c "from scitrace import db; db.create_all()"
```

#### DataLad Issues
```bash
# Check DataLad installation
datalad --version

# Verify dataset
datalad status

# Fix dataset issues
datalad install --recursive .
```

### Performance Issues

#### Large Dataset Handling
```python
# Optimize for large datasets
import pandas as pd

# Use chunking for large files
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    process_chunk(chunk)
```

#### Memory Optimization
```python
# Optimize memory usage
import gc

# Clear memory after processing
gc.collect()

# Use efficient data types
data = pd.read_csv('file.csv', dtype={'column': 'category'})
```

## 📚 Demo Resources

### Sample Scripts
- **Python Analysis**: `demo_scripts/sample_analysis.py`
- **R Analysis**: `demo_scripts/sample_analysis.R`
- **Data Generation**: `demo_scripts/generate_sample_data.py`

### Sample Data
- **Environmental**: `demo_scripts/sample_data.csv`
- **Biomedical**: `demo_scripts/sample_r_data.csv`
- **Computational**: `demo_scripts/sample_ml_data.csv`

### Documentation
- **User Guide**: `docs/user-guide/README.md`
- **API Reference**: `docs/api/README.md`
- **Troubleshooting**: `docs/troubleshooting/README.md`

---

**Need help with demo setup?** Check out the [Installation Guide](../installation/README.md) for setup instructions, or explore the [Troubleshooting Guide](../troubleshooting/README.md) for common issues.
