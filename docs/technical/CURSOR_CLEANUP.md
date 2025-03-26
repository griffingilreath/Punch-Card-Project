# Cursor Folder Cleanup Guide

This document provides instructions for organizing the files within the `Cursor` folder to maintain a cleaner workspace.

## Current State

Currently, the project files are scattered across several directories:
- `Cursor/Punch Card Project/` - Main project files
- `LOOK HERE Punch Card Project 0.5.3/Punch Card Project/` - Version 0.5.3 reference
- `PunchCardProject-Clean/` - New clean organization

## Organization Plan

### Step 1: Create a Main Project Folder

```bash
# Create a new main project folder
mkdir -p ~/Documents/Coding/PunchCardProject

# Copy the clean project structure
cp -R ~/Documents/Coding/PunchCardProject-Clean/* ~/Documents/Coding/PunchCardProject/
cp -R ~/Documents/Coding/PunchCardProject-Clean/.git ~/Documents/Coding/PunchCardProject/
```

### Step 2: Archive Old Project Versions

```bash
# Create an archive directory
mkdir -p ~/Documents/Coding/PunchCardProject/archives

# Archive the old project files (without copying unnecessary files)
cp -R ~/Documents/Coding/Cursor/"Punch Card Project"/versions ~/Documents/Coding/PunchCardProject/archives/
cp -R ~/Documents/Coding/"LOOK HERE Punch Card Project 0.5.3" ~/Documents/Coding/PunchCardProject/archives/version-0.5.3
```

### Step 3: Move Working Files

```bash
# Remove any temporary or unnecessary files
find ~/Documents/Coding/PunchCardProject -name "__pycache__" -type d -exec rm -rf {} +
find ~/Documents/Coding/PunchCardProject -name "*.pyc" -type f -delete
find ~/Documents/Coding/PunchCardProject -name ".DS_Store" -type f -delete
```

### Step 4: Update Working Directory in IDE

Configure your IDE (Cursor) to use the new project folder at:
```
~/Documents/Coding/PunchCardProject
```

### Step 5: Update Git Remote (if applicable)

If you plan to push to GitHub:
```bash
cd ~/Documents/Coding/PunchCardProject
git remote set-url origin https://github.com/yourusername/Punch-Card-Project.git
```

## Directory Structure After Cleanup

```
~/Documents/Coding/
├── PunchCardProject/             # Main project directory (active development)
│   ├── src/                      # Source code
│   ├── resources/                # Resources
│   ├── tests/                    # Tests
│   ├── docs/                     # Documentation
│   ├── run.py                    # Runner script
│   ├── branch_helper.py          # Branch management
│   └── archives/                 # Historical archives
│       ├── versions/             # Version archives
│       └── version-0.5.3/        # Version 0.5.3 reference
├── Cursor/                       # Cursor editor files (read-only reference)
│   └── Punch Card Project/       # Old project structure (for reference only)
└── LOOK HERE Punch Card Project 0.5.3/  # Original reference (for reference only)
```

## Rules for Future Development

1. All new development should happen in the `~/Documents/Coding/PunchCardProject` directory
2. Use the `testing` branch for active development
3. Use the branch helper script for branch management
4. Only refer to archived versions when absolutely necessary
5. Update this guide if the organization changes

## Clean Up Old Directories (Optional)

After confirming everything works in the new structure:

```bash
# Backup old directories first
zip -r ~/Documents/Coding/punch_card_old_backup.zip ~/Documents/Coding/Cursor/"Punch Card Project" ~/Documents/Coding/"LOOK HERE Punch Card Project 0.5.3"

# Then optionally remove them
# rm -rf ~/Documents/Coding/Cursor/"Punch Card Project"
# rm -rf ~/Documents/Coding/"LOOK HERE Punch Card Project 0.5.3"
```

**Note**: The removal step is optional and should only be done after verifying everything is working properly in the new location. 