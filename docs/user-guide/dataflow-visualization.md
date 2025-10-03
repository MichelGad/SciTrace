# Dataflow Visualization Guide

This guide covers dataflow visualization features, interactive exploration, and network analysis in SciTrace.

## 📊 Visualization Overview

SciTrace provides interactive dataflow visualization to help researchers understand data lineage, dependencies, and relationships in their research projects.

## 🎯 Visualization Features

### Interactive Network Graphs

#### Network Visualization Components
```
┌─────────────────────────────────────────────────────────────┐
│                Dataflow Visualization                       │
├─────────────────────────────────────────────────────────────┤
│  Node Types                                                 │
│  ├── Data Files (CSV, JSON, etc.)                          │
│  ├── Script Files (Python, R, etc.)                        │
│  ├── Output Files (Results, Plots)                          │
│  └── External Dependencies                                  │
├─────────────────────────────────────────────────────────────┤
│  Edge Types                                                 │
│  ├── Data Dependencies                                      │
│  ├── Script Dependencies                                    │
│  ├── Output Relationships                                   │
│  └── Version Dependencies                                   │
├─────────────────────────────────────────────────────────────┤
│  Interactive Features                                       │
│  ├── Zoom and Pan                                           │
│  ├── Node Selection                                         │
│  ├── Edge Highlighting                                      │
│  └── Filtering and Search                                   │
└─────────────────────────────────────────────────────────────┘
```

### Visualization Types

#### 1. Network Graph Visualization
- **Nodes**: Represent files, scripts, and data sources
- **Edges**: Show dependencies and relationships
- **Layout**: Force-directed or hierarchical layouts
- **Interactivity**: Click, drag, zoom, and filter

#### 2. Timeline Visualization
- **Temporal View**: Show data evolution over time
- **Commit History**: Visualize changes and versions
- **Dependency Tracking**: Track how data flows through time

#### 3. Hierarchical Tree View
- **File Structure**: Show directory and file organization
- **Dependency Tree**: Display parent-child relationships
- **Collapsible Nodes**: Expand/collapse for detailed view

## 🔍 Interactive Exploration

### Navigation Controls

#### Zoom and Pan
```javascript
// Zoom controls
- Mouse wheel: Zoom in/out
- Double-click: Zoom to fit
- Ctrl + drag: Pan view
- Reset button: Return to default view
```

#### Node Interaction
```javascript
// Node selection
- Click: Select single node
- Ctrl + click: Multi-select nodes
- Drag: Move nodes
- Right-click: Context menu
```

### Filtering and Search

#### Filter Options
```javascript
// Filter by file type
filterByType(['csv', 'py', 'r'])

// Filter by date range
filterByDateRange(startDate, endDate)

// Filter by file size
filterBySize(minSize, maxSize)

// Filter by dependencies
filterByDependencies(hasDependencies)
```

#### Search Functionality
```javascript
// Search by filename
searchFiles('analysis')

// Search by content
searchContent('statistical')

// Search by metadata
searchMetadata('author', 'John Doe')
```

## 📈 Data Analysis Features

### Dependency Analysis

#### Dependency Detection
```python
# Python script dependencies
import pandas as pd
import numpy as np
from sklearn import model_selection

# R script dependencies
library(ggplot2)
library(dplyr)
require(tidyverse)
```

#### Data Flow Tracking
```python
# Track data flow through scripts
data_flow = {
    'raw_data.csv': ['clean_data.py'],
    'clean_data.py': ['processed_data.csv', 'analysis.py'],
    'analysis.py': ['results.csv', 'plot.png']
}
```

### Version Control Integration

#### Git History Visualization
```bash
# Show file changes over time
git log --oneline --graph --all

# Track specific file evolution
git log --follow -- path/to/file.csv

# Show file differences
git diff HEAD~1 HEAD -- path/to/file.csv
```

#### Commit Analysis
```python
# Analyze commit patterns
commits = {
    'frequency': 'daily',
    'files_changed': 5,
    'lines_added': 100,
    'lines_removed': 10
}
```

## 🎨 Customization Options

### Visual Styling

#### Node Styling
```javascript
// Node appearance
const nodeStyles = {
    dataFiles: {
        shape: 'circle',
        color: '#3498db',
        size: 20
    },
    scriptFiles: {
        shape: 'square',
        color: '#e74c3c',
        size: 25
    },
    outputFiles: {
        shape: 'diamond',
        color: '#27ae60',
        size: 18
    }
}
```

#### Edge Styling
```javascript
// Edge appearance
const edgeStyles = {
    dataDependency: {
        color: '#95a5a6',
        width: 2,
        style: 'solid'
    },
    scriptDependency: {
        color: '#f39c12',
        width: 3,
        style: 'dashed'
    }
}
```

### Layout Options

#### Force-Directed Layout
```javascript
// Force-directed layout options
const forceOptions = {
    nodes: {
        repulsion: 1000,
        gravity: 0.1
    },
    edges: {
        length: 100,
        stiffness: 0.1
    }
}
```

#### Hierarchical Layout
```javascript
// Hierarchical layout options
const hierarchyOptions = {
    direction: 'UD', // Up-Down
    sortMethod: 'directed',
    nodeSpacing: 100,
    levelSeparation: 150
}
```

## 🔧 Advanced Features

### Export and Sharing

#### Export Options
```javascript
// Export visualization
exportAsImage('png', 'dataflow_visualization.png')
exportAsSVG('dataflow_visualization.svg')
exportAsJSON('dataflow_data.json')
```

#### Sharing Features
```javascript
// Share visualization
const shareUrl = generateShareableUrl(visualizationId)
const embedCode = generateEmbedCode(visualizationId)
```

### Integration with External Tools

#### Jupyter Notebook Integration
```python
# Display visualization in Jupyter
from scitrace.visualization import DataflowVisualizer

viz = DataflowVisualizer(project_path)
viz.display_notebook()
```

#### R Markdown Integration
```r
# Display visualization in R Markdown
library(scitrace)
viz <- create_dataflow_viz(project_path)
print(viz)
```

## 📊 Performance Optimization

### Large Dataset Handling

#### Data Sampling
```javascript
// Sample large datasets for performance
const sampleSize = 1000
const sampledData = sampleData(fullDataset, sampleSize)
```

#### Lazy Loading
```javascript
// Load data on demand
const lazyLoader = {
    loadNodes: (nodeIds) => loadNodeData(nodeIds),
    loadEdges: (edgeIds) => loadEdgeData(edgeIds)
}
```

### Rendering Optimization

#### Level of Detail
```javascript
// Adjust detail based on zoom level
const lodLevels = {
    zoomedOut: { nodeCount: 100, edgeCount: 200 },
    normal: { nodeCount: 500, edgeCount: 1000 },
    zoomedIn: { nodeCount: 2000, edgeCount: 5000 }
}
```

## 🛠️ Troubleshooting

### Common Issues

#### Performance Problems
```javascript
// Optimize for large datasets
const optimization = {
    maxNodes: 1000,
    maxEdges: 2000,
    clustering: true,
    levelOfDetail: true
}
```

#### Rendering Issues
```javascript
// Fix rendering problems
const rendering = {
    webgl: true,
    antialias: true,
    pixelRatio: window.devicePixelRatio
}
```

### Browser Compatibility

#### Supported Browsers
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

#### Fallback Options
```javascript
// Fallback for older browsers
if (!supportsWebGL()) {
    useCanvasRenderer()
}
```

## 📋 Visualization Checklist

### Setup Checklist
- [ ] Dataflow data loaded
- [ ] Visualization configured
- [ ] Interactive features enabled
- [ ] Export options configured
- [ ] Performance optimized
- [ ] Browser compatibility tested

### Usage Checklist
- [ ] Navigation controls working
- [ ] Filtering and search functional
- [ ] Export features working
- [ ] Sharing options available
- [ ] Performance acceptable
- [ ] User experience smooth

---

**Need help with dataflow visualization?** Check out the [User Guide](README.md) for general usage, or explore the [Troubleshooting Guide](../troubleshooting/README.md) for visualization issues.
