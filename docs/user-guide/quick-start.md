# Quick Start Guide

Get up and running with SciTrace in just a few minutes! This guide will walk you through the essential steps to start managing your research data.

## 🚀 5-Minute Setup

### Step 1: Install SciTrace
```bash
git clone https://github.com/MichelGad/SciTrace
cd SciTrace
chmod +x install.sh
./install.sh
```

### Step 2: Start the Application
```bash
source venv/bin/activate
python run.py
```

### Step 3: Access SciTrace
Open your browser and go to: `http://localhost:5001`

### Step 4: Login
- **Username**: `admin`
- **Password**: `admin123`

### Step 5: Load Demo Data
Click the **"Load Demo Projects"** button on the dashboard to explore SciTrace with sample data.

## 🎯 Your First Project

### Create a New Project
1. **Click "Create Project"** from the dashboard
2. **Fill in the details**:
   - **Name**: "My First Research Project"
   - **Description**: "Learning SciTrace with sample data"
   - **Research Type**: Choose from Environmental, Biomedical, Computational, or General
3. **Click "Create Project"**

### Set Up a Dataflow
1. **Navigate to "Dataflows"** in the main menu
2. **Click "Create Dataflow"**
3. **Select your project** from the dropdown
4. **Choose storage location** (default is fine for learning)
5. **Click "Create Dataflow"**

SciTrace will automatically:
- Create a DataLad dataset
- Set up the directory structure
- Generate an interactive visualization

## 🔍 Explore Your Dataflow

### Interactive Visualization
Your dataflow appears as an interactive network diagram:
- **Blue nodes**: Directories
- **Green nodes**: Files
- **Gray nodes**: Untracked files
- **Red nodes**: Deleted files

### Click to Explore
- **Click any node** to view file content or metadata
- **Download files** with the download button
- **View file locations** in your system explorer
- **See file status** (tracked, modified, etc.)

### Add Files
1. **Navigate to your project directory** (shown in the dataflow)
2. **Add some files** (text files, images, data files)
3. **Return to SciTrace** and refresh the dataflow
4. **New files appear** as gray (untracked) nodes

## 💾 Save Your Work

### Commit Changes
1. **Click "Save Files"** in the dataflow interface
2. **Add a commit message**: "Added initial data files"
3. **Click "Commit Changes"**
4. **Watch the visualization update** as files turn green (tracked)

### View Commit History
1. **Click "Git Log"** in the dataflow interface
2. **See your commits** in the interactive timeline
3. **Click on commits** to view changes
4. **Use "Copy Hash"** to reference specific commits

## 🎨 Key Features to Try

### File Management
- **Upload files** through the web interface
- **View file content** directly in the browser
- **Download files** with one click
- **Open file locations** in your system

### Version Control
- **Make changes** to your files
- **Commit changes** with descriptive messages
- **View differences** between versions
- **Restore deleted files** from previous commits

### Project Organization
- **Add collaborators** to your projects
- **Create tasks** with deadlines
- **Track progress** through the dashboard
- **Organize by research type**

## 🔄 Demo Data Exploration

### Load Demo Projects
1. **Click "Load Demo Projects"** on the dashboard
2. **Wait for setup** (creates sample environmental research data)
3. **Explore the demo project**:
   - Environmental water quality research
   - Sample Python and R scripts
   - Realistic data structure
   - Full DataLad integration

### Demo Features
- **Interactive dataflow** with real research data
- **Sample scripts** for data analysis
- **Commit history** showing research progression
- **File restoration** examples

## 🛠️ Next Steps

### Learn More
- **Read the [User Guide](README.md)** for comprehensive documentation
- **Explore [Features](features.md)** for detailed feature descriptions
- **Check [DataLad Integration](datalad-integration.md)** for advanced usage

### Advanced Usage
- **Set up multiple projects** for different research areas
- **Invite collaborators** to work together
- **Use custom directory structures** for your research
- **Integrate with existing DataLad datasets**

### Get Help
- **Check [Troubleshooting](../troubleshooting/README.md)** for common issues
- **Review [FAQ](../troubleshooting/faq.md)** for answers to common questions
- **Create an issue** on GitHub for bugs or feature requests

## 🎉 Congratulations!

You've successfully:
- ✅ Installed SciTrace
- ✅ Created your first project
- ✅ Set up a dataflow with DataLad integration
- ✅ Explored the interactive visualization
- ✅ Committed changes and viewed history
- ✅ Loaded and explored demo data

**You're now ready to use SciTrace for your research data management!**

---

**Ready for more?** Check out the [Features Overview](features.md) to learn about all the powerful features SciTrace offers.
