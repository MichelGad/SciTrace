# Git Operations Guide

This guide covers Git operations, version control workflows, and commit management in SciTrace.

## 🔄 Git Integration Overview

SciTrace integrates with Git to provide version control for research data and code. This enables tracking changes, collaboration, and reproducibility in research workflows.

## 🏗️ Git Workflow Architecture

### Git Integration Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Git Integration                         │
├─────────────────────────────────────────────────────────────┤
│  Repository Management                                      │
│  ├── Repository Initialization                              │
│  ├── Remote Configuration                                   │
│  ├── Branch Management                                       │
│  └── Repository Cloning                                     │
├─────────────────────────────────────────────────────────────┤
│  Commit Operations                                          │
│  ├── File Staging                                           │
│  ├── Commit Creation                                        │
│  ├── Commit History                                         │
│  └── Commit Reverting                                       │
├─────────────────────────────────────────────────────────────┤
│  Collaboration Features                                      │
│  ├── Branch Operations                                       │
│  ├── Merge Operations                                       │
│  ├── Conflict Resolution                                    │
│  └── Pull/Push Operations                                   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Repository Management

### Repository Initialization

#### Creating New Repositories
```bash
# Initialize Git repository in dataflow directory
cd /path/to/dataflow
git init

# Configure Git user (if not already set globally)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create initial commit
git add .
git commit -m "Initial commit: Add project files"
```

#### Repository Configuration
```bash
# Set up Git configuration for SciTrace
git config core.autocrlf false
git config core.filemode false
git config pull.rebase false

# Configure line ending handling
git config core.eol lf

# Set up Git hooks (optional)
git config core.hooksPath .git/hooks
```

### Remote Repository Setup

#### Adding Remote Repositories
```bash
# Add remote repository
git remote add origin https://github.com/username/repository.git

# Verify remote configuration
git remote -v

# Set default branch
git branch -M main
git push -u origin main
```

#### Multiple Remote Setup
```bash
# Add multiple remotes for collaboration
git remote add upstream https://github.com/original/repository.git
git remote add fork https://github.com/yourusername/repository.git

# List all remotes
git remote -v
```

## 📝 Commit Operations

### Basic Commit Workflow

#### Staging Files
```bash
# Stage specific files
git add file1.txt file2.py

# Stage all changes
git add .

# Stage specific file types
git add *.py *.r

# Interactive staging
git add -i
```

#### Creating Commits
```bash
# Create commit with message
git commit -m "Add data analysis script"

# Create commit with detailed message
git commit -m "Add data analysis script

- Implement statistical analysis
- Add visualization functions
- Update documentation"

# Amend last commit
git commit --amend -m "Updated commit message"
```

### Commit Best Practices

#### Commit Message Format
```
<type>(<scope>): <description>

<body>

<footer>
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

#### Example Commit Messages
```bash
# Feature commit
git commit -m "feat(analysis): add statistical analysis module

- Implement t-test functionality
- Add correlation analysis
- Create visualization functions"

# Bug fix commit
git commit -m "fix(data): correct data loading error

- Fix CSV parsing issue
- Handle missing values properly
- Update error handling"

# Documentation commit
git commit -m "docs(readme): update installation instructions

- Add Python 3.8+ requirement
- Include dependency installation
- Add troubleshooting section"
```

## 🌿 Branch Management

### Branch Operations

#### Creating Branches
```bash
# Create and switch to new branch
git checkout -b feature/new-analysis

# Create branch from specific commit
git checkout -b hotfix/data-correction abc1234

# Create branch without switching
git branch feature/visualization
```

#### Branch Switching
```bash
# Switch to existing branch
git checkout main
git checkout feature/new-analysis

# Switch to previous branch
git checkout -

# Switch to remote branch
git checkout -b feature/remote-branch origin/feature/remote-branch
```

#### Branch Management
```bash
# List all branches
git branch -a

# List remote branches
git branch -r

# Delete local branch
git branch -d feature/completed

# Delete remote branch
git push origin --delete feature/completed

# Rename branch
git branch -m old-name new-name
```

### Branch Workflow

#### Feature Branch Workflow
```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/data-processing

# Work on feature
git add .
git commit -m "feat: implement data processing pipeline"

# Push feature branch
git push origin feature/data-processing

# Create pull request (via GitHub/GitLab interface)
# After approval, merge to main
git checkout main
git pull origin main
git merge feature/data-processing
git push origin main
```

#### Hotfix Workflow
```bash
# Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug

# Fix the issue
git add .
git commit -m "fix: resolve critical data corruption issue"

# Push hotfix
git push origin hotfix/critical-bug

# Merge to main
git checkout main
git merge hotfix/critical-bug
git push origin main

# Merge to development branch
git checkout develop
git merge hotfix/critical-bug
git push origin develop
```

## 🔄 Collaboration Features

### Pull and Push Operations

#### Pulling Changes
```bash
# Pull latest changes from remote
git pull origin main

# Pull specific branch
git pull origin feature/new-analysis

# Pull with rebase
git pull --rebase origin main

# Fetch without merging
git fetch origin
git merge origin/main
```

#### Pushing Changes
```bash
# Push to remote repository
git push origin main

# Push new branch
git push -u origin feature/new-branch

# Force push (use with caution)
git push --force origin main

# Push all branches
git push --all origin
```

### Merge Operations

#### Basic Merging
```bash
# Merge feature branch into main
git checkout main
git merge feature/new-analysis

# Merge with no-fast-forward
git merge --no-ff feature/new-analysis

# Merge with squash
git merge --squash feature/new-analysis
git commit -m "Merge feature: new analysis functionality"
```

#### Conflict Resolution
```bash
# Check for conflicts
git status

# Resolve conflicts in files
# Edit conflicted files manually
# Remove conflict markers

# Stage resolved files
git add resolved-file.txt

# Complete merge
git commit -m "Resolve merge conflicts in data processing"
```

## 📊 Commit History and Analysis

### Viewing Commit History

#### Basic History Commands
```bash
# View commit history
git log

# One-line format
git log --oneline

# Graph format
git log --graph --oneline --all

# Specific file history
git log -- path/to/file.txt

# Author-specific history
git log --author="John Doe"

# Date range history
git log --since="2023-01-01" --until="2023-12-31"
```

#### Advanced History Analysis
```bash
# Show file changes
git log --stat

# Show actual changes
git log -p

# Show commit differences
git diff HEAD~1 HEAD

# Show branch differences
git diff main..feature/new-analysis
```

### Commit Information

#### Detailed Commit View
```bash
# Show specific commit
git show abc1234

# Show commit with files
git show --stat abc1234

# Show commit with changes
git show -p abc1234
```

#### Commit Search
```bash
# Search commit messages
git log --grep="analysis"

# Search in changes
git log -S "function_name"

# Search by file content
git log -G "pattern"
```

## 🔧 Advanced Git Operations

### Git Hooks

#### Pre-commit Hook
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Run code quality checks
python -m flake8 *.py
if [ $? -ne 0 ]; then
    echo "Code quality checks failed"
    exit 1
fi

# Run tests
python -m pytest tests/
if [ $? -ne 0 ]; then
    echo "Tests failed"
    exit 1
fi
```

#### Post-commit Hook
```bash
#!/bin/sh
# .git/hooks/post-commit

# Update documentation
python scripts/update_docs.py

# Notify team
curl -X POST -H "Content-Type: application/json" \
     -d '{"message":"New commit pushed"}' \
     https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### Git Aliases

#### Useful Aliases
```bash
# Add aliases to ~/.gitconfig
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'
```

#### Custom Aliases
```bash
# Create custom aliases
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.undo "reset HEAD~1"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.wip "commit -am 'WIP'"
git config --global alias.unwip "reset HEAD~1"
```

## 🛠️ Troubleshooting Git Issues

### Common Problems

#### Undoing Changes
```bash
# Undo last commit (keep changes)
git reset HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Undo specific commit
git revert abc1234

# Undo file changes
git checkout -- file.txt
```

#### Repository Issues
```bash
# Fix corrupted repository
git fsck
git gc --prune=now

# Recover lost commits
git reflog
git checkout abc1234

# Clean untracked files
git clean -fd
```

### Git Configuration Issues

#### Line Ending Problems
```bash
# Fix line ending issues
git config core.autocrlf false
git rm --cached -r .
git reset --hard

# Normalize line endings
git add --renormalize .
git commit -m "Normalize line endings"
```

#### Authentication Issues
```bash
# Update remote URL with credentials
git remote set-url origin https://username:token@github.com/user/repo.git

# Use SSH instead of HTTPS
git remote set-url origin git@github.com:user/repo.git
```

## 📋 Git Workflow Checklist

### Development Workflow
- [ ] Repository initialized
- [ ] Remote configured
- [ ] Branch created for feature
- [ ] Changes committed with descriptive messages
- [ ] Branch pushed to remote
- [ ] Pull request created
- [ ] Code reviewed
- [ ] Changes merged to main
- [ ] Feature branch deleted

### Collaboration Workflow
- [ ] Latest changes pulled
- [ ] Conflicts resolved
- [ ] Changes tested
- [ ] Commits squashed if needed
- [ ] Changes pushed
- [ ] Team notified

### Maintenance Workflow
- [ ] Repository cleaned up
- [ ] Unused branches deleted
- [ ] History optimized
- [ ] Backups created
- [ ] Documentation updated

---

**Need help with Git operations?** Check out the [Troubleshooting Guide](../troubleshooting/README.md) for common Git issues, or explore the [Developer Guide](../developer/README.md) for advanced Git integration.
